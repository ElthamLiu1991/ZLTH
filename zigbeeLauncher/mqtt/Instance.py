import json
import logging
import threading
import time

import paho.mqtt.client as mqtt

brokers = {}
from . import router
from . import Launcher_API
from zigbeeLauncher.util import pack_payload, get_value, get_ip_address
from zigbeeLauncher.dongle import init
from zigbeeLauncher.logging import mqttLogger as logger


class WiserMQTT(threading.Thread):
    def __init__(self, broker, port, role=None, connected_cb=None):
        threading.Thread.__init__(self)
        self.broker = broker
        self.port = port
        if self.broker == '127.0.0.1':
            self.clientId = get_value('client_ip')
        else:
            self.clientId = self.broker
        self.role = role
        self.connected_cb = connected_cb
        self.will_payload = pack_payload({'connected': False})
        self.will_topic = get_value('mqtt_version') + "/" + self.clientId + "/simulator/update"

    def run(self):
        def on_connect(client, userdata, flags, rc):
            client_ip = get_value('client_ip')
            if self.clientId == client_ip:
                if self.connected_cb:
                    self.connected_cb(client)

            mqtt_version = get_value('mqtt_version')
            logger.info("MQTT connected")
            brokers[self.clientId] = client
            role = self.role
            if role == 'edge':
                # 订阅消息
                # outside
                client.subscribe(mqtt_version + "/+/simulator/error", qos=2)
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

                if self.clientId != client_ip:
                    logger.info("get dongle list from %s", self.clientId)
                    Launcher_API.request_synchronized(client, client_ip)
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

            if not get_value("dongle"):
                # 初始化serial handler
                # init(WiserZigbeeSimulator.dongle_info_callback,
                #      WiserZigbeeSimulator.dongle_update_callback,
                #      WiserZigbeeSimulator.dongle_error_callback)
                # thread = threading.Thread(target=serial_management)
                # thread.start()
                init()

        def on_message(client, userdata, msg):
            client_ip = get_value('client_ip')
            mqtt_version = get_value('mqtt_version')
            logger.info("Receive MQTT message, topic: %s", msg.topic)
            items = msg.topic.split("/")
            version = items[0]
            ip = items[1]
            if ip == 'simulator':
                # local message
                topic = msg.topic[msg.topic.find("/", 1):]
                router.call(topic, client, client_ip, msg.payload.decode('utf-8'))
                if 'info' in msg.topic or 'update' in msg.topic or 'error' in msg.topic:
                    # transfer to another edges also
                    for broker in brokers:
                        if broker == client_ip:
                            continue
                        else:
                            topic = mqtt_version + '/' + client_ip + topic
                            logger.info("public to outside:%s", topic)
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
                # add to dongle mqtt queue
                router.call(topic, client, ip, msg.payload.decode('utf-8'))

        def on_subscribe(client, userdata, mid, granted_qos):
            pass

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                logger.error("%s:Unexpected disconnection %s", self.clientId, rc)
            client.disconnect()
            # remove brokers
            if brokers and self.clientId in brokers:
                del brokers[self.clientId]

        try:
            logger.info("Try to connect MQTT broker: %s %d" % (self.broker, self.port))
            client = mqtt.Client("ZLTH-" + self.role + "-" + self.clientId)
            if self.role == 'edge':
                client.will_set(topic=self.will_topic, payload=self.will_payload)
                pass
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_subscribe = on_subscribe
            client.on_disconnect = on_disconnect
            client.connect(self.broker, self.port, 60)
            client.loop_forever()
        except TimeoutError:
            logger.warning("MQTT connect timeout, try again")
            time.sleep(5)
            self.run()
        except ConnectionRefusedError:
            logger.warning("MQTT connect refused, try again")
            time.sleep(5)
            self.run()
