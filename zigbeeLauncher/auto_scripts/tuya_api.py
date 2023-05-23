import asyncio
from dataclasses import dataclass, asdict
from functools import wraps
from typing import Optional, Any

import time
import hmac
from hashlib import sha256

from dacite import from_dict

from zigbeeLauncher.auto_scripts.script import Http
from zigbeeLauncher.tasks import Tasks
from zigbeeLauncher.logging import autoLogger as logger


@dataclass
class Response:
    success: bool
    t: int
    tid: str
    result: Optional[Any]
    code: Optional[int]
    msg: Optional[str]


@dataclass
class Token:
    access_token: str
    expire_time: int
    refresh_token: str
    uid: str


@dataclass
class TokenResponse:
    success: bool
    t: int
    tid: str
    result: Token


@dataclass
class DPStatus:
    code: str
    value: str


@dataclass
class Device:
    active_time: int
    biz_type: int
    category: str
    create_time: int
    icon: str
    id: str
    ip: str
    lat: str
    local_key: str
    lon: str
    model: str
    name: str
    online: bool
    owner_id: str
    product_id: str
    product_name: str
    status: list[DPStatus]
    sub: bool
    time_zone: str
    uid: str
    update_time: int
    uuid: str


@dataclass
class DeviceResponse:
    success: bool
    t: int
    tid: str
    result: Device


@dataclass
class SubDevice:
    active_time: int
    category: str
    icon: str
    id: str
    name: str
    node_id: str
    online: bool
    owner_id: str
    product_id: str
    update_time: int


@dataclass
class SubDeviceResponse:
    success: bool
    t: int
    tid: str
    result: list[SubDevice]


class TUYAAPI(Http):
    client_id = "fytdc8v4txurm79sskp3"
    # client_id = "fytdc8v4txurm79sskp2"
    secret = "dwny8qy3s7epqqawcjqngqpe75mmmcsq"
    schema = "sewiserdemo"
    sign_method = "HMAC-SHA256"
    uid = "ay1600225458332csTDL"
    counter = 3

    def __init__(self, vid):
        Http.__init__(self,
                      url="https://openapi.tuyacn.com")
        self.gateway = vid
        self.sign = None
        self.timestamp = None
        self.token = None
        self.token = self._get_token()

    def _calculate_sign(self):
        self.timestamp = str(int(time.time() * 1000))
        plaintext = self.client_id + self.timestamp
        self.sign = hmac.new(self.secret.encode('utf-8'), plaintext.encode('utf-8'),
                             digestmod=sha256).digest().hex().upper()
        self.headers = {
            'client_id': self.client_id,
            'sign': self.sign,
            't': self.timestamp,
            'sign_method': self.sign_method
        }

    def _calculate_sign_with_token(self):
        self.timestamp = str(int(time.time() * 1000))
        plaintext = self.client_id + self.token.access_token + self.timestamp
        self.sign = hmac.new(self.secret.encode('utf-8'), plaintext.encode('utf-8'),
                             digestmod=sha256).digest().hex().upper()
        self.headers = {
            'client_id': self.client_id,
            'sign': self.sign,
            't': self.timestamp,
            'sign_method': self.sign_method
        }
        if self.token:
            self.headers.update({'access_token': self.token.access_token})

    @staticmethod
    def _decode(data):
        def send(func, *args, **kwargs):
            func(*args, **kwargs)
            obj = args[0]
            task = Tasks()
            try:
                task.add(obj.send()).result()
            except Exception as e:
                logger.error("TUYA request error: {}".format(repr(e)))
                if TUYAAPI.counter == 0:
                    TUYAAPI.counter = 3
                    return None
                else:
                    TUYAAPI.counter -= 1
                    return send(func, *args, **kwargs)
            logger.info(f"TUYA response:{obj.response}")
            if obj.response.get('success'):
                TUYAAPI.counter = 3
                return from_dict(data_class=data, data=obj.response).result
            else:
                if obj.response.get('msg') == 'token invalid':
                    logger.info('refresh token')
                    obj.token = obj.refresh_token()
                    return send(func, *args, **kwargs)
                else:
                    logger.error('other error')
                    return None

        def function(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return send(func, *args, **kwargs)
            return wrapper
        return function

    @_decode(TokenResponse)
    def _get_token(self):
        print("get token")
        if not self.token:
            self.method = 'GET'
            self.path = '/v1.0/token'
            self.params = {"grant_type": 1}
            self._calculate_sign()

    @_decode(TokenResponse)
    def refresh_token(self):
        self.method = "GET"
        self.path = '/v1.0/token/' + self.token.refresh_token
        self.params = None
        self._calculate_sign()

    @_decode(DeviceResponse)
    def get_device_info(self, vid):
        self.method = "GET"
        self.path = '/v1.0/devices/{}'.format(vid)
        self.params = None
        self._calculate_sign_with_token()

    def is_online(self, vid=None):
        info = self.get_device_info(vid if vid else self.gateway)
        if info:
            return info.online
        return None

    def is_permit(self, permit):
        info = self.get_device_info(self.gateway)
        if info:
            for item in info.status:
                if item.code == 'permit_join':
                    if item.value == "true" and permit:
                        return True
                    elif item.value == 'false' and not permit:
                        return True
                    else:
                        return False
        return False

    def get_channel(self):
        info = self.get_device_info(self.gateway)
        if info:
            for item in info.status:
                if item.code == 'zigbee_channel':
                    return int(item.value)
        return None

    @_decode(SubDeviceResponse)
    def get_sub_devices(self):
        self.method = "GET"
        self.path = '/v1.0/devices/{}/sub-devices'.format(self.gateway)
        self.params = None
        self._calculate_sign_with_token()

    def is_register(self, mac):
        devices = self.get_sub_devices()
        if devices:
            for device in devices:
                if device.node_id == mac:
                    return True
            return False

    @_decode(Response)
    def delete_device(self, vid):
        self.method = "DELETE"
        self.path = '/v1.0/devices/{}'.format(vid)
        self.params = None
        self.body = None
        self._calculate_sign_with_token()

    @_decode(Response)
    def permit_join(self, duration):
        self.method = 'PUT'
        self.path = '/v1.0/devices/{}/enabled-sub-discovery'.format(self.gateway)
        self.params = {
            'duration': duration
        }
        self.body = None
        self._calculate_sign_with_token()

    @_decode(Response)
    def request(self, vid, status: DPStatus):
        self.method = 'POST'
        self.path = '/v1.0/devices/{}/commands'.format(vid)
        self.params = None
        self.body = {
            "commands": [
                asdict(status)
            ]
        }
        self._calculate_sign_with_token()
