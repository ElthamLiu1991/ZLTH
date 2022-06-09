import asyncio
import base64
import platform
import time
from asyncio import transports, Protocol
from binascii import hexlify
from threading import Thread
from typing import Optional

import serial
import serial.tools.list_ports
import serial_asyncio

from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.mqtt.WiserZigbeeDongleInfo import Info
from zigbeeLauncher.serial_protocol import SerialProtocol as protocol
from .WiserZigbeeDongleCommands import Command, send_command, commands_init
from .WiserZigbeeDongleUpgrade import Upgrade, bootloader_stop_transfer, bootloader_stop_transfer_response, \
    bootloader_finish_transfer, bootloader_start_transfer_response, WiserFile
from .WiserZigbeeGlobal import set_value, get_value, except_handle
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *
from zigbeeLauncher.serial_protocol.SerialProtocol02 import *

dongles_dict = {}


class Dongles(Protocol):
    def __init__(self):
        self.name = ""  # mac
        self.port = ""  # name
        self.state = 1
        self.new_state = 1
        self.label = ""
        self.configured = 0
        self.swversion = ""
        self.hwversion = ""
        self.flag = None
        self.data = b''
        self.ready = False

    def set_attributes(self, **kwargs):
        for key in kwargs.keys():
            value = kwargs[key]
            if key == 'port':
                self.port = value
            elif key == "name":
                self.name = value
            elif key == "state":
                self.state = value

    def data_write(self, data):
        self.flag = None
        if type(data) == type(b''):
            self.transport.write(data)
        else:
            self.transport.write(unhexlify(data))

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport
        logger.info("Port connected:%s", self.transport.serial.name)
        transport.serial.rts = False

    def data_received(self, data: bytes) -> None:
        # logger.info("Receive serial data from:%s, %s: %s", self.port, self.name, repr(data))
        if "Serial upload aborted" in repr(data):
            logger.info("%s, %s: Serial upload aborted", self.port, self.name)
            bootloader_stop_transfer_response(self.name)
            if self.new_state != 2:
                # update to 2
                self.new_state = 2
                if get_value("dongle_update_callback"):
                    get_value("dongle_update_callback")(self.name, {"state": 2})

        elif "Serial upload complete" in repr(data):
            logger.info("%s, %s: Serial upload complete", self.port, self.name)
            self.flag = b'\x06'
            if self.new_state != 2:
                # update to 2
                self.new_state = 2
                if get_value("dongle_update_callback"):
                    get_value("dongle_update_callback")(self.name, {"state": 2})

        elif "begin upload" in repr(data):
            logger.info("%s, %s: Serial upload begin", self.port, self.name)
            bootloader_start_transfer_response(self.name)
            if self.new_state != 3:
                self.new_state = 3
                if get_value("dongle_update_callback"):
                    get_value("dongle_update_callback")(self.name, {"state": 3})
        elif "Gecko Bootloader" in repr(data):
            logger.info("%s, %s: Gecko Bootloader", self.port, self.name)
            reset_bootloader_request_response(self.name)
            if self.new_state != 2:
                # update to 2
                self.new_state = 2
                if get_value("dongle_update_callback"):
                    get_value("dongle_update_callback")(self.name, {"state": 2})
        elif self.new_state == 2 or self.new_state == 3 and (b'\x04' in data or b'\x06' in data or b'\x15' in data or b'\x18' in data or b'C' in data):
            if self.new_state != 3:
                self.new_state = 3
                if get_value("dongle_update_callback"):
                    get_value("dongle_update_callback")(self.name, {"state": 3})
            self.flag = data
        else:
            if self.new_state != self.state:
                self.new_state = self.state
                if get_value("dongle_update_callback"):
                    get_value("dongle_update_callback")(self.name, {"state": self.state})
            self.data = self.data + data
            logger.info("receive data:%s", repr(data))
            while len(self.data) >= 2:
                if self.data[0] == 0xaa and self.data[1] == 0x55:
                    if len(self.data) >= 6 and len(self.data) >= (6+self.data[5]+2):
                        record = hexlify(self.data[2:6+self.data[5]+2]).upper().decode()
                        if not protocol.crc16Xmodem_verify(record):
                            logger.warning("CRC check failed for %s", record)
                        else:
                            protocol.decode(self, record)
                        self.data = self.data[6+self.data[5]+2:]
                    else:
                        logger.warning("incomplete package %s", repr(self.data))
                        break
                else:
                    logger.warning("incomplete package %s", repr(self.data))
                    break

    def connection_lost(self, exc: Optional[Exception]) -> None:
        global dongles_dict
        logger.warning("Port disconnected:%s", self.name)
        del dongles_dict[self.name]
        # disconnect
        if get_value("dongle_update_callback"):
            get_value("dongle_update_callback")(self.name, {"connected": False})


