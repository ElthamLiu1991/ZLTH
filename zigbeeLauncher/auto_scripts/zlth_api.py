import json
import asyncio
from dataclasses import dataclass, asdict
from functools import wraps
from typing import Optional, Any

from dacite import from_dict

from zigbeeLauncher.auto_scripts.script import Http, wait_and_retry
from zigbeeLauncher.dongle import Tasks
from zigbeeLauncher.logging import autoLogger as logger


@dataclass
class Response:
    uuid: str
    timestamp: int
    code: int
    message: str
    data: object


@dataclass
class Simulator:
    connected: bool
    version: str
    label: str
    name: str
    ip: str
    mac: str
    devices: list[str]


@dataclass
class SimulatorsResponse:
    uuid: str
    timestamp: int
    code: int
    message: str
    data: list[Simulator]


@dataclass
class Device_base:
    state: int
    label: str
    connected: bool
    name: str
    configured: bool
    hwversion: str
    mac: str
    ip: str
    swversion: str


@dataclass
class DeviceResponse:
    uuid: str
    timestamp: int
    code: int
    message: str
    data: Device_base


@dataclass
class DevicesResponse:
    uuid: str
    timestamp: int
    code: int
    message: str
    data: list[Device_base]


@dataclass
class ZigbeeBase:
    extended_pan_id: int
    device_type: str
    pan_id: int
    channel: int
    node_id: int
    mac: str


@dataclass
class ZigbeeResponse:
    uuid: str
    timestamp: int
    code: int
    message: str
    data: ZigbeeBase


@dataclass
class ZigbeesResponse:
    uuid: str
    timestamp: int
    code: int
    message: str
    data: list[ZigbeeBase]


@dataclass
class AttributeQuery:
    endpoint: int
    cluster: int
    server: int
    attribute: int
    manufacturer: int = 0
    manufacturer_code: int = 0


@dataclass
class Attribute:
    endpoint: int
    cluster: int
    server: bool
    attribute: int
    type: str
    value: Any
    manufacturer: bool
    manufacturer_code: Optional[int]


@dataclass
class AttributeResponse:
    uuid: str
    timestamp: int
    code: int
    message: str
    data: Attribute


class ZLTHAPI(Http):

    def __init__(self):
        Http.__init__(self, url='http://localhost:5000',
                      headers={'Content-Type': 'application/json'})
        self.simulators = self._get_simulators()
        self.dongles = self._get_devices()

    @staticmethod
    def _decode(data):

        def send(func, *args, **kwargs):
            func(*args, **kwargs)
            obj = args[0]
            task = Tasks()
            try:
                task.add(obj.send()).result()
            except Exception as e:
                logger.error("ZLTH request error: {}".format(repr(e)))
                return None
            logger.debug(f"ZLTH response:{obj.response}")
            response = from_dict(data_class=data, data=obj.response).data
            return response if response else True

        def function(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return send(func, *args, **kwargs)

            return wrapper

        return function

    @_decode(SimulatorsResponse)
    def _get_simulators(self):
        self.method = 'GET'
        self.path = '/api/2/simulators'
        self.params = None
        self.body = None

    @_decode(DevicesResponse)
    def _get_devices(self, params=None):
        self.method = 'GET'
        self.path = '/api/2/devices'
        self.params = params
        self.body = None

    def refresh(self):
        self.dongles = self._get_devices()

    @_decode(DeviceResponse)
    def get_device(self, mac):
        self.method = 'GET'
        self.path = '/api/2/devices/{}'.format(mac)
        self.params = None
        self.body = None

    @_decode(Response)
    def join(self, mac, channels, pan_id=None, extended_pan_id=None):
        self.method = 'PUT'
        self.path = '/api/2/zigbees/{}'.format(mac)
        self.params = None
        self.body = None
        if pan_id:
            self.body = {'join': {
                'channels': channels,
                'pan_id': pan_id,
                'extended_pan_id': extended_pan_id
            }}
        else:
            self.body = {
                'join': {
                    'channels': channels
                }
            }

    @wait_and_retry()
    def is_joined(self, mac):
        device = self.get_device(mac)
        if device and device.state == 6:
            return True
        else:
            return False

    @_decode(Response)
    def leave(self, mac):
        self.method = 'PUT'
        self.path = '/api/2/zigbees/{}'.format(mac)
        self.params = None
        self.body = {'leave': {}}

    @_decode(Response)
    def reset(self, mac):
        self.method = 'PUT'
        self.path = f'/api/2/devices/{mac}'
        self.params = None
        self.body = {'reset': {}}

    @wait_and_retry()
    def is_reset(self, mac):
        device = self.get_device(mac)
        if device.state == 1:
            return True
        else:
            self.reset(mac)
            return False

    @_decode(Response)
    def write(self, mac, attribute: Attribute):
        """
        update attribute value
        :param mac: dongle mac address
        :param attribute: Attribute object
        :return:
        """
        self.method = 'PUT'
        self.path = '/api/2/zigbees/{}'.format(mac)
        self.params = None
        self.body = {'attribute': asdict(attribute)}

    @_decode(Response)
    def data_request(self, mac):
        self.method = 'PUT'
        self.path = '/api/2/zigbees/{}'.format(mac)
        self.params = None
        self.body = {'data_request': {}}

    @_decode(ZigbeesResponse)
    def get_zigbees(self):
        self.method = 'GET'
        self.path = '/api/2/zigbees'
        self.params = None
        self.body = None

    @_decode(ZigbeeResponse)
    def get_zigbee(self, mac):
        self.method = 'GET'
        self.path = '/api/2/zigbees/{}'.format(mac)
        self.params = None
        self.body = None

    @_decode(AttributeResponse)
    def get_attribute(self, mac, attribute: AttributeQuery):
        self.method = 'GET'
        self.path = '/api/2/zigbees/{}/attributes'.format(mac)
        self.params = asdict(attribute)
        self.body = None

    def has_device(self, mac):
        for dongle in self.dongles:
            if dongle.mac == mac:
                return dongle
        return None

    def has_simulator(self, ip):
        for simulator in self.simulators:
            if simulator.ip == ip:
                return simulator
        return None
