import json
import logging
import threading
import time

import paho.mqtt.client as mqtt
import socket

from . import router, mqtt_version
from . import Launcher_API
from zigbeeLauncher.util import pack_payload, get_ip_address
from zigbeeLauncher.logging import mqttLogger as logger


class WiserMQTT(threading.Thread):
    def __init__(self, broker, port, role=None, connected_cb=None):
        threading.Thread.__init__(self)
        self.broker = broker
        self.port = port
        self.ip = get_ip_address()
        self.role = role
        self.connected_cb = connected_cb
        self.will_payload = pack_payload({'connected': False})
        self.will_topic = mqtt_version + "/" + self.ip + "/simulator/update"

    def run(self):
        def on_connect(client, userdata, flags, rc):
            logger.info("MQTT connected")
            role = self.role
            if role == 'edge':
                # 订阅消息
                # outside
                client.subscribe(mqtt_version + "/+/simulator/error", qos=2)
                client.subscribe(mqtt_version + "/+/simulator/devices/+/error", qos=2)
                client.subscribe(mqtt_version + "/" + self.ip + "/simulator/info", qos=2)
                client.subscribe(mqtt_version + "/+/simulator/devices/+/info", qos=2)
                client.subscribe(mqtt_version + "/+/simulator/update", qos=2)
                client.subscribe(mqtt_version + "/+/simulator/devices/+/update", qos=2)

                # client.subscribe(mqtt_version + "/+/synchronized", qos=2)

                client.subscribe(mqtt_version + "/+/simulator", qos=2)
                client.subscribe(mqtt_version + "/+/simulator/devices/+", qos=2)
                client.subscribe(mqtt_version + "/" + self.ip + "/simulator/command", qos=2)
                client.subscribe(mqtt_version + "/" + self.ip + "/simulator/devices/+/command", qos=2)
            else:
                # 订阅消息
                # local
                client.subscribe(mqtt_version + "/simulator/synchronized", qos=2)
                client.subscribe(mqtt_version + "/simulator/error", qos=2)
                client.subscribe(mqtt_version + "/simulator/devices/+/error", qos=2)
                client.subscribe(mqtt_version + "/simulator/info", qos=2)
                client.subscribe(mqtt_version + "/simulator/devices/+/info", qos=2)
                client.subscribe(mqtt_version + "/simulator/update", qos=2)
                client.subscribe(mqtt_version + "/+/simulator/update", qos=2)   # subscribe from outside
                client.subscribe(mqtt_version + "/simulator/devices/+/update", qos=2)
                client.subscribe(mqtt_version + "/simulator/command", qos=2)
                client.subscribe(mqtt_version + "/simulator/devices/+/command", qos=2)
            if self.broker == '127.0.0.1' and self.connected_cb:
                self.connected_cb(client)
            if role == 'edge':
                logger.info("get dongle list from %s", self.broker)
                Launcher_API.request_synchronized(client, pack_payload({'ip': self.ip}))

        def on_message(client, userdata, msg):
            logger.info("Receive MQTT message, topic: %s", msg.topic)
            items = msg.topic.split("/")
            version = items[0]
            ip = items[1]
            if ip == 'simulator':
                # local message
                topic = msg.topic[msg.topic.find("/", 1):]
                router.call(topic, ip=self.ip, payload=msg.payload.decode('utf-8'))
                if 'info' in msg.topic or 'update' in msg.topic or 'error' in msg.topic:
                    # transfer to another edges also
                    topic = mqtt_version + '/' + self.ip + topic
                    logger.info("public to outside:%s", topic)
                    client.publish(topic, msg.payload, qos=2)
            else:
                if 'update' in msg.topic or 'error' in msg.topic:
                    if ip == self.ip:
                        logger.info('don not %s message from own', msg.topic)
                        return
                # message from another edge, include /command, /update, /info, /error
                topic = msg.topic[msg.topic.find("/", 10):]
                # add to dongle mqtt queue
                router.call(topic, ip=ip, payload=msg.payload.decode('utf-8'))

        def on_subscribe(client, userdata, mid, granted_qos):
            pass

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                logger.error("%s:Unexpected disconnection %s", self.broker, rc)
            client.disconnect()
            # remove brokers

        try:
            logger.info("Try to connect MQTT broker: %s %d" % (self.broker, self.port))
            client = mqtt.Client("ZLTH-" + self.role + "-" + self.ip)
            if self.role == 'edge':
                client.will_set(self.will_topic, payload=self.will_payload, qos=2)
                pass
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_subscribe = on_subscribe
            client.on_disconnect = on_disconnect
            client.connect(self.broker, self.port, 10)
            client.loop_forever()
        except Exception as e:
            logger.exception("MQTT connect failed, try again")
            time.sleep(5)
            self.run()

