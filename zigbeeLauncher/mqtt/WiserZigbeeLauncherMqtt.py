import threading
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

        if self.role == "simulator":
            self.will_topic = mqtt_version + "/" + self.clientId + "/simulator/update"
            self.will_payload = pack_payload({"connected": False})

    def run(self):
        try:
            logger.info("Try to connect MQTT broker: %s %d" % (self.broker, self.port))
            client = mqtt.Client("wiser-zigbee-" + self.role + "-" + self.clientId)
            if self.role == 'simulator':
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
            logger.fatal("MQTT connect timeout, please try again later")

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logger.info("MQTT connected")
        brokers = get_value('brokers')
        if brokers:
            brokers[userdata[0]] = client
        else:
            brokers = {userdata[0]: client}
        set_value('brokers', brokers)
        # 订阅消息
        client.subscribe(mqtt_version + "/+/simulator/devices/+/error", qos=2)
        client.subscribe(mqtt_version + "/+/simulator/info", qos=2)
        client.subscribe(mqtt_version + "/+/simulator/devices/+/info", qos=2)
        client.subscribe(mqtt_version + "/+/simulator/update", qos=2)
        client.subscribe(mqtt_version + "/+/simulator/devices/+/update", qos=2)

        client.subscribe(mqtt_version + "/synchronization", qos=2)
        client.subscribe(mqtt_version + "/" + client_ip + "/simulator", qos=2)
        client.subscribe(mqtt_version + "/" + client_ip + "/simulator/devices/+", qos=2)
        client.subscribe(mqtt_version + "/" + client_ip + "/simulator/command", qos=2)
        client.subscribe(mqtt_version + "/" + client_ip + "/simulator/devices/+/command", qos=2)

        if not get_value("dongle"):
            # 初始化serial handler
            init(WiserZigbeeSimulator.dongle_info_callback,
                 WiserZigbeeSimulator.dongle_update_callback,
                 WiserZigbeeSimulator.dongle_error_callback)
            # request info
            WiserZigbeeLauncher.request_synchronization(client)

    @staticmethod
    def on_message(client, userdata, msg):
        # get version, ip, and other
        if "synchronization" in msg.topic:
            # sync simulator and dongle info
            logger.info("receive message:topic:%s", msg.topic)
            WiserZigbeeSimulator.synchronization(client)
        else:
            items = msg.topic.split("/")
            version = items[0]
            ip = items[1]
            topic = msg.topic[msg.topic.find("/", 10):]
            logger.info("Receive message, topic: %s/%s%s, payload:%s", version, ip, topic, msg.payload.decode('utf-8'))
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
