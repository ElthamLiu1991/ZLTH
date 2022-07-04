import binascii

from crcmod import mkCrcFun
from binascii import unhexlify, hexlify
from . import response
from zigbeeLauncher.logging import dongleLogger as logger
from ..zigbee.DataType import get_bytes, data_type_value_table, data_type_table

start_frame = "AA55"

global sequence
sequence = -1


class WiserZigbeeDongleSerial:
    def __init__(self, dongle, seq, length, payload):
        self.dongle = dongle
        self.seq = int(seq, 16)
        self.length = int(length, 16)
        self.payload = payload
        # logger.info("Get serial data from %s, seq=%d, length=%d, payload:%s",
        #             self.dongle.name, self.seq, self.length, self.payload)


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


def encode(seq, command, payload):
    data = command
    data = data + "%02X" % seq
    if payload:
        data = data + "".join(format(int(len(payload) / 2), "02X"))
        data = data + payload
    else:
        data = data + "00"
    data = data + crc16Xmodem_calculate(data)
    return start_frame + data


def decode(dongle, data):
    # pri_command = data[:2]
    # sec_command = data[2:4]
    # seq_number = data[4:6]
    # payload_len = data[6:8]
    # payload = data[8:-4]
    # crc = data[-4:]
    # logger.info("%s, decode:%s%s, %s, %s, %s, %s", dongle.property.mac, pri_command, sec_command, seq_number, payload_len, payload, crc)
    # try:
    #     response.call(pri_command + sec_command,
    #                   int(seq_number, 16), dongle, payload)
    # except ValueError as e:
    #     logger.exception("decode error:%ss", str(e))
    instance = ZLTH_Serial(dongle)
    instance.decode(data)


def to_hex(data):
    result = hex(data)[2:]
    if len(result) % 2 != 0:
        result = '0' + result
    return result.upper()


def from_string(data, length=None):
    value = ''.join(format(ord(c), "02X") for c in data)
    if length is not None:
        return to_hex(length) + value
    else:
        return value


def to_string(data):
    value = unhexlify(data.encode('utf-8')).decode('utf-8')
    if value.find('\u0000') == -1:
        return value
    else:
        return value[:value.find('\u0000')]


def big_small_end_convert(data):
    if len(data) % 2 != 0:
        data = '0' + data
    return binascii.hexlify(binascii.unhexlify(data)[::-1]).upper().decode()


def big_small_end_convert_from_int(data, bytes=2):
    data = hex(data)[2:].zfill(bytes * 2)
    return binascii.hexlify(binascii.unhexlify(data)[::-1]).upper().decode()


def big_small_end_convert_to_int(data):
    if len(data) % 2 != 0:
        data = '0' + data
    return int(binascii.hexlify(binascii.unhexlify(data)[::-1]).upper().decode(), 16)


def signed_to_unsigned(value, length):
    # 如果>=0， 直接返回
    # 如果<0，先计算绝对值，然后与该长度最大值进行异或操作，然后加1
    if value >= 0:
        return value
    else:
        value_max = (1 << 8 * length) - 1
        value = abs(value)
        return (value_max ^ value) + 1


def unsigned_to_signed(value, length):
    # 如果>=0， 直接返回
    # 如果<0，先计算绝对值，然后与该长度最大值进行异或操作，然后加1
    value_max = (1 << 8 * length) - 1
    if value >= value_max / 2:
        return -((value - 1) ^ value_max)
    else:
        return value


def ack(command, seq):
    data = command
    data = data + "%02X" % seq
    data = data + "00"
    data = data + crc16Xmodem_calculate(data)
    return start_frame + data


class ZLTH_Serial:
    class Sub_object:
        def __init__(self):
            pass

    def __init__(self, dongle=None):
        self.dongle = dongle
        self.command = ''
        self.sequence = 0
        self.payload = 0
        self.index = 0
        self.data = ''

    def decode(self, data):
        self.command = data[:4]
        self.sequence = int(data[4:6], 16)
        self.payload = data[8:-4]
        logger.info("%s, decode:%s, %d, %s", self.dongle.property.mac, self.command, self.sequence,
                    self.payload)
        try:
            # get serial schema
            self.schema, self.callback = response.get_schema(self.command)
            self.protocol = self.Sub_object()
            self._response_mapping(self.protocol, self.schema)
            logger.info('call %s, sequence:%d', self.command, self.sequence)
            try:
                self.callback(self.sequence, self.dongle, self.protocol)
            except Exception as e:
                logger.exception('handle response error')
        except ValueError as e:
            logger.exception(str(e))

    def encode(self, sequence, command, payload):
        self.sequence = sequence
        self.command = command
        # get schema
        self.schema, self.callback = response.get_schema(self.command)
        self.protocol = self.Sub_object()
        self._request_mapping(self.protocol, self.schema)
        return encode(self.sequence, self.command, self.data)

    def _request_mapping(self, schema, payload):
        try:
            for item in schema:
                _object = schema[item]
                if _object['type'] == 'integer':
                    value = payload[item]
                    if 'length' in _object:
                        length = _object['length'] * 2
                        value = big_small_end_convert_from_int(value, length)
                    if 'enumerate' in _object:
                        value = _object['enumerate'][value]
                    self.data = self.data + value
                elif _object['type'] == 'string':
                    value = payload[item]
                    if 'length' not in _object:
                        length = len(value)
                    else:
                        length = _object['length']
                    value = from_string(value, length)
                    self.data = self.data + value
        except Exception as e:
            logger.exception(str(e))

    def _response_mapping(self, _object, schema):
        try:
            for item in schema:
                payload = schema[item]
                if payload['type'] == 'integer':
                    if 'length' in payload:
                        length = payload['length'] * 2
                        value = big_small_end_convert_to_int(self.payload[self.index: self.index + length])
                        self.index += length
                    else:
                        value = big_small_end_convert_to_int(self.payload[self.index:])
                    if item == 'default' or item == 'value':
                        # 需要分别计算有符号数和无符号数
                        if _object.type in ['int8', 'int16', 'int24', 'int32', 'int48', 'int56', 'int64']:
                            value = unsigned_to_signed(value, data_type_table[data_type_value_table[_object.type]])
                    if 'enumerate' in payload:
                        value = payload['enumerate'][value]
                    _object.__dict__.update({item: value})

                elif payload['type'] == 'string':
                    if 'length' not in payload:
                        # get util last bytes, the first byte is length
                        value = to_string(self.payload[self.index+2:])
                    else:
                        length = payload['length'] * 2
                        value = to_string(self.payload[self.index + 2: self.index + length])
                        self.index += length
                    _object.__dict__.update({item: value})
                elif payload['type'] == 'array':
                    length = payload['length']
                    if isinstance(length, str):
                        length = _object.__dict__[length]
                    _object.__dict__.update({item: []})
                    for i in range(length):
                        _sub_object = self.Sub_object()
                        self._response_mapping(_sub_object, payload['object'])
                        _object.__dict__[item].append(_sub_object)
                else:
                    # type为_object的一个属性
                    _payload = payload.copy()
                    _schema = {item: _payload}
                    _type = _object.__dict__[_payload['type']]
                    if get_bytes(data_type_value_table[_type]) == 0:
                        # string
                        _payload['type'] = 'string'
                    else:
                        # integer
                        _payload['type'] = 'integer'
                    if 'length' in _payload:
                        length = _payload['length']
                        if isinstance(length, str):
                            _payload['length'] = _object.__dict__[length]
                    self._response_mapping(_object, _schema)
        except Exception as e:
            logger.exception(str(e))
