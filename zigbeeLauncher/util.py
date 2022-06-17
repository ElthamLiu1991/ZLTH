import os

import rapidjson as json
import socket
import time
import uuid
from functools import wraps

from zigbeeLauncher.logging import utilLogger as logger
from zigbeeLauncher.request_and_response import wait_response

mqtt_error_code = {
    1000: "device {} not exist",
    2000: 'unsupported command: {}',
    3000: 'json validation failed: {}',
    4000: 'missing key:{}',
    9000: 'internal error: {}'
}


def payload_validate(data):
    json.Validator('{"required":["timestamp", "uuid", "data"]}')(data)


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


def send_command(client, topic, body):
    timestamp = int(round(time.time() * 1000))
    uid = str(uuid.uuid1())
    # 加入request等待队列
    task = wait_response(timestamp, uid)
    payload = {
        "timestamp": timestamp,
        "uuid": uid,
        "data": body
    }
    client.publish(topic, json.dumps(payload))
    result = task.result()
    if result == {}:
        result = {
            'code': 91000,
            'message': "no response",
            'timestamp': timestamp,
            'uuid': uid,
            'response': {
            }
        }
    return result


def pack_payload(data):
    timestamp = int(round(time.time() * 1000))
    uid = str(uuid.uuid1())
    return json.dumps({
        "timestamp": timestamp,
        "uuid": uid,
        "data": data
    })

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
        else:
            return func(*args, **kwargs)


def except_handle(error_handle):
    # msg用于自定义函数的提示信息
    def except_execute(func):
        @wraps(func)
        def except_print(*args, **kwargs):
            device = None
            try:
                payload_validate(args[2])
                payload = json.loads(args[2])
                timestamp = payload["timestamp"]
                uuid = payload["uuid"]
                if len(args) == 4:
                    # device command
                    device = args[3]
                return func(*args, **kwargs)
            except json.JSONDecodeError as e:
                code = 3000
                message = mqtt_error_code.format(str(e))
            except json.ValidationError as e:
                code = 3000
                message = mqtt_error_code.format(str(e))
            except KeyError as e:
                code = 4000
                message = mqtt_error_code.format(str(e))
            except Exception as e:
                message = str(e)
                if str(e) == "device not exist":
                    code = 1000
                    message = mqtt_error_code.format(str(e))
                elif "unsupported command" in str(e):
                    code = 2000
                    message = mqtt_error_code.format(str(e))
                else:
                    code = 900
                    message = mqtt_error_code.format(str(e))
            if code != 0:
                if device:
                    error_handle(device=device,
                                 code=code,
                                 message=message,
                                 payload={},
                                 timestamp=timestamp,
                                 uuid=uuid)
                else:
                    error_handle(code=code,
                                 message=message,
                                 payload={},
                                 timestamp=timestamp,
                                 uuid=uuid)
        return except_print

    return except_execute
