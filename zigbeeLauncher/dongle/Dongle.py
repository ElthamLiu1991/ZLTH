import asyncio
import base64
import threading
import time
import uuid
from multiprocessing import Queue
from typing import Optional
from asyncio import transports, Protocol
from binascii import unhexlify, hexlify

# import serial
# from serial import SerialException

# from zigbeeLauncher.dongle.Command import Commands
from zigbeeLauncher.dongle.Config import GetConfig, SetConfig
from zigbeeLauncher.dongle.Info import Info
# from zigbeeLauncher.dongle.Serial_multithread import Serial
from zigbeeLauncher.dongle.Task import Tasks
from zigbeeLauncher.dongle.Upgrade import WiserFile, Upgrade
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.mqtt.Callbacks import dongle_update_callback, dongle_error_callback
from zigbeeLauncher.serial_protocol.SerialProtocol import crc16Xmodem_verify, decode
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *
from zigbeeLauncher.serial_protocol.SerialProtocol02 import *
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *

dongles = {}


class Dongles:
    def __init__(self, mac, port):
        self.property = self.Property(mac, port)
        self.serial = None
        self.mqtt = None
        self.commands = {}
        self.sequence = 0
        self.data = b''
        self.flag = b''

    # multi-threading
    # def isReady(self, port):
    #     self.serial = Serial(port,
    #                          connected=self._connected,
    #                          disconnected=self._disconnected,
    #                          received=self._received)
    #     if self.serial.is_open():
    #         self.serial.start()
    #         return True
    #     else:
    #         return False

    # coroutine
    def ready(self, serial):
        self.serial = serial
        self.serial.ready(self._received, self._connected, self._disconnected)

    def request(self, **kwargs):
        self._next_sequence()
        command = self.Commands(self.property.mac,
                                self.sequence,
                                self.write,
                                self.timeout,
                                **kwargs)
        if 'sequence' in kwargs:
            self.commands[kwargs['sequence']] = command
        else:
            self.commands[self.sequence] = command
        return command

    def response(self, seq, *args, **kwargs):
        if seq not in self.commands:
            return
        command = self.commands[seq]
        command.done_flag = True
        command.response(*args, **kwargs)

    def timeout(self, seq):
        if seq in self.commands:
            del self.commands[seq]

    def _next_sequence(self):
        if self.sequence == 255:
            self.sequence = -1
        self.sequence = self.sequence + 1
        return self.sequence

    def activated(self):
        self.mqtt = self.Mqtt(self)
        self.mqtt.start()
        self.serial.start()
        now = time.time()
        # while not self.property.boot:
        #     if time.time() - now > 1:
        #         break
        threading.Thread(target=Info, args=(self,)).start()

    def _deactivated(self):
        if self.serial:
            self.serial.stop()
        if self.mqtt:
            self.mqtt.stop()

    def _connected(self):
        logger.info("Dongle %s, %s connected", self.property.port, self.property.mac)
        self.property.update(connected=True)

    def _disconnected(self):
        logger.error("Dongle %s, %s disconnected", self.property.port, self.property.mac)
        if self.property.mac in dongles:
            del dongles[self.property.mac]
        self._deactivated()
        self.property.update(connected=False)

    def _received(self, data):
        self._serial_handle(data)

    def write(self, data):
        return self.serial.write(data)

    def _serial_handle(self, data):
        mac = self.property.mac
        port = self.property.port
        if "Serial upload aborted" in repr(data):
            logger.info("%s, %s: Serial upload aborted", port, mac)
            bootloader_upgrading_stop_response(upgrading_stop_sequence, self, {})
            self.property.update(state=2)

        elif "Serial upload complete" in repr(data):
            logger.info("%s, %s: Serial upload complete", port, mac)
            self.flag = b'\x06'
            self.property.update(state=2)

        elif "begin upload" in repr(data):
            logger.info("%s, %s: Serial upload begin", port, mac)
            bootloader_upgrading_start_response(upgrading_start_sequence, self, {})
            self.property.update(state=3)

        elif "Gecko Bootloader" in repr(data):
            logger.info("%s, %s: Gecko Bootloader", port, mac)
            reset_bootloader_request_response(bootloader_sequence, self, {})
            self.property.update(state=2)
        elif (self.property.state == 2 or self.property.state == 3) and (
                b'\x04' in data or b'\x06' in data or b'\x15' in data or b'\x18' in data or b'C' in data):
            self.property.update(state=3)
            self.flag = data
        else:
            self.data = self.data + data
            while len(self.data) >= 2:
                if self.data[0] == 0xaa and self.data[1] == 0x55:
                    if len(self.data) >= 6 and len(self.data) >= (6 + self.data[5] + 2):
                        record = hexlify(self.data[2:6 + self.data[5] + 2]).upper().decode()
                        if not crc16Xmodem_verify(record):
                            logger.warning("CRC check failed for %s", record)
                        else:
                            decode(self, record)
                        self.data = self.data[6 + self.data[5] + 2:]
                    else:
                        logger.warning("incomplete package %s", repr(self.data))
                        break
                else:
                    logger.warning("incomplete package %s", repr(self.data))
                    break

    class Mqtt(threading.Thread):
        def __init__(self, dongle):
            threading.Thread.__init__(self)
            self.dongle = dongle
            self.queue = Queue(0)
            self._exit = False

        def stop(self):
            self._exit = True

        def add(self, payload):
            self.queue.put_nowait(payload)

        def run(self) -> None:
            while not self._exit:
                if self.queue.empty():
                    continue
                payload = self.queue.get()
                self.handle(payload)

            print("exit dongle MQTT")
            """
            thread to handle MQTT data
            :return:
            """
            pass

        def handle(self, payload):
            timestamp = payload['timestamp']
            uuid = payload['uuid']
            for key in payload['data']:
                data = payload['data'][key]
                logger.info('key:%s', key)
                if key == 'config':
                    if 'endpoints' in data:
                        threading.Thread(target=SetConfig, args=(self.dongle, data, timestamp, uuid,)).start()
                    else:
                        threading.Thread(target=GetConfig, args=(self.dongle, timestamp, uuid)).start()
                elif key == 'firmware':
                    if 'data' in data:
                        if "filename" in data:
                            filename = data["filename"]
                        else:
                            filename = uuid.uuid1()
                        filename = './firmwares/' + filename
                        # save data to file
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(data["data"]))
                    else:
                        # upgrade firmware by file
                        filename = './firmwares/' + data['filename']
                    file = WiserFile(filename)
                    threading.Thread(target=Upgrade, args=(self.dongle, file, )).start()
                else:
                    logger.info(', payload:%s', data)
                    command = self.dongle.request(
                        response_cb=dongle_error_callback,
                        timestamp=timestamp,
                        uuid=uuid
                    )
                    if key == 'identify':
                        command.request_cb = identify_request_handle
                        command.send()
                    elif key == 'reset':
                        if self.dongle.property.state == 3:
                            command.request_cb = bootloader_upgrading_stop_transfer
                            if command.send().result():
                                command = self.dongle.request(
                                    response_cb=dongle_error_callback,
                                    timestamp=timestamp,
                                    uuid=uuid
                                )
                                command.request_cb = bootloader_upgrading_finish_transfer
                                command.send()
                        elif self.dongle.property.state == 2:
                            command.request_cb = bootloader_upgrading_finish_transfer
                            command.send()
                        else:
                            command.request_cb = reset_request_handle
                            command.send()
                    elif key == 'label':
                        command.request_cb = label_write_handle
                        label = data['data']
                        if command.send(label).result():
                            # update label
                            self.dongle.property.update(label=label)
                    elif key == 'join':
                        command.request_cb = join_network_request_handle
                        command.send()
                    elif key == 'join':
                        command.request_cb = join_network_request_handle
                        command.send()
                    elif key == 'leave':
                        command.request_cb = leave_network_request_handle
                        command.send()
                    elif key == 'data_request':
                        command.request_cb = data_request_handle
                        command.send()
                    elif key == 'attribute':
                        if 'value' in data:
                            # write attribute
                            command.request_cb = attribute_write_request_handle
                        else:
                            # get attribute
                            command.request_cb = attribute_request_handle
                        command.send(data)

    class Property:
        def __init__(self, mac, port):
            self.mac = mac
            self.port = port
            self.state = 1
            self.new_state = 1
            self.label = ''
            self.configured = False
            self.swversion = ''
            self.hwversion = ''
            self.connected = True
            self.zigbee = {}
            self.ready = False
            self.boot = False

        def default(self):
            return {
                'name': self.port,
                'mac': self.mac,
                'state': self.state,
                'connected': True,
                'configured': 0,
                'label': '',
                'swversion': '',
                'hwversion': '',
                'zigbee': {
                    "node_id": 65534,
                    "device_type": "unknown",
                    "extended_pan_id": 0,
                    "channel": 255,
                    "pan_id": 65535
                }
            }

        def get(self):
            return {
                'name': self.port,
                'mac': self.mac,
                'state': self.state,
                'connected': self.connected,
                'configured': self.configured,
                'label': self.label,
                'swversion': self.swversion,
                'hwversion': self.hwversion,
                'zigbee': self.zigbee
            }

        def update(self, **kwargs):
            payload = {}
            for key in kwargs:
                if key in self.__dict__ and kwargs[key] != self.__dict__[key]:
                    payload.update({key: kwargs[key]})
            self.__dict__.update(kwargs)
            if self.ready and payload != {}:
                dongle_update_callback(self.mac, payload)

    class Commands:
        def __init__(self, mac, seq, write, done, request_cb=None, response_cb=None, timeout_cb=None, retry=None,
                     timestamp=0, uuid='', **kwargs):
            self.mac = mac
            self.sequence = seq
            self.write = write
            self.done = done
            self.request_cb = request_cb
            self.response_cb = response_cb
            self.timeout_cb = timeout_cb
            self.retry = retry
            self.timestamp = timestamp
            self.uuid = uuid
            self.failed = False
            self.done_flag = False
            self.retry_counter = 0
            self.retry_max = 5

        def send(self, *args, **kwargs):
            self.done_flag = False
            tasks = Tasks()
            return tasks.add(self._send_request(*args, **kwargs))

        def response(self, code=0, message='', payload={}):
            if self.response_cb:
                if code != 0:
                    self.failed = True
                    logger.error("request failed:%d, timestamp:%d, uuid:%s", code, self.timestamp, self.uuid)
                else:
                    self.failed = False
                self.response_cb(device=self.mac,
                                 code=code,
                                 message=message,
                                 payload=payload,
                                 timestamp=self.timestamp,
                                 uuid=self.uuid)

        async def _send_request(self, *args, **kwargs):
            """
            async task for sending serial data and check timeout, if self.timeout_cb is None, use
            default timeout handle to resend serial data
            :param args:
            :param kwargs:
            :return:
            """
            while True:
                data = self.request_cb(self.sequence, *args, **kwargs)
                self.write(data)
                try:
                    await asyncio.wait_for(self._wait_response(), timeout=1)
                except asyncio.TimeoutError:
                    self.failed = True
                    if self.timeout_cb:
                        logger.error("request timeout, sequence: %d, timestamp:%d, uuid:%s", self.sequence, self.timestamp, self.uuid)
                        self.timeout_cb(device=self.mac,
                                        code=5000,
                                        message='request timeout',
                                        payload={},
                                        timestamp=self.timestamp,
                                        uuid=self.uuid,
                                        callback=self.retry)
                        break
                    else:
                        logger.error("request timeout, sequence: %d, retry:%d", self.sequence,
                                     self.retry_counter)
                        if self.retry_counter < self.retry_max:
                            self.retry_counter = self.retry_counter + 1
                            continue
                        else:
                            self.response(code=5000, message='request timeout')
                self.done(self.sequence)
                if self.failed:
                    return False
                return True

        async def _wait_response(self):
            while not self.done_flag:
                await asyncio.sleep(0.05)
            return

