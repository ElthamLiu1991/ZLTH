import threading
import time

from zigbeeLauncher.dongle.Info import Info
from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.mqtt.Callbacks import dongle_info_callback, dongle_error_callback, dongle_update_callback
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *
from xmodem import XMODEM


class Upgrade:
    def __init__(self, dongle, file, timestamp=0, uuid=''):
        self.dongle = dongle
        self.file = file
        self.timestamp = timestamp
        self.uuid = uuid
        self.state = self.dongle.property.state
        self.percentage = -1
        self.counter = len(file.data) / 128

        self.start()

    def response(self, **kwargs):
        if kwargs['code'] != 0:
            self.finish(**kwargs)

    def finish(self, **kwargs):
        dongle_error_callback(**kwargs)

    def getc(self, size, timeout=1):
        while True:
            if self.dongle.flag:
                data = self.dongle.flag
                self.dongle.flag = None
                return data
            time.sleep(0.001)

    def update_process(self, total_packets, success_count, error_count):
        percentage = success_count * 100 // self.counter
        if percentage % 10 == 0 and self.percentage != percentage:
            logger.info("Total %d, success:%d, percentage: %d", self.counter, success_count, percentage)
            # call update process
            self.percentage = percentage
            dongle_update_callback(self.dongle.property.mac, {"process": percentage})

    def start(self):
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
            if not command.send().result():
                pass
        self.enter_bootloader_mode()

    def enter_bootloader_mode(self):
        """
        enter bootloader mode
        :return:
        """
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=reset_bootloader_request_handle,
            sequence=bootloader_sequence
        )

        if not command.send().result():
            return
        self.enter_upgrade_mode()

    def enter_upgrade_mode(self):
        command = self.dongle.request(
            timestamp=self.timestamp,
            uuid=self.uuid,
            response_cb=self.response,
            request_cb=bootloader_upgrading_start_handle,
            sequence=upgrading_start_sequence
        )

        if not command.send().result():
            return
        self.transfer()

    def transfer(self):
        try:
            modem = XMODEM(self.getc, self.dongle.write)
            status = modem.send(self.file, callback=self.update_process)
            command = self.dongle.request(
                timestamp=self.timestamp,
                uuid=self.uuid,
                response_cb=self.response,
                request_cb=bootloader_upgrading_finish_transfer,
                sequence=upgrading_finish_sequence
            )
            self.dongle.property.boot = False
            if not command.send().result():
                return
            self.enter_normal()
        except TypeError:
            logger.warn("%s, %s upgrade failed", self.dongle.property.port, self.dongle.property.mac)
            self.finish(device=self.dongle.property.mac,
                        code=10001,
                        message='upgrade failed',
                        payloa={},
                        timestamp=self.timestamp,
                        uuid=self.uuid)

    def enter_normal(self):
        now = time.time()
        while not self.dongle.property.boot:
            if time.time() - now > 5:
                logger.error("dongle %s reboot timeout", self.dongle.property.mac)
                return
        self.dongle.property.update(state=1)
        threading.Thread(target=Info, args=(self.dongle,)).start()


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
