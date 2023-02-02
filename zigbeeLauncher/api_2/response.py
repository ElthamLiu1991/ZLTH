import time
import uuid


class Response:
    codes = {
        0: "",
        10000: "device {} not exist",
        10001: "device {} is offline",
        10002: "device {} is in bootloader mode",
        10003: "device {} is in upgrading mode",
        10009: "device {} is in configuring mode",
        20000: "simulator {} not exist",
        20001: "simulator {} is offline",
        20002: "simulator {} error: {}",
        20003: "simulator {} unreachable",
        30000: "attribute {} not exist",
        30001: "type {} not exist",
        30002: "value type incorrect",
        40000: "{} not in any network",
        40001: "{} already in a network",
        50000: "file {} not exist",
        50001: "{} is not a YAML file",
        60000: "device {} is not configured yet",
        60001: 'device {} is configuring, please try later',
        70000: 'script {} not exist',
        70001: 'record {} not exist',
        70002: 'config {} invalid',
        70003: 'record {} not running',
        70004: 'record {} is running',
        90000: "internal error: {}",
        90001: "missing mandatory item {}",
        90002: "unsupported command: {}",
        90003: 'illegal schema:{}',
        90004: 'json validation failed:{}',
        90005: 'out of range:{}',
        90006: 'invalid value:{}',
        # 90007: 'simulator {simulator} not connected',
        # 90008: 'device {device} no response'
        90007: 'this is a manufacture attribute, please provide "manufacturer_code" and "type"'
    }

    def __init__(self, *args, code=0, message='', data={}, timestamp=int(round(time.time() * 1000)), uuid=str(uuid.uuid1())):
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = timestamp
        self.uuid = uuid
        self.errors = args

    def pack(self):
        response = self.__dict__
        if self.code == 0:
            state = 200
        elif self.code == 10000 or self.code == 20000 or self.code == 30000 or self.code == 70000:
            state = 404
        else:
            state = 500
        if self.code in self.codes:
            response['message'] = self.codes[self.code].format(*self.errors)
        del response['errors']
        return response, state