from binascii import unhexlify
from dataclasses import dataclass, field
from typing import Any

from crcmod import mkCrcFun

from zigbeeLauncher.exceptions import OutOfRange
from zigbeeLauncher.util import Global
from zigbeeLauncher.logging import serialLogger as logger


def crc_verify(data: bytes, crc: bytes):
    """
    verify CRC
    :param data: bytes data
    :param crc: CRC, bytes
    :return: True if verify success, otherwise False
    """
    crc16 = mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    _crc = int.to_bytes(crc16(data), 2, byteorder='little')
    if crc == _crc:
        return True
    else:
        logger.error(f"CRC verify failed, expect {crc.decode()}, actually {_crc.decode()}")
        return False


def crc_calculate(data: bytes):
    """
    calculate CRC
    :param data: bytes data
    :return: CRC result, bytes, little endian
    """
    crc16 = mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    return int.to_bytes(crc16(data[2:]), 2, byteorder='little')


def encode_int(data, length, big=False):
    """
    int to bytes, include negative
    :param data: int
    :param length: int length
    :return: bytes
    """
    try:
        if data < 0:
            data = data & (1 << 8 * length) - 1
        if big:
            return int.to_bytes(data, length=length, byteorder='big')
        return int.to_bytes(data, length=length, byteorder='little')
    except OverflowError as e:
        raise OutOfRange(data, f'[0, {(1<<8*length)-1}]')


def encode_str(data, length):
    """
    str to bytes
    :param data: str
    :param length: bytes length
    :return: bytes
    """
    suffix = b''.join(b'\x00' for i in range(0, length - len(data)))
    # return encode_int(length, 1) + data.encode('ascii')[:length] + suffix
    return data.encode('ascii')[:length] + suffix


def decode_int(data: bytes, length, negative=False, big=False):
    """
    bytes to int, include negative
    :param data: bytes data
    :param length: integer length
    :param negative: negative flag
    :param big: big-endian flag
    :return: int
    """
    if big:
        data = int.from_bytes(data, byteorder='big')
    else:
        data = int.from_bytes(data, byteorder='little')
    max = (1 << 8 * length) - 1
    if negative and data > max/2:
        return -((data - 1) ^ max)
    else:
        return data


def decode_str(data: bytes):
    """
    byte to str
    :param data: bytes data
    :return: str
    """
    if data.find(b'\x00') != -1:
        return data.decode()[:data.find(b'\x00')]
    else:
        return data.decode()


class SPType:
    BOOL = 0
    INT = 1
    STR = 2
    OBJ = 3
    ARR = 4


class SerialProtocol:
    id = 0

    # attrs = []

    def __init__(self, id):
        self.id = id
        self.sequence = 0
        self.attrs = []
        self.sp_response = SPResponse(code=0, message="", data={})
        pass

    def register(self, attr, type, length, default_value=None, array_count_name=None):
        self.attrs.append((attr, type, length, array_count_name))
        setattr(self, attr, default_value)

    def serialize(self, sequence):
        """
        将类转化为串口数据
        :return: bytes, prefix+payload+CRC
        """
        self.sequence = sequence
        data = self._prefix(sequence)
        length, payload = self._encode()
        data += encode_int(length, 1)
        data += payload
        # data += self._encode()
        data += crc_calculate(data)
        return data

    def deserialize(self, mac, sequence, data):
        """
        将串口数据转化为类对象
        :param mac: dongle mac地址
        :param sequence: 命令sequence
        :param data: 串口数据
        :return:
        """
        self.sequence = sequence
        self.dongle = Global.get(Global.DONGLES).get(mac)
        if not self.dongle:
            logger.warning(f'donge {mac} not found')
        else:
            self._decode(data)
            self._response(mac, sequence)

    def _response(self, mac, sequence):
        self.dongle.get_response(sequence, self.sp_response)

    def _prefix(self, sequence):
        data = encode_int(0x55aa, 2)
        data += encode_int(self.id, 2, big=True)
        data += encode_int(sequence, 1)
        return data

    def _encode(self):
        """
        encode attributes to bytes
        :return:
        """
        len = 0
        data = b''
        for attr, type, length, count in self.attrs:
            value = getattr(self, attr)
            if type == SPType.BOOL:
                len += length
                data += encode_int(int(value), length)
            elif type == SPType.INT:
                len += length
                data += encode_int(value, length)
                pass
            elif type == SPType.STR:
                len += length
                data += encode_str(value, length)
                pass
            elif type == SPType.OBJ:
                _len, payload = value._encode()
                data += payload
                len += _len
                pass
            elif type == SPType.ARR:
                for obj in value:
                    _len, payload = obj._encode()
                    data += payload
                    len += _len
                pass
        return len, data

    def _decode(self, data):
        """
        decode bytes to attributes
        :return:
        """
        index = 0
        for attr, type, length, count in self.attrs:
            if index == len(data):
                break
            if type == SPType.BOOL:
                value = bool(decode_int(data[index:index + length], length))
                logger.info(f"decode: {attr}, {value}")
                setattr(self, attr, value)
            elif type == SPType.INT:
                value = decode_int(data[index:index + length], length)
                logger.info(f"decode: {attr}, {value}")
                setattr(self, attr, value)
                pass
            elif type == SPType.STR:
                if length == 0:
                    value = decode_str(data[index:])
                    index = len(data)-index
                else:
                    value = decode_str(data[index:index + length])
                logger.info(f"decode: {attr}, {value}")
                setattr(self, attr, value)
                pass
            elif type == SPType.OBJ:
                obj = getattr(self, attr)()
                # instance = obj()
                offset = obj._decode(data[index:])
                index += offset
                setattr(self, attr, obj)
                pass
            elif type == SPType.ARR:
                value = []
                obj = getattr(self, attr)
                for i in range(0, getattr(self, count)):
                    instance = obj()
                    offset = instance._decode(data[index:])
                    value.append(instance)
                    index += offset
                setattr(self, attr, value)
                pass
            index += length
        return index


class Response:
    def __init__(self, sp):
        self._sp = sp
        Global.set(sp.id, self)

    def __call__(self):
        obj = self._sp()
        return obj


class ACK(SerialProtocol):
    id = 0

    def __init__(self, command=None):
        super().__init__(command)
        self.register('payload', SPType.INT, 1, 0)


@dataclass
class SPResponse:
    code: int
    message: str
    data: Any
