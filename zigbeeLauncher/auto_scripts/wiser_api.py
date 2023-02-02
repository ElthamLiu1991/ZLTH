import asyncio
import random
import threading
import time
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Optional, Any

import rapidjson as json
from dacite import from_dict

from zigbeeLauncher.dongle import Tasks
from zigbeeLauncher.logging import autoLogger as logger

import paho.mqtt.client as mqtt

from zigbeeLauncher.util import get_ip_address


@dataclass
class Network:
    Code: int
    Sequence: int
    Type: str
    Channel: int
    State: str
    Permit: int
    PanId: str
    ExPanId: str
    RecommendedChannel: int


@dataclass
class ApplicationBase:
    id: int
    Endpoint: int
    Name: str


@dataclass
class DeviceBase:
    id: int
    Type: str
    State: int
    MacAddress: str
    Manufacturer: str
    Model: str
    FirmwareVersion: str
    HardwareVersion: str
    Application: list[ApplicationBase]


@dataclass
class Device:
    Code: Optional[int]
    Sequence: Optional[int]
    Type: str
    State: int
    MacAddress: str
    Manufacturer: str
    Model: str
    FirmwareVersion: str
    HardwareVersion: str
    Application: list[ApplicationBase]


@dataclass
class Devices:
    Code: int
    Sequence: int
    Device: list[DeviceBase]


