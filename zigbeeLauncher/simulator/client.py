import abc
import json
import time
from dataclasses import asdict

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes

from zigbeeLauncher.data_model import DeviceInfo, SimulatorInfo, Message, ErrorMessage
from zigbeeLauncher.util import pack_payload, get_ip_address, Global
from zigbeeLauncher.logging import mqttLogger as logger
from zigbeeLauncher.simulator.handler import topic
from zigbeeLauncher.wait_response import add_response

version = 'v1.0'
Global.set(Global.MQTT_VERSION, version)


class MQTTClient:
    def __init__(self, broker, port, name, connection_cb=None, will_topic=None, will_payload=None, ip=""):
        self.broker = broker
        self.port = port
        self.name = name
        self.connection_cb = connection_cb
        self.will_topic = will_topic
        self.will_payload = will_payload
        self.ip = ip

        self._client = None
        self._stop = False
        self._connected = False
        self._topic = None
        self._payload = None

        self._start()

    def _start(self):

        self._client = mqtt.Client(self.name, protocol=mqtt.MQTTv5)
        if self.will_topic and self.will_payload:
            props = mqtt.Properties(PacketTypes.PUBLISH)
            props.UserProperty = ('ip', self.ip)
            self._client.will_set(self.will_topic, payload=json.dumps(self.will_payload), qos=1, properties=props)
        self._client.reconnect_delay_set(min_delay=1, max_delay=10)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe
        self._client.on_disconnect = self._on_disconnect

        self._connecting()
        self._client.user_data_set(self)
        self._client.loop_start()

    def stop(self):
        logger.info(f"stop connection: {self.broker}")
        if self._client and self._connected:
            self._client.disconnect()
            self._client.loop_stop()
            del self._client

    def _connecting(self):
        try:
            logger.info(f"Connecting to broker:{self.broker}:{self.port}")
            self._client.connect(self.broker, self.port, 10)
        except Exception as e:
            logger.error("MQTT connect failed, try again")
            self.connection_cb(False)
            time.sleep(5)
            self._connecting()

    @staticmethod
    @abc.abstractmethod
    def _on_connect(client, userdata, flags, rc, properties):
        """
        user on_connection handler
        :return: None
        """
        pass

    @staticmethod
    def _on_disconnect(client, userdata, rc, properties):
        """
        on_disconnect handler
        :return: None
        """
        userdata._connected = False
        if rc != 0:
            logger.warn(f"Unexpected disconnection with {userdata.broker}, rc:{rc}")
        if userdata.connection_cb:
            userdata.connection_cb(userdata._connected)
        logger.info(f"Disconnected with {userdata.broker}")

    @staticmethod
    def _on_subscribe(client, userdata, mid, granted_qos, properties):
        logger.info("subscribe callback")
        pass

    @staticmethod
    @abc.abstractmethod
    def _on_message(client, userdata, msg):
        """
        user on_message handler
        :param client:
        :param userdata:
        :param msg:
        :return:
        """
        pass

    def _send(self, topic, payload):
        if not topic or not payload:
            return
        self._topic = topic
        self._payload = payload
        if self._client and self._connected:
            props = mqtt.Properties(PacketTypes.PUBLISH)
            props.UserProperty = ('ip', self.ip)
            info = self._client.publish(
                topic=self._topic,
                payload=json.dumps(self._payload),
                qos=1,
                properties=props)
            if info.rc == mqtt.MQTT_ERR_SUCCESS:
                self._topic = None
                self._payload = None
            else:
                logger.warning(f'send {topic} failed')


