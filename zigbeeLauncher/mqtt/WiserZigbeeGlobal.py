import json
import socket
import time
import traceback
import uuid
from datetime import datetime
from functools import wraps

import rapidjson

from ..logging import mqttLogger as logger


def _init():
    global _global_dict
    _global_dict = {}


def set_value(name, value):
    _global_dict[name] = value


def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue


# 获取IP地址
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
        return ip


# 获取MAC地址
def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def pack_payload(data):
    timestamp = int(round(time.time() * 1000))
    uid = uuid.uuid1()
    payload = {
        "timestamp": timestamp,
        "uuid": str(uid),
        "data": data
    }
    return json.dumps(payload)


class Router(object):

    def __init__(self):
        self.url_map = {}

    def route(self, url):
        def wrapper(func):
            self.url_map[url] = func

        return wrapper

    def call(self, url, *args, **kwargs):
        func = self.url_map.get(url)
        para = ""
        if not func:
            for k in self.url_map:
                if k.find("+") != -1:
                    k_list = k.split("/")
                    url_list = url.split("/")
                    if len(k_list) == len(url_list):
                        match = True
                        item = ""
                        for k_item, url_item in zip(k_list, url_list):
                            if k_item == "+":
                                item = url_item
                            else:
                                if k_item != url_item:
                                    match = False
                                    break
                        if match:
                            para = item
                            func = self.url_map[k]
                            break
                        continue
            if not para:
                raise ValueError('No url function: %s', url)
        if para:
            args = args + (para,)
        logger.info("call %s", func.__name__)
        return func(*args, **kwargs)


class Response(object):

    def __init__(self):
        self.url_map = {}

    def cmd(self, url):
        def wrapper(func):
            self.url_map[url] = func

        return wrapper

    def call(self, url, *args, **kwargs):
        func = self.url_map.get(url)
        if not func:
            raise ValueError('No response function: %s', url)
        return func(*args, **kwargs)


def except_handle(error_handle):
    # msg用于自定义函数的提示信息
    def except_execute(func):
        @wraps(func)
        def execept_print(*args, **kwargs):
            try:
                if "device" in kwargs:
                    device = kwargs["device"]
                    timestamp = kwargs["timestamp"]
                    uuid = kwargs["uuid"]
                else:
                    device = None
                    payload = rapidjson.loads(args[2])
                    timestamp = payload["timestamp"]
                    uuid = payload["uuid"]

                return func(*args, **kwargs)
            except rapidjson.JSONDecodeError as e:
                error_handle(device,
                             {
                                 "code": 500,
                                 "description": str(e)
                             }
                             )
            except rapidjson.ValidationError as e:
                error_handle(device,
                             {
                                 "code": 501,
                                 "description": str(e)
                             }
                             )
            except KeyError as e:
                error_handle(device,
                             {
                                 "code": 502,
                                 "description": "mandatory key missing: " + str(e)
                             }
                             )
            except Exception as e:
                if str(e) == "device not exist":
                    error_handle(device,
                                 {
                                     "timestamp": timestamp,
                                     "uuid": uuid,
                                     "code": 400,
                                     "description": str(e)
                                 }
                                 )
                elif str(e) == "device is in bootloader mode":
                    error_handle(device,
                                 {
                                     "timestamp": timestamp,
                                     "uuid": uuid,
                                     "code": 401,
                                     "description": str(e)
                                 }
                                 )
                elif "unsupported command" in str(e):
                    error_handle(device,
                                 {
                                     "timestamp": timestamp,
                                     "uuid": uuid,
                                     "code": 300,
                                     "description": str(e)
                                 }
                                 )

        return execept_print

    return except_execute
