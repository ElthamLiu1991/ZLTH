import json
import logging
import threading
import time

import paho.mqtt.client as mqtt

from . import set_value, get_value, mqtt_version, client_ip, router
from . import WiserZigbeeLauncher
from . import WiserZigbeeSimulator
from .WiserZigbeeGlobal import pack_payload
from ..logging import mqttLogger as logger
from .WiserZigbeeDongle import init


class WiserMQTT(threading.Thread):
    def __init__(self, broker, port, clientId, role=None):
        threading.Thread.__init__(self)
        self.broker = broker
        self.port = port
        self.clientId = clientId
        self.role = role
        self.will_payload = pack_payload({'connected': False})
        self.will_topic = mqtt_version + "/" + self.clientId + "/simulator/update"

    def run(self):
        try:
            logger.info("Try to connect MQTT broker: %s %d" % (self.broker, self.port))
            client = mqtt.Client("ZLTH-" + self.role + "-" + self.clientId)
            if self.role == 'edge':
                client.will_set(topic=self.will_topic, payload=self.will_payload)
                pass
            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.on_subscribe = self.on_subscribe
            client.on_disconnect = self.on_disconnect
            client.user_data_set((self.broker, self.role))

            client.connect(self.broker, self.port, 60)
            set_value(self.role, client)
            client.loop_forever()
        except TimeoutError:
            logger.warning("MQTT connect timeout, try again")
            time.sleep(5)
            self.run()
        except ConnectionRefusedError:
            logger.warning("MQTT connect refused, try again")
            time.sleep(5)
            self.run()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logger.info("MQTT connected")
        brokers = get_value('brokers')
        if brokers:
            brokers[userdata[0]] = client
        else:
            brokers = {userdata[0]: client}
        set_value('brokers', brokers)
        print('brokers:', brokers)
        role = userdata[1]
        if role == 'edge':
            # 订阅消息
            # outside
            client.subscribe(mqtt_version + "/+/simulator/devices/+/error", qos=2)
            client.subscribe(mqtt_version + "/" + client_ip + "/simulator/info", qos=2)
            client.subscribe(mqtt_version + "/+/simulator/devices/+/info", qos=2)
            client.subscribe(mqtt_version + "/+/simulator/update", qos=2)
            client.subscribe(mqtt_version + "/+/simulator/devices/+/update", qos=2)

            client.subscribe(mqtt_version + "/+/synchronized", qos=2)

            client.subscribe(mqtt_version + "/+/simulator", qos=2)
            client.subscribe(mqtt_version + "/+/simulator/devices/+", qos=2)
            client.subscribe(mqtt_version + "/+/simulator/command", qos=2)
            client.subscribe(mqtt_version + "/+/simulator/devices/+/command", qos=2)

            if userdata[0] != client_ip:
                logger.info("get dongle list from %s", userdata[0])
                WiserZigbeeLauncher.request_synchronized(client, client_ip)
        else:
            # 订阅消息
            # local
            client.subscribe(mqtt_version + "/simulator/error", qos=2)
            client.subscribe(mqtt_version + "/simulator/devices/+/error", qos=2)
            client.subscribe(mqtt_version + "/simulator/info", qos=2)
            client.subscribe(mqtt_version + "/simulator/devices/+/info", qos=2)
            client.subscribe(mqtt_version + "/simulator/update", qos=2)
            client.subscribe(mqtt_version + "/simulator/devices/+/update", qos=2)
            client.subscribe(mqtt_version + "/simulator/command", qos=2)
            client.subscribe(mqtt_version + "/simulator/devices/+/command", qos=2)
            data = pack_payload(WiserZigbeeSimulator.pack_simulator_info())
            topic = mqtt_version + "/simulator/info"
            logger.info("public:%s", topic)
            client.publish(topic, data)

        if not get_value("dongle"):
            # 初始化serial handler
            init(WiserZigbeeSimulator.dongle_info_callback,
                 WiserZigbeeSimulator.dongle_update_callback,
                 WiserZigbeeSimulator.dongle_error_callback)

    @staticmethod
    def on_message(client, userdata, msg):
        logger.info("Receive MQTT message, topic: %s, payload:%s", msg.topic, msg.payload.decode('utf-8'))
        items = msg.topic.split("/")
        version = items[0]
        ip = items[1]
        if ip == 'simulator':
            # local message
            topic = msg.topic[msg.topic.find("/", 1):]
            router.call(topic, client, client_ip, msg.payload.decode('utf-8'))
            if 'info' in msg.topic or 'update' in msg.topic or 'error' in msg.topic:
                # transfer to another edges also
                brokers = get_value('brokers')
                for broker in brokers:
                    if broker == '127.0.0.1' or broker == client_ip:
                        continue
                    else:
                        topic = mqtt_version + '/' + client_ip + topic
                        logger.info("public:%s", topic)
                        brokers[broker].publish(topic, msg.payload, qos=2)
                pass
        else:
            if 'command' in msg.topic and ip != client_ip:
                logger.info('don not handle command request from others')
                return
            if 'synchronized' in msg.topic and ip == client_ip:
                logger.info('don not handle synchronized request from own')
                return
            if 'update' in msg.topic or 'error' in msg.topic:
                if ip == client_ip:
                    logger.info('don not %s message from own', msg.topic)
                    return
            # message from another edge, include /command, /update, /info, /error
            topic = msg.topic[msg.topic.find("/", 10):]
            router.call(topic, client, ip, msg.payload.decode('utf-8'))

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        pass

    @staticmethod
    def on_disconnect(client, userdata, rc):
        set_value("connected", False)
        if rc != 0:
            logger.error("%s:Unexpected disconnection %s", userdata, rc)
        client.disconnect()
        # remove brokers
        brokers = get_value('brokers')
        if brokers and userdata[0] in brokers:
            del brokers[userdata[0]]
            set_value('brokers', brokers)
