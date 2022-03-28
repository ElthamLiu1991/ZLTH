import asyncio
import time
from functools import wraps

from crcmod import mkCrcFun
from binascii import unhexlify, hexlify
from . import response
from .WiserZigbeeDongleCommands import commands, send_command, Command
from .WiserZigbeeGlobal import get_value
from zigbeeLauncher.logging import dongleLogger as logger

start_frame = "AA55"
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

network_config_command = "01"

global sequence
sequence = -1


def timeout(device, timestamp, uuid):
    if get_value("dongle_error_callback"):
        get_value("dongle_error_callback")(device, {
            "timestamp": timestamp,
            "uuid": uuid,
            "code": 300,
            "description": "request timeout"
        })


def error(device, data):
    if "code" in data:
        if get_value("dongle_error_callback"):
            get_value("dongle_error_callback")(device, data)
    else:
        if get_value("dongle_update_callback"):
            get_value("dongle_update_callback")(device, data)


class WiserZigbeeDongleSerial:
    def __init__(self, name, seq, length, payload):
        self.name = name
        self.seq = int(seq, 16)
        self.length = int(length, 16)
        self.payload = payload
        logger.info("Get serial data from %s, seq=%d, length=%d, payload:%s",
                    self.name, self.seq, self.length, self.payload)


def crc16Xmodem_verify(data):
    crc = data[len(data) - 4:]
    data = data[:len(data) - 4]
    crc16 = mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    crc_out = hex(crc16(unhexlify(data))).upper()[2:].zfill(4)
    if (crc_out[2:] + crc_out[:2]) == crc:
        return True
    else:
        return False


def crc16Xmodem_calculate(data):
    crc16 = mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    crc_out = hex(crc16(unhexlify(data))).upper()[2:].zfill(4)
    return crc_out[2:] + crc_out[:2]


def next_sequence():
    global sequence
    if sequence == 255:
        sequence = -1
    sequence = sequence + 1
    return sequence


def encode(command, payload):
    data = command
    data = data + "%02X" % next_sequence()
    if payload:
        data = data + "".join(format(int(len(payload) / 2), "02X"))
        data = data + payload
    else:
        data = data + "00"
    data = data + crc16Xmodem_calculate(data)
    return sequence, start_frame + data


def decode(name, data):
    pri_command = data[:2]
    sec_command = data[2:4]
    seq_number = data[4:6]
    payload_len = data[6:8]
    payload = data[8:-4]
    crc = data[-4:]
    logger.info("decode:%s%s, %s, %s, %s, %s", pri_command, sec_command, seq_number, payload_len, payload, crc)
    response.call(pri_command + sec_command,
                  WiserZigbeeDongleSerial(name, seq_number, payload_len, payload))


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
    if (data.seq, data.name) in commands:
        commands[(data.seq, data.name)].get_response(rsp)
    pass


def label_request_handle(payload=None):
    # get label
    return encode(local_setting_command + label_request, None)


@response.cmd(local_setting_command + label_response)
def label_response_handle(data):
    rsp = {
        "label": unhexlify(data.payload[:-2].encode('utf-8')).decode('utf-8')
    }
    if (data.seq, data.name) in commands:
        commands[(data.seq, data.name)].get_response(rsp)
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
        "state": int(data.payload[:2], 16),
        "configured": int(data.payload[2:], 16)
    }
    if (data.seq, data.name) in commands:
        commands[(data.seq, data.name)].get_response(rsp)


@response.cmd(local_setting_command + status_response)
def status_response_handle(data):
    rsp = {}
    status = int(data.payload, 16)
    if status != 0:
        rsp = {
            "code": status,
            "description": "please refer error code specification"
        }
    if (data.seq, data.name) in commands:
        commands[(data.seq, data.name)].get_response(rsp)
