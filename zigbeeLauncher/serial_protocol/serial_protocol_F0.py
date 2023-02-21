import sys
import time
from binascii import unhexlify
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.serial_protocol import response
from zigbeeLauncher.serial_protocol.serial_protocol import encode, to_hex, ack, from_string, ZLTH_Serial

serial_protocol_schema_F003 = {
        'major_firmware_version':{
            'type': 'integer',
            'length': 1
        },
        'minor_firmware_version':{
            'type': 'integer',
            'length': 1
        },
        'build_firmware_version':{
            'type': 'integer',
            'length': 1
        },
        'application_information':{
            'type': 'integer',
            'length': 1
        },
        'EUI64':{
            'type': 'integer',
            'length': 8
        },
        'hardware_version':{
            'type': 'integer',
            'length': 1
        },
        'bootloader_type':{
            'type': 'integer',
            'length': 1
        }
    }
serial_protocol_schema_F005 = {
        'label_string':{
            'type': 'string'
        }
    }
serial_protocol_schema_F006 = {
    'label':{
        'type': 'string'
    }
}
serial_protocol_schema_F009 = {
        'running_state':{
            'type': 'integer',
            'length': 1,
            "description":"0x00=Staring up"
                          "0x01=Already running"
        },
        'configuration_state':{
            'type': 'integer',
            'length': 1,
            "description":"0x00=Factory default"
                          "0x01=No configure"
                          "0x02=Fully configured"
        }
    }
serial_protocol_schema_F00A = {
    'state_change': {
        'type': 'integer',
        'length': 1
    }
}
serial_protocol_schema_F0F0 = {
        'status':{
            'type': 'integer',
            'length': 1
        }
    }

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
reset_sequence = 0x80


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


@response.cmd(local_setting_command + info_response, serial_protocol_schema_F003)
def info_response_handle(sequence, dongle, protocol):
    swversion = str(protocol.major_firmware_version).zfill(2)+\
        str(protocol.minor_firmware_version).zfill(2)+\
        str(protocol.build_firmware_version).zfill(2)
    rsp = {
        "connected": True,
        "swversion": swversion,
        "hwversion": str(protocol.hardware_version)
    }
    # 修改dongle属性
    dongle.property.update(**rsp)
    dongle.response(sequence, payload=rsp)


def label_request_handle(seq, payload=None):
    # get label
    return encode(seq, local_setting_command + label_request, None)


@response.cmd(local_setting_command + label_response, serial_protocol_schema_F005)
def label_response_handle(sequence, dongle, protocol):
    rsp = {
        "label": protocol.label_string
    }
    dongle.property.update(**rsp)
    dongle.response(sequence, payload=rsp)


# @response.cmd(local_setting_command + label_write, serial_protocol_schema_F006)
# def label_write_handle(seq, payload):
#     # write label
#     protocol = ZLTH_Serial()
#     return protocol.encode(seq, local_setting_command + label_write, payload)

def label_write_handle(seq, data):
    # write label
    return encode(seq, local_setting_command + label_write, from_string(data, len(data)))


def identify_request_handle(seq, payload=None):
    # identify
    return encode(seq, local_setting_command + identify_request, None)


def state_request_handle(seq, payload=None):
    # request running state, config state
    return encode(seq, local_setting_command + state_request, None)


@response.cmd(local_setting_command + state_response, serial_protocol_schema_F009)
def state_response_handle(sequence, dongle, protocol):
    dongle.write(ack(local_setting_command + state_response, sequence))
    configured = protocol.configuration_state
    if configured == 1:
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


@response.cmd(local_setting_command + status_response, serial_protocol_schema_F0F0)
def status_response_handle(sequence, dongle, protocol):
    status = protocol.status
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