def start_loop(loop):
    #  运行事件循环， loop以参数的形式传递进来运行
    asyncio.set_event_loop(loop)
    loop.run_forever()


def scan():
    thread_loop = asyncio.new_event_loop()  # 获取一个事件循环
    run_loop_thread = Thread(target=start_loop, args=(thread_loop,))  # 将次事件循环运行在一个线程中，防止阻塞当前主线程
    run_loop_thread.start()  # 运行线程，同时协程事件循环也会运行
    while True:
        try:
            new_port_list = list(serial.tools.list_ports.comports())
            for port in new_port_list:
                if not port.serial_number or len(port.serial_number) < 5 or port.serial_number[:5] != "ZLTH_":
                    continue
                serial_number = port.serial_number[5:]
                if serial_number not in dongles_dict:
                    # ports.append(port.name)
                    logger.info("Found a new port:%s, %s", port.name, port.serial_number)
                    if platform.system() != "Windows":
                        name = '/dev/'+port.name
                    else:
                        name = port.name
                    future = asyncio.run_coroutine_threadsafe(
                        serial_asyncio.create_serial_connection(thread_loop,
                                                                Dongles,
                                                                name,
                                                                baudrate=460800), thread_loop
                    )
                    # 保存name:serial_number, future元组到ports
                    dongles_dict[serial_number] = future.result()[1]
                    dongles_dict[serial_number].set_attributes(
                        port=port.name, name=serial_number
                    )
                    # pack info
                    Info(dongles_dict[serial_number], get_value("dongle_info_callback"))

        except Exception as e:
            logger.exception("Serial management error:%s", e)

        time.sleep(0.1)


def pack_port_info():
    devices = []
    for key in dongles_dict.keys():
        device = {
            'name': dongles_dict[key].port,
            'mac': dongles_dict[key].name,
            'connected': True,
            'configured': dongles_dict[key].configured,
            'hwversion': dongles_dict[key].hwversion,
            'swversion': dongles_dict[key].swversion,
            'label': dongles_dict[key].label,
            'state': dongles_dict[key].state
        }
        devices.append(device)
    return devices


def upload_port_info(dongle=None):
    if dongle:
        if dongle in dongles_dict:
            if dongles_dict[dongle].state == 1:
                Info(dongles_dict[dongle], get_value("dongle_info_callback"))
            else:
                # device is not in normal mode
                get_value("dongle_info_callback")(dongles_dict[dongle].name, {
                    "name": dongles_dict[dongle].port,
                    "mac": dongles_dict[dongle].name,
                    "connected": True,
                    "swversion": '0',
                    "hwversion": '0',
                    "label": '',
                    "state": dongles_dict[dongle].state,
                    "configured": 0
                })
        else:
            raise Exception("device not exist")
    else:
        for name in dongles_dict.keys():
            if dongles_dict[name].state == 1:
                Info(dongles_dict[name], get_value("dongle_info_callback"))
            else:
                # device is not in normal mode
                get_value("dongle_info_callback")(dongles_dict[name].name, {
                    "name": dongles_dict[name].port,
                    "mac": dongles_dict[name].name,
                    "connected": True,
                    "swversion": '0',
                    "hwversion": '0',
                    "label": '',
                    "state": dongles_dict[name].state,
                    "configured": 0
                })


def init(MQTT_info_callback, MQTT_update_callback=None, MQTT_error_callback=None):
    """
    串口初始化函数，接受MQTT update, error callback
    ports保存name, future
    """
    logger.info("Dongle Management started")
    set_value("dongle_info_callback", MQTT_info_callback)
    set_value("dongle_update_callback", MQTT_update_callback)
    set_value("dongle_error_callback", MQTT_error_callback)
    thread = Thread(target=scan)
    thread.start()
    commands_init()
    set_value("dongle", True)
    set_value('pending', {})


def mqtt_info_callback(name, msg):
    print("info callback here:%s" % msg)


def mqtt_update_callback(name, msg):
    print("update callback here:%s" % msg)


def mqtt_error_callback(name, msg):
    print("error callback here:%s" % msg)


if __name__ == '__main__':
    init(mqtt_info_callback, mqtt_update_callback, mqtt_error_callback)
