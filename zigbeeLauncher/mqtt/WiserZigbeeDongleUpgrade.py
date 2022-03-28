import asyncio
import random
import time
from threading import Thread

from xmodem import XMODEM

from .WiserZigbeeDongleInfo import Info
from .WiserZigbeeLauncherSerialProtocol import reset_bootloader_request_handle, \
    info_request_handle
from .WiserZigbeeDongleCommands import Command, send_command, commands
from .WiserZigbeeGlobal import get_value
from zigbeeLauncher.logging import dongleLogger as logger


def bootloader_start_transfer(payload=None):
    return 1001, "31"


def bootloader_start_transfer_response(device):
    if (1001, device) in commands:
        commands[(1001, device)].get_response(0)


def bootloader_finish_transfer(payload=None):
    return 0x80, "32"


def bootloader_stop_transfer(payload=None):
    return 1003, "32"


def bootloader_stop_transfer_response(device):
    if (1003, device) in commands:
        commands[(1003, device)].get_response(0)


class Upgrade:
    def __init__(self, dongle, file):
        self.dongle = dongle
        self.file = file
        self.counter = len(file.data)/128
        self.percentage = -1
        self.done = False
        self.enter_bootloader()
        self.retry = 0

    def enter_bootloader(self):
        # if device already in bootloader mode, stop current transfer first
        logger.info("%s, %s:Entering bootloader...", self.dongle.port, self.dongle.name)
        send_command(Command(
            dongle=self.dongle,
            request=reset_bootloader_request_handle,
            timeout=self.enter_bootloader_timeout,
            done=self.start_transfer))

    def start_transfer(self):
        logger.info("%s, %s:Starting transfer...", self.dongle.port, self.dongle.name)
        send_command(Command(
            dongle=self.dongle,
            request=bootloader_start_transfer,
            timeout=self.enter_bootloader_timeout,
            done=self.transfer))

    def xmodem_transfer(self):
        try:
            modem = XMODEM(self.getc, self.dongle.transport.write)
            status = modem.send(self.file, callback=self.callback)
            send_command(Command(
                dongle=self.dongle,
                request=bootloader_finish_transfer,
                done=self.enter_normal))
        except TypeError:
            logger.warn("%s, %s upgrade failed", self.dongle.port, self.dongle.name)

    def transfer(self):
        t = Thread(target=self.xmodem_transfer)
        t.start()

    def enter_normal(self):
        logger.info("%s, %s:Entering normal", self.dongle.port, self.dongle.name)
        time.sleep(2)
        Info(self.dongle, get_value("dongle_info_callback"))

    def enter_bootloader_timeout(self, device, timestamp, uuid):
        logger.warn("%s, %s:Upgrade timeout, retry:%d", self.dongle.port, self.dongle.name, self.retry)
        self.retry = self.retry + 1
        if self.retry < 10:
            self.enter_bootloader()
        else:
            logger.error("%s, %s:Upgrade timeout, notify to launcher", self.dongle.port, self.dongle.name)

    def getc(self, size, timeout=1):
        while True:
            if self.dongle.flag:
                data = self.dongle.flag
                self.dongle.flag = None
                return data
            time.sleep(0.001)

    def callback(self, total_packets, success_count, error_count):
        # upgrade percentage
        percentage = success_count * 100 // self.counter
        if percentage % 10 == 0 and self.percentage != percentage:
            logger.info("Total %d, success:%d, percentage: %d", self.counter, success_count, percentage)
            # call update process
            self.percentage = percentage
            if get_value("update_callback"):
                get_value("update_callback")(self.dongle.name, {"process": percentage})


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
        elif self.offset+size >= self.length:
            content = self.data[self.offset:]
            self.offset = self.length
        else:
            content = self.data[self.offset:self.offset+size]
            self.offset = self.offset+size
        return content