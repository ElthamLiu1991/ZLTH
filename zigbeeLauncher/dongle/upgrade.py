import asyncio

from zigbeeLauncher.dongle.command import Request
from zigbeeLauncher.data_model import ErrorMessage
from zigbeeLauncher.exceptions import NotFound
from zigbeeLauncher.serial_protocol.sp_01 import Leave
from zigbeeLauncher.serial_protocol.sp_f0 import EnterBootloader, BOOTLOADER_SEQ, RESET_SEQ, UPGRADE_START_SEQ
from zigbeeLauncher.tasks import Tasks
from zigbeeLauncher.dongle.info import Info
from zigbeeLauncher.serial_protocol.serial_protocol_F0 import *
from zigbeeLauncher.serial_protocol.serial_protocol_01 import *
from zigbeeLauncher.dongle.xmodem import XMODEM


class Upgrade(Request):
    def __init__(self, dongle, file, message):
        super(Request, self).__init__()
        self.dongle = dongle
        self.file = file
        self.message = message
        self.retry = 5

        self.percentage = -1
        self.counter = len(file.data) / 128

        task = Tasks()
        task.add(self.start())

    def response(self, mac, uuid, timestamp, response, sender):
        logger.info(f'response {mac}, {uuid}, {timestamp}, {response}')
        # broadcast error

    def timeout(self, mac, sequence, uuid, timestamp):
        logger.warning(f'timeout {mac}, {sequence}, {uuid}, {timestamp}')

    async def getc(self, size, timeout=1):
        """
        异步串口读取函数，配合异步Xmodem一起使用
        :param size:
        :param timeout:
        :return:
        """
        while True:
            if self.dongle.flag:
                print('getc: ', self.dongle.flag)
                data = self.dongle.flag
                self.dongle.flag = None
                return data
            await asyncio.sleep(0.001)

    def update_process(self, total_packets, success_count, error_count):
        percentage = success_count * 100 // self.counter
        if percentage % 10 == 0 and self.percentage != percentage:
            logger.info("Total %d, success:%d, percentage: %d", self.counter, success_count, percentage)
            # call update process
            self.percentage = percentage
            self.dongle.send_update({"process": percentage})

    async def start(self):
        """
        leave network
        :return:
        """
        if self.dongle.state == self.dongle.DongleState.BOOTLOADER:
            await self.enter_upgrade_mode()
        elif self.dongle.state == self.dongle.DongleState.UPGRADING:
            await self.transfer()
        else:
            request = self.dongle.pack_request(
                message=self.message,
                request=Leave(),
                response=self.response,
                timeout=self.timeout,
                retry=self.retry
            )
            await request.send()
            if request.result:
                await self.enter_bootloader_mode()

    async def enter_bootloader_mode(self):
        """
        enter bootloader mode
        :return:
        """
        if self.dongle.state == self.dongle.DongleState.UPGRADING:
            logger.info(f'dongle is in upgrading mode')
        else:
            request = self.dongle.pack_request(
                message=self.message,
                sequence=BOOTLOADER_SEQ,
                request=EnterBootloader(),
                response=self.response,
                timeout=self.timeout
            )
            await request.send()
            if request.result:
                await self.enter_upgrade_mode()
            else:
                logger.error(f'enter bootloader mode failed')

    async def enter_upgrade_mode(self):
        if self.dongle.state == self.dongle.DongleState.UPGRADING:
            logger.info(f'dongle is in upgrading mode')
        else:
            request = self.dongle.pack_request(
                message=self.message,
                sequence=UPGRADE_START_SEQ,
                response=self.response,
                timeout=self.timeout,
                data=b'\x31'
            )
            await request.send()
            if request.result:
                await self.transfer()
            else:
                logger.error(f'enter upgrading mode failed')

    async def transfer(self):
        try:
            logger.info("start transfer")
            modem = XMODEM(self.getc, self.dongle.write)
            await modem.send(self.file, callback=self.update_process)
            # tasks = Tasks()
            # await tasks.loop.run_in_executor(None, modem.send, self.file, 16, 60, False, self.update_process)
            while self.dongle.state != self.dongle.DongleState.BOOTLOADER:
                await asyncio.sleep(0.01)
            self.dongle.boot = False
            request = self.dongle.pack_request(
                message=self.message,
                sequence=RESET_SEQ,
                response=self.response,
                data=b'\x32'
            )
            await request.send()
            if not request.result:
                logger.error('reboot error')
                return
            await self.enter_normal()
            # self.dongle.boot = False
        except TypeError:
            logger.warn(f"{self.dongle.name}, {self.dongle.mac} upgrade failed")

    async def enter_normal(self):
        logger.info(f'initial dongle:{self.dongle.name}, {self.dongle.mac}')
        self.dongle.state = self.dongle.DongleState.UN_COMMISSIONED
        while not self.dongle.boot:
            await asyncio.sleep(0.5)
        # if not self.dongle.boot:
        #     logger.warn("failed to enter upgrading mode: %s", self.dongle.mac)
        #     return

        # self.dongle.property.update(state=1)
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
            raise NotFound(self.file)

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
