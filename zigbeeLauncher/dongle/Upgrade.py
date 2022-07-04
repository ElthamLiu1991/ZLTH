import asyncio
import threading
import time
from multiprocessing import Process

from zigbeeLauncher.dongle.Task import Tasks
from zigbeeLauncher.dongle.Info import Info
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.mqtt.Callbacks import dongle_info_callback, dongle_error_callback, dongle_update_callback
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *
# from xmodem import XMODEM
from .Xmodem import XMODEM


class Upgrade:
    def __init__(self, dongle, file, timestamp=0, uuid=''):
        self.dongle = dongle
        self.file = file
        self.timestamp = timestamp
        self.uuid = uuid
        self.state = self.dongle.property.state
        self.percentage = -1
        self.counter = len(file.data) / 128

        task = Tasks()
        task.add(self.start())

    def response(self, **kwargs):
        if kwargs['code'] != 0:
            self.finish(**kwargs)

    def finish(self, **kwargs):
        dongle_error_callback(**kwargs)

    async def getc(self, size, timeout=1):
        """
        异步串口读取函数，配合异步Xmodem一起使用
        :param size:
        :param timeout:
        :return:
        """
        while True:
            if self.dongle.flag:
                data = self.dongle.flag
                self.dongle.flag = None
                return data
            await asyncio.sleep(0.001)
    # def getc(self, size, timeout=1):
    #     while True:
    #         if self.dongle.flag:
    #             data = self.dongle.flag
    #             self.dongle.flag = None
    #             return data
    #         time.sleep(0.001)

    def update_process(self, total_packets, success_count, error_count):
        percentage = success_count * 100 // self.counter
        if percentage % 10 == 0 and self.percentage != percentage:
            logger.info("Total %d, success:%d, percentage: %d", self.counter, success_count, percentage)
            # call update process
            self.percentage = percentage
            dongle_update_callback(self.dongle.property.mac, {"process": percentage})

    async def start(self):
        """
        leave network
        :return:
        """
        if self.state == 2 or self.state == 3:
            pass
        else:
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                request_cb=leave_network_request_handle
            )
            result = await command.send()
            if not result:
                return
        await self.enter_bootloader_mode()

    async def enter_bootloader_mode(self):
        """
        enter bootloader mode
        :return:
        """
        if self.state == 3:
            pass
        else:
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=reset_bootloader_request_handle,
                sequence=bootloader_sequence,
                timeout=4
            )
            result = await command.send()
            if not result:
                logger.warn("failed to enter bootloader mode: %s", self.dongle.property.mac)
                return
        await self.enter_upgrade_mode()

    async def enter_upgrade_mode(self):
        if self.state == 3:
            pass
        else:
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=bootloader_upgrading_start_handle,
                sequence=upgrading_start_sequence,
                timeout=2
            )
            result = await command.send()
            if not result:
                logger.warn("failed to enter upgrading mode: %s", self.dongle.property.mac)
                return
        await self.transfer()

    async def transfer(self):
        try:
            modem = XMODEM(self.getc, self.dongle.write)
            await modem.send(self.file, callback=self.update_process)
            # tasks = Tasks()
            # await tasks.loop.run_in_executor(None, modem.send, self.file, 16, 60, False, self.update_process)
            while self.dongle.property.state != 2:
                await asyncio.sleep(0.01)
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=bootloader_upgrading_finish_transfer,
                sequence=upgrading_finish_sequence,
                timeout=4
            )
            self.dongle.property.boot = False
            result = await command.send()
            if not result:
                return
            self.enter_normal()
        except TypeError:
            logger.warn("%s, %s upgrade failed", self.dongle.property.port, self.dongle.property.mac)

    def enter_normal(self):
        if not self.dongle.property.boot:
            logger.warn("failed to enter upgrading mode: %s", self.dongle.property.mac)
            return

        self.dongle.property.update(state=1)
        # retrieve dongle info
        info = Info(self.dongle)


class WiserFile:
    def __init__(self, file):
        self.offset = 0
        self.file = file
        self.length = 0
        self.data = None
        self.get_file()

    def get_file(self):
        try:
            with open(self.file, 'rb') as f:
                self.data = f.read()
                self.length = len(self.data)
        except FileNotFoundError:
            logger.warn("File not found:%s", self.file)

    def read(self, size):
        if self.offset == self.length:
            return None
        elif self.offset + size >= self.length:
            content = self.data[self.offset:]
            self.offset = self.length
        else:
            content = self.data[self.offset:self.offset + size]
            self.offset = self.offset + size
        return content
