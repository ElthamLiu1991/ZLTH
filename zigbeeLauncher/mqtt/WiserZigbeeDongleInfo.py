import time

from zigbeeLauncher.serial_protocol.SerialProtocol02 import endpoint_list_request_handle, \
    endpoint_descriptor_request_handle
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *
from . import set_value, get_value
from .WiserZigbeeDongleCommands import Command, send_command
from zigbeeLauncher.logging import dongleLogger as logger


class Info:
    """
    初始化dongle, 读取configured, state, label, zigbee等信息
    重试次数：5次
    状态判断：如果dongle处于bootloader或者upgrade状态，直接返回默认数据
    超时判断：如果达到最大重试次数，直接返回默认数据

    """
    def __init__(self, dongle, callback):
        self.dongle = dongle
        self.callback = callback
        self.info = {"name": dongle.port, "mac": dongle.name}
        self.retry = 0
        self.counter = 0
        self.get_info()

    def start(self):
        pending = get_value('pending')
        if self.dongle.name not in pending:
            logger.info("add %s to info queue", self.dongle.name)
            pending[self.dongle.name] = self
            set_value('pending', pending)
        if len(pending) == 1:
            self.get_info()

    def timeout(self, device, timestamp, uuid):
        state = self.dongle.new_state
        if state == 2 or state == 3 or self.retry > 4:
            logger.warn('%s, %s:Get info timeout, state:%d, retry:%d',
                        self.dongle.port, self.dongle.name, self.dongle.new_state, self.retry)
            if self.callback:
                self.callback(self.dongle.name, {
                    "name": self.dongle.port,
                    "mac": self.dongle.name,
                    "connected": True,
                    "swversion": '0',
                    "hwversion": '0',
                    "label": '',
                    "state": self.dongle.new_state,
                    "configured": 0
                })
                self.dongle.ready = True
        else:
            time.sleep(0.1)
            self.retry = self.retry + 1

    def response(self, device, userdata):
        # self.info = dict(**self.info, **userdata)
        self.info.update(**userdata)

    def finish(self):
        if self.callback:
            if 'code' in self.info:
                del self.info['code']
            if 'message' in self.info:
                del self.info['message']
            if 'response' in self.info:
                del self.info['response']
            self.callback(self.dongle.name, self.info)
        self.dongle.ready = True

    def get_info(self):
        """
        发送命令获取info，失败->结束，成功->下一个状态
        :return:
        """
        send_command(Command(
            dongle=self.dongle,
            request=info_request_handle,
            done=self.get_label,
            response=self.response,
            timeout=self.timeout,
        ))

    def get_label(self):
        send_command(Command(
            dongle=self.dongle,
            request=label_request_handle,
            done=self.get_state,
            response=self.response,
            timeout=self.timeout,
        ))

    def get_state(self):
        send_command(Command(
            dongle=self.dongle,
            request=state_request_handle,
            done=self.get_network_state,
            response=self.response,
            timeout=self.timeout,
        ))

    def get_network_state(self):
        send_command(Command(
            dongle=self.dongle,
            request=network_status_request_handle,
            done=self.finish,
            response=self.response,
            timeout=self.timeout,
        ))