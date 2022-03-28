import time

from .WiserZigbeeLauncherSerialProtocol import info_request_handle, \
    state_request_handle, label_request_handle
from .WiserZigbeeDongleCommands import Command, send_command
from zigbeeLauncher.logging import dongleLogger as logger


class Info:
    def __init__(self, dongle, callback):
        self.dongle = dongle
        self.callback = callback
        self.info = {"name": dongle.port, "mac": dongle.name}
        self.get_info()
        self.retry = 0

    def timeout(self, device, timestamp, uuid):
        if self.dongle.state == 1:
            if self.retry < 10:
                logger.warn('%s, %s:Get info timeout, retry:%d', self.dongle.port, self.dongle.name, self.retry)
                time.sleep(1)
                self.retry = self.retry + 1
                self.get_info()
            else:
                logger.error('Get info failed')
        else:
            if self.callback:
                self.callback(self.dongle.name, {
                    "name": self.dongle.port,
                    "mac": self.dongle.name,
                    "connected": True,
                    "swversion": '0',
                    "hwversion": '0',
                    "label": '',
                    "state": self.dongle.state,
                    "configured": 0
                })

    def response(self, device, userdata):
        self.info.update(userdata)
        logger.info(self.info)

    def call_callback(self):
        if self.callback:
            self.callback(self.dongle.name, self.info)

    def get_info(self):
        """
        发送命令获取info，失败->结束，成功->下一个状态
        :return:
        """
        send_command(Command(
            dongle=self.dongle,
            request=info_request_handle,
            response=self.response,
            timeout=self.timeout,
            done=self.get_label))

    def get_label(self):
        send_command(Command(
            dongle=self.dongle,
            request=label_request_handle,
            response=self.response,
            timeout=self.timeout,
            done=self.get_state))

    def get_state(self):
        send_command(Command(
            dongle=self.dongle,
            request=state_request_handle,
            response=self.response,
            timeout=self.timeout,
            done=self.call_callback))
