import threading

from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.mqtt.Callbacks import dongle_info_callback
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *


class Info:
    """
    初始化dongle, 读取configured, state, label, zigbee等信息
    重试次数：5次
    状态判断：如果dongle处于bootloader或者upgrade状态，直接返回默认数据
    超时判断：如果达到最大重试次数，直接返回默认数据

    """
    def __init__(self, dongle):
        self.dongle = dongle
        self.retry = 0
        self.retry_max = 5
        self.start()

    def timeout(self, **kwargs):
        state = self.dongle.property.state
        if state == 2 or state == 3:
            logger.warn('%s, %s:Get info timeout, state:%d',
                        self.dongle.property.port, self.dongle.property.mac, self.dongle.property.state)
            self.finish(payload=self.dongle.property.default())
        else:
            if self.retry < self.retry_max:
                self.retry = self.retry + 1
                if kwargs['callback']:
                    threading.Thread(target=kwargs['callback']).start()
            else:
                # timeout
                logger.warn('%s, %s:Get info timeout',
                            self.dongle.property.port, self.dongle.property.mac)
                self.finish(payload=self.dongle.property.default())

    def response(self, **kwargs):
        if kwargs['code'] != 0:
            self.finish(**kwargs)

    def finish(self, payload={}, **kwargs):
        dongle_info_callback(self.dongle.property.mac, payload, **kwargs)
        self.dongle.property.ready = True

    def start(self):
        """
        发送命令获取info，失败->结束，成功->下一个状态
        :return:
        """
        command = self.dongle.request(
            response_cb=self.response,
            timeout_cb=self.timeout,
            request_cb=info_request_handle,
            retry=self.start
        )

        if not command.send().result():
            return
        self.get_label()

    def get_label(self):
        command = self.dongle.request(
            response_cb=self.response,
            timeout_cb=self.timeout,
            request_cb=label_request_handle,
            retry=self.get_label
        )

        if not command.send().result():
            return
        self.get_state()

    def get_state(self):
        command = self.dongle.request(
            response_cb=self.response,
            timeout_cb=self.timeout,
            request_cb=state_request_handle,
            retry=self.get_state
        )

        if not command.send().result():
            return
        self.get_network_state()

    def get_network_state(self):
        command = self.dongle.request(
            response_cb=self.response,
            timeout_cb=self.timeout,
            request_cb=network_status_request_handle,
            retry=self.get_network_state
        )

        if not command.send().result():
            return
        self.finish(payload=self.dongle.property.get())