class WiserAPI:
    class RSP(Enum):
        DEVICES = 1
        DEVICE = 2
        DEVICE_ATTRIBUTE = 3
        NETWORK = 4

    class DATA(Enum):
        NETWORK_PERMIT = 1

    def __init__(self):
        self.sequence = 0
        self.client = None
        self.permit = None
        self.channel = None
        self.device_id = None
        self.device = None
        self.devices = None
        self.rsp = None

    def _next_sequence(self):
        if self.sequence > 255:
            self.sequence = 1
        else:
            self.sequence += 1

    @staticmethod
    def _wait_response(rsp):

        async def wait(obj):
            while obj.rsp != rsp:
                logger.debug("waiting")
                await asyncio.sleep(1)

        async def checking(obj):
            try:
                await asyncio.wait_for(wait(obj), timeout=5)
            except asyncio.TimeoutError:
                logger.debug("timeout")
                return False
            else:
                return True

        def function(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                timeout = 5
                obj = args[0]
                obj.rsp = None
                func(*args, **kwargs)
                task = Tasks()
                return task.add(checking(obj)).result()
            return wrapper
        return function

    def set_client(self, client):
        self.client = client

    def build_network(self):
        topic = "ZLTH/v2/CMD/WDC/Network/Initiate"
        payload = {
            "Sequence": self.sequence,
            "Type": "Zigbee"
        }
        logger.info("build a Zigbee network")
        self.client.send(topic, payload)
        self._next_sequence()

    @_wait_response(RSP.NETWORK)
    def get_network(self):
        topic = "ZLTH/v2/REQ/WDC/Network"
        payload = {
            "Sequence": self.sequence,
            "Type": "Zigbee"
        }
        logger.info("Get current Zigbee network")
        self.client.send(topic, payload)
        self._next_sequence()

    @_wait_response(DATA.NETWORK_PERMIT)
    def permit_join(self, timeout):
        topic = "ZLTH/v2/CMD/WDC/Network/PermitJoining"
        payload = {
            "Sequence": self.sequence,
            "Type": "Zigbee",
            "Permit": 1 if timeout > 0 else 0,
            "Timeout": timeout
        }
        logger.info("Open permit join:%d", timeout)
        self.client.send(topic, payload)
        self._next_sequence()

    @_wait_response(RSP.DEVICES)
    def get_devices(self):
        topic = "ZLTH/v2/REQ/WDC/Device"
        payload = self.sequence
        logger.info("Get join devices list")
        self.client.send(topic, payload)
        self._next_sequence()
        # wait response

    def is_joined(self, mac):
        if self.get_devices() and self.devices:
            for device in self.devices:
                if device.MacAddress == mac:
                    return True
        return False

    @_wait_response(RSP.DEVICE)
    def get_device(self, id):
        self.device = None
        topic = "ZLTH/v2/REQ/WDC/Device/{}".format(id)
        payload = self.sequence
        logger.info("Get join devices list")
        self.client.send(topic, payload)
        self._next_sequence()

    def reset_device(self, id):
        topic = "ZLTH/v2/CMD/WDC/Device/{}/Reset".format(id)
        payload = self.sequence
        logger.info("reset device %d", id)
        self.client.send(topic, payload)
        self._next_sequence()

    def is_permit(self):
        # get network
        return self.permit

    def on_device_add(self, id, device):
        """
        notify there is a new device join
        :param id: device id
        :param device: Device object
        :return:
        """
        pass

    def on_device_del(self, id):
        pass

    def on_device_data(self, id, attribute, value):
        pass

    def on_network_data(self, attribute, value):
        if attribute == 'Permit':
            self.permit = value
        elif attribute == 'Channel':
            self.channel = value
        self.rsp = self.DATA.NETWORK_PERMIT

    def on_application_data(self, id, attribute, payload):
        pass

    def on_devices_rsp(self, devices):
        self.devices = devices
        self.rsp = self.RSP.DEVICES

    def on_device_rsp(self, id, device):
        self.device_id = id
        self.device = device
        self.rsp = self.RSP.DEVICE

    def on_device_attribute_rsp(self, id, attribute, value):
        self.rsp = self.RSP.DEVICE_ATTRIBUTE
        pass

    def on_network_rsp(self, network):
        logger.debug("receive network response")
        logger.debug(network)
        if network:
            self.channel = network.Channel
            self.permit = network.Permit
            logger.debug(f"channel:{self.channel}")
            logger.debug(f"permit:{self.permit}")
        self.rsp = self.RSP.NETWORK


class WiserMQTT:
    def __init__(self, ip, wiser_api=None):
        self.ip = ip
        self.wiser_api = wiser_api if wiser_api else WiserAPI()
        self.wiser_api.set_client(self)
        self.client = None
        self.connected = False
        self._topic = ""
        self._payload = ""
        self._need_resend = False
        self._stop = False
        self.start()

    def stop(self):
        self.client.disconnect()
        self._stop = True

    def send(self, topic, payload):
        self._topic = topic
        self._payload = json.dumps(payload)
        logger.debug(f"send: {self._topic}, {self._payload}")
        self.client.publish(self._topic, self._payload, qos=2)

    def resend(self):
        if self._need_resend:
            logger.debug(f"resend:{self._topic}, {self._payload}")
            self.client.publish(self._topic, self._payload, qos=2)
            self._need_resend = False

    def start(self) -> None:
        def on_connect(client, userdata, flags, rc):
            logger.info("Wiser Standard Hub connected")
            client.subscribe("WDC/+/ADD/Device/+", qos=2)
            client.subscribe("WDC/+/DATA/Device/#", qos=2)
            client.subscribe("WDC/+/DEL/Device/+", qos=2)
            client.subscribe("WDC/+/DATA/Network/#", qos=2)
            client.subscribe("WDC/+/RSP/ZLTH/#", qos=2)
            self.connected = True
            self.resend()

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                logger.error("Wiser hub disconnected unexpected:%s", rc)
                time.sleep(1)
                self._need_resend = True
                connect()
                return
                # self.run()
            self.connected = False
            logger.info("Wiser hub disconnected")

        def on_message(client, userdata, msg):
            topic = msg.topic
            logger.info("Revice Wiser MQTT message: %s", topic)
            try:
                payload = json.loads(msg.payload.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error("MQTT: failed to decode message:{}".format(repr(e)))
                return

            items = msg.topic.split("/")
            type = items[2]

            if type == "ADD":
                # device joined notification
                # WDC/v2/ADD/Device/1
                id = items[-1]
                if items[3] == "Device":
                    device = from_dict(data_class=Device, data=payload)
                    self.wiser_api.on_device_add(id, device)
                else:
                    # TODO: application
                    pass
            elif type == "DEL":
                # device leave notification
                # WDC/v2/DEL/Device/1
                id = items[-1]
                if items[3] == "Device":
                    self.wiser_api.on_device_del(id)
                else:
                    # TODO: application
                    pass
            elif type == "DATA":
                # device status change notification
                # WDC/v2/DATA/Device/1/State
                # WDC/v2/DATA/Application/1/On
                # WDC/v2/DATA/Network/Channel
                if items[3] == "Device":
                    id = items[-2]
                    attribute = items[-1]
                    self.wiser_api.on_device_data(id, attribute, payload)
                elif items[3] == "Network":
                    attribute = items[-1]
                    self.wiser_api.on_network_data(attribute, payload)
                else:
                    id = items[-2]
                    attribute = items[-1]
                    self.wiser_api.on_application_data(id, attribute, payload)
            elif type == "RSP":
                # retrieve device list response
                # WDC/v2/RSP/ZLTH/Device
                # WDC/v2/RSP/ZLTH/Device/1
                # WDC/v2/RSP/ZLTH/Device/1/State
                # WDC/v2/RSP/ZLTH/Application/1
                # WDC/v2/RSP/ZLTH/Application/1/On
                # WDC/v2/RSP/ZLTH/Network
                name = items[4]
                id = items[5] if len(items) > 5 else None
                attribute = items[6] if len(items) > 6 else None
                if name == "Device":
                    if attribute:
                        self.wiser_api.on_device_attribute_rsp(id, attribute, payload)
                    elif id:
                        device = from_dict(data_class=Device, data=payload)
                        self.wiser_api.on_device_rsp(device)
                    else:
                        devices = from_dict(data_class=Devices, data=payload).Device
                        self.wiser_api.on_devices_rsp(devices)
                elif name == "Network":
                    network = from_dict(data_class=Network, data=payload)
                    self.wiser_api.on_network_rsp(network)
                else:
                    # TODO: application response
                    pass

        def on_subscribe(client, userdata, mid, granted_qos):
            pass

        def connect():
            try:
                logger.info("Connecting to Wiser Standard Hub %s", self.ip)
                self.client.connect(self.ip, 1883, 10)
            except Exception as e:
                logger.error("MQTT connect failed, try again")
                time.sleep(5)
                connect()

        self.client = mqtt.Client("ZLTH-" + get_ip_address() + "-" + str(int(time.time())))
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_subscribe = on_subscribe
        self.client.on_disconnect = on_disconnect
        connect()
        self.client.loop_start()
