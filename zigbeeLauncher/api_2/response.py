import time
import uuid

codes = {
    0: "",
    10000: "device {device} not exist",
    10001: "device {device} is offline",
    10002: "device {device} is in bootloader or upgrading mode",
    10003: "device {device} is in bootloader or upgrading mode",
    10009: "device {device} is in bootloader or upgrading mode",
    20000: "simulator {device} not exist",
    20001: "simulator {device} is offline",
    20002: "simulator {device} error: {error}",
    20003: "simulator {device} unreachable",
    30000: "attribute {attribute} not exist",
    30001: "type {type} not exist",
    30002: "value type incorrect",
    40000: "{device} not in any network",
    40001: "{device} already in a network",
    50000: "file {file} not exist",
    50001: "{file} is not a YAML file",
    90000: "internal error: {error}",
    90001: "missing mandatory item {item}",
    90002: "unsupported command: {command}",
    90003: 'illegal schema:{error}',
    90004: 'json validation failed:{error}',
    90005: 'out of range:{value}',
    90006: 'invalid value:{value}',
    # 90007: 'simulator {simulator} not connected',
    # 90008: 'device {device} no response'
    90007: 'this is a manufacture attribute, please provide "manufacturer_code" and "type"'
}


def pack_response(response, status=200, **kwargs):
    code = response['code']
    if code in codes.keys():
        message = codes[code].format(**kwargs)
    else:
        if 'message' in response:
            message = response['message']
    if 'response' not in response:
        response.update({
            'data': {}
        })
    else:
        response.update({
            "data": response['response']
        })
        del response['response']
    if 'timestamp' not in response and 'uuid' not in response:
        response.update({
            "timestamp": int(round(time.time() * 1000)),
            "uuid": str(uuid.uuid1())
        })
    response.update({
        'code': code,
        'message': message
    })
    return response, status