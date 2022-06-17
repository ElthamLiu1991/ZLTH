import sys
from binascii import unhexlify
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.serial_protocol import response
from zigbeeLauncher.serial_protocol.SerialProtocol import encode, to_hex, ack

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
configuration_state_change_request = '0A'
status_response = "F0"

bootloader_sequence = 1000
upgrading_start_sequence = 1001
upgrading_stop_sequence = 1002
upgrading_finish_sequence = 0x80


def reset_request_handle(seq, payload=None):
    data = encode(seq, local_setting_command + reset_request, None)
    return data


def reset_bootloader_request_handle(seq, payload=None):
    data = encode(seq, local_setting_command + reset_bootloader_request, None)
    return data


def reset_bootloader_request_response(sequence, dongle, payload):
    dongle.response(bootloader_sequence)


def bootloader_upgrading_start_handle(seq, payload=None):
    return "31"


def bootloader_upgrading_start_response(sequence, dongle, payload):
    dongle.response(upgrading_start_sequence)


def bootloader_upgrading_stop_transfer(seq, payload=None):
    return "32"


def bootloader_upgrading_stop_response(sequence, dongle, payload):
    dongle.response(upgrading_stop_sequence)


def bootloader_upgrading_finish_transfer(seq, payload=None):
    return "32"


def info_request_handle(seq, payload=None):
    return encode(seq, local_setting_command + info_request, None)


@response.cmd(local_setting_command + info_response)
def info_response_handle(sequence, dongle, payload):
    rsp = {
        "connected": True,
        "swversion": payload[:6],
        "hwversion": "1.0.0"
    }
    # 修改dongle属性
    dongle.property.update(**rsp)
    dongle.response(sequence, payload=rsp)


def label_request_handle(seq, payload=None):
    # get label
    return encode(seq, local_setting_command + label_request, None)


@response.cmd(local_setting_command + label_response)
def label_response_handle(sequence, dongle, payload):
    rsp = {
        "label": unhexlify(payload[:-2].encode('utf-8')).decode('utf-8')
    }
    dongle.property.update(**rsp)
    dongle.response(sequence, payload=rsp)


def label_write_handle(seq, data):
    # write label
    data = data + "\0"
    return encode(seq, local_setting_command + label_write, "".join(format(ord(c), "02X") for c in data))


def identify_request_handle(seq, payload=None):
    # identify
    return encode(seq, local_setting_command + identify_request, None)


def state_request_handle(seq, payload=None):
    # request running state, config state
    return encode(seq, local_setting_command + state_request, None)


@response.cmd(local_setting_command + state_response)
def state_response_handle(sequence, dongle, payload):
    dongle.write(ack(local_setting_command + state_response, sequence))
    configured = payload[2:]
    if configured == '01':
        configured = False
    else:
        configured = True

    rsp = {
        "configured": configured
    }
    dongle.property.boot = True
    dongle.property.update(**rsp)
    dongle.response(sequence, payload=rsp)


def configuration_state_change_request_handle(seq, payload=None):
    logger.info("function:%s, seq:%d", sys._getframe().f_code.co_name, seq)
    """
    change device to
    0x00: factory default
    0x01: No configured
    0x02: Fully configured
    :param payload:
    :return:
    """
    return encode(seq, local_setting_command + configuration_state_change_request, payload)


@response.cmd(local_setting_command + status_response)
def status_response_handle(sequence, dongle, payload):
    status = int(payload, 16)
    if status in codes:
        message = codes[status]
    else:
        message = 'unknown failure'
    dongle.response(sequence, code=status, message=message)


codes = {
    0: "",
    1: 'invalid call',
    2: 'invalid data',
    3: 'unsupported',
    4: 'endpoint not found',
    5: 'cluster not found',
    6: 'attribute not found',
    7: 'invalid data type',
    8: 'invalid length',
    9: 'out of space',
    0x0A: 'save data to flash failure',
    0x0B: 'get data from flash failure',
    0x0C: 'not found command in cluster',
    0x0D: 'configuration state error',
    0x0E: 'configuration data error',
    0xFE: 'unknown serial command',
    0xFF: 'unknown failure'
}