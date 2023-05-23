import copy
from functools import wraps
from binascii import unhexlify, hexlify

from dacite import from_dict
from zigbeeLauncher.dongle.command import Command, Request
from zigbeeLauncher.data_model import DeviceInfo, Message, CommandDevice, ZigbeeInfo, ErrorMessage
from zigbeeLauncher.dongle.config import GetConfig, SetConfig
from zigbeeLauncher.dongle.info import Info
from zigbeeLauncher.serial_protocol.sp_01 import Leave, DataRequest, JoinNetwork
from zigbeeLauncher.serial_protocol.sp_02 import ReadAttribute, WriteAttribute
from zigbeeLauncher.serial_protocol.sp_f0 import BOOTLOADER_SEQ, UPGRADE_START_SEQ, UPGRADE_STOP_SEQ, RESET_SEQ, Reset, \
    WriteLabel, Identify
from zigbeeLauncher.exceptions import InvalidPayload, exception, Unsupported, OutOfRange
from zigbeeLauncher.serial_protocol.sp import decode_int, crc_verify, SPResponse
from zigbeeLauncher.tasks import Tasks
from zigbeeLauncher.dongle.upgrade import WiserFile, Upgrade
from zigbeeLauncher.util import Global, get_ip_address
from zigbeeLauncher.logging import dongleLogger as logger


