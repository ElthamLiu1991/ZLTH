import binascii

from crcmod import mkCrcFun
from binascii import unhexlify, hexlify
from zigbeeLauncher.mqtt import response
from zigbeeLauncher.mqtt.WiserZigbeeGlobal import get_value
from zigbeeLauncher.logging import dongleLogger as logger

start_frame = "AA55"

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
    def __init__(self, dongle, seq, length, payload):
        self.dongle = dongle
        self.seq = int(seq, 16)
        self.length = int(length, 16)
        self.payload = payload
        logger.info("Get serial data from %s, seq=%d, length=%d, payload:%s",
                    self.dongle.name, self.seq, self.length, self.payload)


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


def decode(dongle, data):
    pri_command = data[:2]
    sec_command = data[2:4]
    seq_number = data[4:6]
    payload_len = data[6:8]
    payload = data[8:-4]
    crc = data[-4:]
    logger.info("decode:%s%s, %s, %s, %s, %s", pri_command, sec_command, seq_number, payload_len, payload, crc)
    try:
        response.call(pri_command + sec_command,
                      WiserZigbeeDongleSerial(dongle, seq_number, payload_len, payload))
    except ValueError as e:
        logger.exception("decode error:%ss", str(e))


def to_hex(data):
    result = hex(data)[2:]
    if len(result) % 2 != 0:
        result = '0'+result
    return result


def big_small_end_convert(data):
    if len(data) % 2 != 0:
        data = '0'+data
    return binascii.hexlify(binascii.unhexlify(data)[::-1]).upper().decode()
