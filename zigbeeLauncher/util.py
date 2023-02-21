import os
from dataclasses import asdict

import rapidjson as json
import socket
import time
import uuid
from functools import wraps

from zigbeeLauncher.data_model import Message
from zigbeeLauncher.logging import utilLogger as logger
from zigbeeLauncher.wait_response import wait_response

mqtt_error_code = {
    1000: "device {} not exist",
    2000: 'unsupported command: {}',
    3000: 'json validation failed: {}',
    4000: 'missing key:{}',
    9000: 'internal error: {}'
}


def payload_validate(data):
    json.Validator('{"required":["timestamp", "uuid", "data"]}')(data)


def get_version():
    try:
        with open(os.path.join(os.path.abspath('./version'), 'version.txt')) as f:
            version = f.read()
        return version
    except Exception as e:
        return '0.0.0'


# 获取IP地址
def get_ip_address():
    ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
        if not ip:
            ip = '127.0.0.1'
        # print("simulator ip:", ip)
        return ip


# 获取MAC地址
def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def pack_payload(data={}):
    return {
        "uuid": str(uuid.uuid1()),
        "timestamp": int(round(time.time() * 1000)),
        "data": data
    }


# def pack_payload(data):
#     return Message(
#         uuid=str(uuid.uuid1()),
#         timestamp=int(round(time.time() * 1000)),
#         data=data if data is not None else {}
#     )


class Global:
    SIMULATOR = "simulator"
    DONGLES = "dongles"
    MQTT_VERSION = 'v1.0'

    @classmethod
    def set(cls, key, value):
        if not isinstance(key, str):
            key = str(key)
        logger.info(f'set global attribute: {key}, {value}')
        setattr(cls, key, value)
        pass

    @classmethod
    def get(cls, key):
        if not isinstance(key, str):
            key = str(key)
        try:
            return getattr(cls, key)
        except Exception as e:
            return None