class DongleMetaData:
    class DongleState:
        UN_COMMISSIONED = 1
        BOOTLOADER = 2
        UPGRADING = 3
        PAIRING = 4
        JOINED = 6
        ORPHAN = 7
        CONFIGURING = 9

    class DongleConfigured:
        FACTORY_DEFAULT = 0
        NO_CONFIGURED = 1
        FULLY_CONFIGURED = 2

    def __init__(self, mac, port, update_cb):
        self.mac = mac
        self.name = port
        self._info = DeviceInfo(ip=get_ip_address(),
                                mac=self.mac,
                                name=self.name,
                                state=self.DongleState.UN_COMMISSIONED,
                                connected=True,
                                configured=False,
                                label="",
                                swversion="",
                                hwversion="",
                                zigbee=ZigbeeInfo(mac=self.mac,
                                                  channel=0xFF,
                                                  node_id=0xFFFE,
                                                  device_type='unknown',
                                                  pan_id=0xFFFF,
                                                  extended_pan_id=hex(0)[2:])
                                )
        self._default = copy.copy(self._info)
        self.update_cb = update_cb

    @staticmethod
    def update(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            func(*args, **kwargs)
            args[0].update_cb({func.__code__.co_varnames[1]: args[1]})

        return decorator

    @property
    def info(self):
        """
        pack dongle info data to dict
        :return:
        """
        return self._info

    @property
    def default(self):
        return

    @property
    def state(self):
        return self._info.state

    @state.setter
    @update
    def state(self, state):
        self._info.state = state

    @property
    def label(self):
        return self._info.label

    @label.setter
    @update
    def label(self, label):
        self._info.label = label

    @property
    def configured(self):
        return self._info.configured

    @configured.setter
    @update
    def configured(self, configured):
        self._info.configured = configured

    @property
    def swversion(self):
        return self._info.swversion

    @swversion.setter
    @update
    def swversion(self, swversion):
        self._info.swversion = swversion

    @property
    def hwversion(self):
        return self._info.hwversion

    @hwversion.setter
    @update
    def hwversion(self, hwversion):
        self._info.hwversion = hwversion

    @property
    def connected(self):
        return self._info.connected

    @connected.setter
    @update
    def connected(self, connected):
        self._info.connected = connected

    @property
    def zigbee(self):
        return self._info.zigbee

    @zigbee.setter
    @update
    def zigbee(self, zigbee):
        self._info.zigbee = zigbee


class Dongle(DongleMetaData, Request):

    def __init__(self, mac, port):
        super().__init__(mac, port, self.send_update)
        self.property = self.Property()
        self._ready = False
        self._serial = None
        self._commands = {}
        self._sequence = 0
        self._data = b''
        self.flag = b''

        self._sender = None

    # Request methods
    def response(self, mac, uuid, timestamp, sp_response, sender):
        logger.info(f'response {mac}, {uuid}, {timestamp}, {sp_response}')
        # broadcast error
        self.send_error(sender, ErrorMessage(uuid=uuid,
                                             timestamp=timestamp,
                                             code=sp_response.code,
                                             message=sp_response.message,
                                             data=sp_response.data))

    def timeout(self, mac, sequence, uuid, timestamp):
        logger.info(f'timeout {mac}, {sequence}, {uuid}, {timestamp}')
        if sequence in self._commands:
            del self._commands[sequence]
        return

    # error, update, info notification
    def send_error(self, sender, error: ErrorMessage):
        if not self._ready:
            return
        # error = from_dict(data_class=ErrorMessage, data=message)
        Global.get(Global.SIMULATOR).client.send_error(sender, error)

    def send_info(self):
        if not self._ready:
            return
        Global.get(Global.SIMULATOR).client.send_device_info(self.mac, self.info)

    def send_update(self, data):
        if not self._ready:
            return
        Global.get(Global.SIMULATOR).client.send_device_update(self.mac, data)

    def is_ready(self):
        return self._ready

    # coroutine
    def ready(self, serial):
        self._serial = serial
        self._serial.ready(self._received, self._connected, self._disconnected)

    def pack_request(self, message: Message = None, sequence=None, request=None, response=None, timeout=None,
                     retry=1, data=None):
        """
        pack a serial command
        :param message: data_model.Message object
        :param sequence: user specific sequence, use self management sequence number as default
        :param request: serial protocol API
        :param response: command response callback
        :param timeout: command timeout callback
        :param retry: retry setting
        :param data: data ready send to serial
        :return: 
        """
        bootloader = False
        if sequence == BOOTLOADER_SEQ:
            bootloader = True
        if not sequence or bootloader:
            sequence = self._next_sequence()
        self._next_sequence()

        uuid = ""
        timestamp = 0
        if message:
            uuid = message.uuid
            timestamp = message.timestamp
        command = Command(self.mac, self._serial.write, sequence, uuid, timestamp, self._sender)
        command.ready(request, response, timeout, retry, data)
        # add to command dict
        if bootloader:
            sequence = BOOTLOADER_SEQ
        logger.info(f"pending command:{sequence}, {command.request}")
        self._commands[sequence] = command

        return command

    def get_response(self, sequence, sp):
        """
        serial response handle, search pending command to mark it done
        :param sequence: command sequence number
        :param sp: serial protocol instance
        :return: 
        """
        logger.info(f'serial response:{sequence}, {sp}')
        if sequence not in self._commands:
            return
        command = self._commands[sequence]
        command.done = sp

        del self._commands[sequence]

    def cancel(self, sequence):
        """
        cancel pending command
        :param sequence: command sequence
        :return:
        """
        if sequence in self._commands:
            self._commands[sequence].cancel()
            del self._commands[sequence]

    def write(self, data):
        self._serial.write(data)

    def _next_sequence(self):
        if self._sequence == 255:
            self._sequence = -1
        self._sequence = self._sequence + 1
        return self._sequence

    def activated(self):
        pass

    def _deactivated(self):
        """
        delete all pending commands
        :return: 
        """
        for k, v in self._commands.items():
            v.cancel()
            del v

        self._commands.clear()
        pass
        # if self._serial:
        #     self._serial.stop()
        # if self.mqtt:
        #     self.mqtt.stop()

    def _connected(self):
        logger.info(f"Dongle {self.name}, {self.mac} connected")
        self.connected = True
        # get info
        info = Info(self)

    def _disconnected(self):
        logger.warning(f"Dongle {self.name}, {self.mac} disconnected")
        dongles = Global.get(Global.DONGLES)
        if self.mac in dongles:
            del dongles[self.mac]
        self._deactivated()
        self.connected = False

    def _received(self, data):
        tasks = Tasks()
        tasks.add(self._serial_handle(data))

    async def _serial_handle(self, data):
        mac = self.mac
        name = self.name
        if "Serial upload aborted" in repr(data):
            logger.info(f"{name}, {mac}: Serial upload aborted")
            # bootloader_upgrading_stop_response(upgrading_stop_sequence, self, {})
            # self.property.update(state=2)
            self.state = self.DongleState.BOOTLOADER
            self.get_response(UPGRADE_STOP_SEQ, SPResponse(code=0, message="", data={}))

        elif "Serial upload complete" in repr(data):
            logger.info(f"{name}, {mac}: Serial upload complete")
            self.flag = b'\x06'
            # self.property.update(state=2)
            self.state = self.DongleState.BOOTLOADER
            self.get_response(RESET_SEQ, SPResponse(code=0, message="", data={}))

        elif "begin upload" in repr(data):
            logger.info(f"{name}, {mac}: Serial upload begin")
            # bootloader_upgrading_start_response(upgrading_start_sequence, self, {})
            # self.property.update(state=3)
            self.state = self.DongleState.UPGRADING
            self.get_response(UPGRADE_START_SEQ, SPResponse(code=0, message="", data={}))

        elif "Gecko Bootloader" in repr(data):
            logger.info(f"{name}, {mac}: Gecko Bootloader")
            # reset_bootloader_request_response(bootloader_sequence, self, {})
            # self.property.update(state=2)
            self.state = self.DongleState.BOOTLOADER
            self.get_response(BOOTLOADER_SEQ, SPResponse(code=0, message="", data={}))

        elif self.state in [self.DongleState.BOOTLOADER, self.DongleState.UPGRADING] and (
                b'\x04' in data or b'\x06' in data or b'\x15' in data or b'\x18' in data or b'C' in data):
            # self.property.update(state=3)
            # self.state = self.DongleState.UPGRADING
            self.flag = data
        else:
            self._data += data
            print('current serial data:')
            print(self._data)
            while True:
                if not self._data:
                    break
                index = self._data.find(unhexlify('AA55'))
                if index == -1:
                    logger.warning("incomplete package %s", repr(self._data))
                    break
                else:
                    package = self._data[index + 2:]
                    package_index = 0
                    command = decode_int(package[package_index:package_index + 2], 2, big=True)
                    package_index += 2
                    sequence = decode_int(package[package_index:package_index + 1], 1)
                    package_index += 1
                    payload_length = decode_int(package[package_index:package_index + 1], 1)
                    package_index += 1
                    payload = package[package_index: package_index + payload_length]
                    package_index += payload_length
                    crc = package[package_index:package_index + 2]
                    package_index += 2
                    self._data = self._data[index + 2 + package_index:]
                    # verify crc first
                    if not crc_verify(package[:package_index - 2], crc):
                        logger.error(f'crc verify failed:{repr(package[:package_index - 2])}, CRC:{crc}')
                    else:
                        logger.info(f"receive command:{hex(command)}")
                        sp = Global.get(command)
                        if not sp:
                            logger.warning(f'command {command} is not register')
                        else:
                            sp = sp()
                            sp.deserialize(self.mac, sequence, payload)

    def handle(self, message: Message, sender):
        tasks = Tasks()
        tasks.add(self._handle(message, sender))

    async def _handle(self, message, sender):
        """
        mqtt command handler
        :param message: data_model.Message
        :return:
        """
        request = None
        self._sender = sender
        try:
            if not isinstance(message.data, CommandDevice):
                try:
                    command = from_dict(data_class=CommandDevice, data=message.data)
                except Exception as e:
                    logger.exception("device handle error")
                    raise InvalidPayload(repr(e))
            else:
                command = message.data
            if command.firmware is not None:
                file = WiserFile(f'./firmwares/{command.firmware.filename}')
                # update Update class
                Upgrade(self, file, message)
            elif command.config is not None:
                SetConfig(self, message, command.config)
            elif command.get_config is not None:
                GetConfig(self, message)
            elif command.label is not None:
                request = self.pack_request(message=message,
                                            request=WriteLabel(command.label.data),
                                            response=self.response
                                            )
                await request.send()
                if request.result:
                    self.label = command.label.data
                    del request
                    request = None
            elif command.join is not None:
                # check channel list
                if not set(command.join.channels) <= set(list(range(11, 27))):
                    raise OutOfRange(command.join.channels, list(range(11, 27)))
                else:
                    channel_mask = 0
                    for item in command.join.channels:
                        channel_mask = channel_mask + (1 << item)
                # check pan id
                if command.join.pan_id is not None and command.join.pan_id not in range(0, 0x10000):
                    raise OutOfRange(command.join.pan_id, [0, 0xFFFF])
                # check extended pan id
                if command.join.extended_pan_id is not None and command.join.extended_pan_id not in range(0, 0x10000000000000000):
                    raise OutOfRange(command.join.pan_id, [0, 0xFFFFFFFFFFFFFFFF])

                request = self.pack_request(message=message,
                                            request=JoinNetwork(channel_mask, 0, command.join.pan_id, command.join.extended_pan_id),
                                            response=self.response
                                            )
                await request.send()
            elif command.leave is not None:
                request = self.pack_request(message=message,
                                            request=Leave(),
                                            response=self.response
                                            )
                await request.send()
            elif command.attribute is not None:
                if command.attribute.manufacturer and (command.attribute.manufacturer is None or command.attribute.manufacturer==0):
                    raise InvalidPayload('manufacturer_code invalid')
                if command.attribute.value is not None:
                    # write attribute
                    request = self.pack_request(message=message,
                                                request=WriteAttribute(
                                                    endpoint=command.attribute.endpoint,
                                                    cluster=command.attribute.cluster,
                                                    server=command.attribute.server,
                                                    attribute=command.attribute.attribute,
                                                    manufacturer_code=command.attribute.manufacturer_code if command.attribute.manufacturer else 0,
                                                    type=command.attribute.type,
                                                    value=command.attribute.value
                                                ),
                                                response=self.response)
                else:
                    # get attribute
                    request = self.pack_request(message=message,
                                                request=ReadAttribute(
                                                    endpoint=command.attribute.endpoint,
                                                    cluster=command.attribute.cluster,
                                                    server=command.attribute.server,
                                                    attribute=command.attribute.attribute,
                                                    manufacturer_code=command.attribute.manufacturer_code if command.attribute.manufacturer else 0
                                                ),
                                                response=self.response
                                                )
                await request.send()
            elif command.reset is not None:
                if self.state == self.DongleState.BOOTLOADER:
                    request = self.pack_request(message=message,
                                                sequence=RESET_SEQ,
                                                response=self.response,
                                                data=b'\x32'
                                                )
                else:
                    request = self.pack_request(message=message,
                                                request=Reset(),
                                                sequence=RESET_SEQ,
                                                response=self.response
                                                )
            elif command.identify is not None:
                request = self.pack_request(message=message,
                                            request=Identify(),
                                            response=self.response
                                            )
            elif command.data_request is not None:
                request = self.pack_request(message=message,
                                            request=DataRequest(),
                                            response=self.response
                                            )
            else:
                raise Unsupported(message.data)
            if request:
                await request.send()
        except InvalidPayload as e:
            e.uuid = message.uuid
            e.timestamp = message.timestamp
            self.send_error(sender, e.error)
        except Unsupported as e:
            e.uuid = message.uuid
            e.timestamp = message.timestamp
            self.send_error(sender, e.error)
        except OutOfRange as e:
            e.uuid = message.uuid
            e.timestamp = message.timestamp
            self.send_error(sender, e.error)
        except Exception as e:
            logger.exception("internal error:")
            self.send_error(sender, ErrorMessage(
                code=200,
                message='internal error',
                data={},
                timestamp=message.timestamp,
                uuid=message.uuid
            ))

    class Property:
        def __init__(self):
            self.ready = False
            self.boot = False
