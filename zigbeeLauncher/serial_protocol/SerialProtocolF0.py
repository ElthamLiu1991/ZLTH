from binascii import unhexlify

from zigbeeLauncher.mqtt.WiserZigbeeDongleCommands import commands
from zigbeeLauncher.serial_protocol.SerialProtocol import encode
from zigbeeLauncher.mqtt import response

local_setting_command = "F0"
reset_request = "00"
reset_bootloader_request = "01"
info_request = "02"
info_response = "03"
label_request = "04"
label_response = "05"
label_write = "06"
identify_request = "07"
state_request = "08"
state_response = "09"
status_response = "F0"


def reset_request_handle(payload=None):
    seq, data = encode(local_setting_command + reset_request, None)
    seq = 0x80
    return seq, data


def reset_bootloader_request_handle(payload=None):
    # return encode(local_setting_command + reset_bootloader_request, None)
    seq, data = encode(local_setting_command + reset_bootloader_request, None)
    seq = 1000
    return seq, data


def reset_bootloader_request_response(device):
    if (1000, device) in commands:
        commands[(1000, device)].get_response(0)


def info_request_handle(payload=None):
    return encode(local_setting_command + info_request, None)


@response.cmd(local_setting_command + info_response)
def info_response_handle(data):
    rsp = {
        "connected": True,
        "swversion": data.payload[:6],
        "hwversion": "1.0.0"
    }
    # 修改dongle属性
    data.dongle.swversion = rsp['swversion']
    data.dongle.hwversion = rsp['hwversion']
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    pass


def label_request_handle(payload=None):
    # get label
    return encode(local_setting_command + label_request, None)


@response.cmd(local_setting_command + label_response)
def label_response_handle(data):
    rsp = {
        "label": unhexlify(data.payload[:-2].encode('utf-8')).decode('utf-8')
    }
    data.dongle.label = rsp['label']
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
    pass


def label_write_handle(data):
    # write label
    data = data + "\0"
    return encode(local_setting_command + label_write, "".join(format(ord(c), "02X") for c in data))


def identify_request_handle(payload=None):
    # identify
    return encode(local_setting_command + identify_request, None)


def state_request_handle(payload=None):
    # request running state, config state
    return encode(local_setting_command + state_request, None)


@response.cmd(local_setting_command + state_response)
def state_response_handle(data):
    rsp = {
        "configured": int(data.payload[2:], 16)
    }
    data.dongle.configured = rsp['configured']
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)


@response.cmd(local_setting_command + status_response)
def status_response_handle(data):
    rsp = {}
    status = int(data.payload, 16)
    if status != 0:
        rsp = {
            "code": status,
            "description": "please refer error code specification"
        }
    if (data.seq, data.dongle.name) in commands:
        commands[(data.seq, data.dongle.name)].get_response(rsp)