class ZLTHClient(MQTTClient):
    ip = get_ip_address()

    topic_broadcast_simulator_info = f'{version}/+/simulator/info'
    topic_broadcast_device_info = f'{version}/+/simulator/devices/+/info'
    topic_broadcast_simulator_update = f'{version}/+/simulator/update'
    topic_broadcast_device_update = f'{version}/+/simulator/devices/+/update'
    topic_broadcast_simulator_connected = f'{version}/+/simulator/connected'

    topic_sync_simulator = f'{version}/{ip}/simulator/sync'
    topic_sync_device = f'{version}/{ip}/simulator/devices/+/synced'
    topic_synced_simulator = f'{version}/{ip}/simulator/synced'
    topic_synced_device = f'{version}/{ip}/simulator/devices/+/synced'
    topic_received_simulator = f'{version}/{ip}/simulator/received'

    topic_simulator_command = f'{version}/{ip}/simulator/command'
    topic_device_command = f'{version}/{ip}/simulator/devices/+/command'

    topic_broadcast_simulator_error = f'{version}/{ip}/simulator/error'

    def __init__(self, broker, name, connection_cb=None):
        MQTTClient.__init__(self,
                            broker=broker,
                            port=1883,
                            name=name,
                            connection_cb=connection_cb,
                            will_topic=f'{version}/{self.ip}/simulator/update',
                            will_payload=pack_payload({'connected': False}),
                            ip=self.ip)
    @staticmethod
    def _on_connect(client, userdata, flags, rc, properties):
        userdata._connected = True
        if userdata.connection_cb:
            userdata.connection_cb(userdata._connected)

        # subscribe topics

        client.subscribe(ZLTHClient.topic_broadcast_simulator_info, qos=2)
        client.subscribe(ZLTHClient.topic_broadcast_device_info, qos=2)
        client.subscribe(ZLTHClient.topic_broadcast_simulator_update, qos=2)
        client.subscribe(ZLTHClient.topic_broadcast_device_update, qos=2)
        client.subscribe(ZLTHClient.topic_broadcast_simulator_error, qos=2)
        client.subscribe(ZLTHClient.topic_broadcast_simulator_connected, qos=2)

        client.subscribe(ZLTHClient.topic_sync_simulator, qos=2)
        client.subscribe(ZLTHClient.topic_sync_device, qos=2)
        client.subscribe(ZLTHClient.topic_synced_simulator, qos=2)
        client.subscribe(ZLTHClient.topic_synced_device, qos=2)
        client.subscribe(ZLTHClient.topic_received_simulator, qos=2)

        client.subscribe(ZLTHClient.topic_simulator_command, qos=2)
        client.subscribe(ZLTHClient.topic_device_command, qos=2)

        # broadcast connected notification
        # self._send(self.topic_broadcast_simulator_connected, pack_payload(None))
        userdata.send_connected()

    @staticmethod
    def _on_message(client, userdata, msg):
        # try:
        logger.info("receive MQTT data")
        logger.info(f'topic:{msg.topic}')
        logger.info(f'payload:{msg.payload.decode()}')
        path = msg.topic[len(version):]
        payload = msg.payload.decode('utf-8')
        try:
            sender = msg.properties.UserProperty[0][1]
        except Exception as e:
            sender = get_ip_address()
        topic.run(path, payload, sender)

        # except Exception as e:
        #     userdata.send_error(e.error)

    def send_connected(self):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{self.ip}/simulator/connected'
        payload = pack_payload()
        self._send(topic, payload)

    def send_simulator_sync(self, ip):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{ip}/simulator/sync'
        payload = pack_payload({'ip': self.ip})
        self._send(topic, payload)
        pass

    def send_device_sync(self, ip, mac):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{ip}/simulator/devices/{mac}/sync'
        payload = pack_payload({'ip': self.ip})
        self._send(topic, payload)

    def send_simulator_synced(self, ip, info: SimulatorInfo):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{ip}/simulator/synced'
        # remove simulator attr
        info = asdict(info)
        del info['simulator']
        for item in info['devices']:
            del item['device']
        payload = pack_payload(info)
        self._send(topic, payload)

    def send_device_synced(self, ip, mac, info:DeviceInfo):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return

        topic = f'{version}/{ip}/simulator/devices/{mac}/synced'
        info = asdict(info)
        del info['device']
        payload = pack_payload(info)
        self._send(topic, payload)

    def send_simulator_received(self, ip, info: SimulatorInfo):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{ip}/simulator/received'
        # remove simulator attr
        info = asdict(info)
        del info['simulator']
        for item in info['devices']:
            del item['device']
        payload = pack_payload(info)
        self._send(topic, payload)

    def send_simulator_info(self, info:SimulatorInfo):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{self.ip}/simulator/info'
        info = asdict(info)
        del info['simulator']
        payload = pack_payload(info)
        self._send(topic, payload)

    def send_device_info(self, mac, info: DeviceInfo):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{self.ip}/simulator/devices/{mac}/info'
        info = asdict(info)
        del info['device']
        payload = pack_payload(info)
        self._send(topic, payload)

    def send_simulator_update(self, data):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{self.ip}/simulator/update'
        payload = pack_payload(data)
        self._send(topic, payload)

    def send_device_update(self, mac, data):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{self.ip}/simulator/devices/{mac}/update'
        payload = pack_payload(data)
        self._send(topic, payload)

    def send_error(self, sender, error: ErrorMessage):
        """
        send error notification to sender
        :param sender: sender ip address
        :param error: ErrorMessage object
        :return:
        """
        if sender == self.ip:
            add_response(error.uuid, error)
        else:
            if not self._connected:
                logger.warning(f'MQTT client not connect')
                return
            topic = f'{version}/{sender}/simulator/error'
            payload = asdict(error)
            self._send(topic, payload)

    def send_simulator_command(self, ip, command: Message):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{ip}/simulator/command'
        # payload = pack_payload(asdict(command))
        payload = asdict(command)
        self._send(topic, payload)

    def send_device_command(self, ip, mac, command):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/{ip}/simulator/devices/{mac}/command'
        payload = asdict(command)
        self._send(topic, payload)

    def forward(self, topic, payload):
        if not self._connected:
            logger.warning(f'MQTT client not connect')
            return
        topic = f'{version}/web{topic}'
        self._send(topic, payload)
