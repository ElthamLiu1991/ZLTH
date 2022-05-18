import time

from zigbeeLauncher.serial_protocol.SerialProtocol02 import endpoint_list_request_handle, \
    endpoint_descriptor_request_handle
from zigbeeLauncher.serial_protocol.SerialProtocolF0 import *
from zigbeeLauncher.serial_protocol.SerialProtocol01 import *
from . import set_value, get_value
from .WiserZigbeeDongleCommands import Command, send_command
from zigbeeLauncher.logging import dongleLogger as logger


class Info:
    def __init__(self, dongle, callback):
        self.dongle = dongle
        self.callback = callback
        self.info = {"name": dongle.port, "mac": dongle.name}
        self.retry = 0
        self.counter = 0
        self.start()

    def start(self):
        pending = get_value('pending')
        if self.dongle.name not in pending:
            logger.info("add %s to info queue", self.dongle.name)
            pending[self.dongle.name] = self
            set_value('pending', pending)
        if len(pending) == 1:
            self.get_info()

    def timeout(self, device, timestamp, uuid):
        if self.dongle.state != 2 and self.dongle.state != 3:
            if self.retry < 5:
                logger.warn('%s, %s:Get info timeout, retry:%d', self.dongle.port, self.dongle.name, self.retry)
                time.sleep(1)
                self.retry = self.retry + 1
                # retry next time
                # self.get_info()
                pending = get_value('pending')
                for info in pending:
                    if pending[info].retry < self.retry:
                        # go with this device
                        pending[info].get_info()
                        return
                # start next loop
                for info in pending:
                    pending[info].get_info()
                    break
            else:
                logger.error('Get info failed')
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
                pending = get_value('pending')
                del pending[self.dongle.name]
                set_value('pending', pending)
                for info in pending:
                    pending[info].get_info()
                    return

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
            pending = get_value('pending')
            del pending[self.dongle.name]
            set_value('pending', pending)
            for info in pending:
                pending[info].get_info()
                return

    def response(self, device, userdata):
        if 'descriptor' not in userdata:
            self.info = dict(**self.info, **userdata)
        else:
            if 'endpoints' not in self.info['zigbee']:
                self.info['zigbee']['endpoints'] = [userdata['descriptor']]
            else:
                self.info['zigbee']['endpoints'].append(userdata['descriptor'])

    def finish(self):
        if self.callback:
            self.callback(self.dongle.name, self.info)
        pending = get_value('pending')
        del pending[self.dongle.name]
        set_value('pending', pending)
        for info in pending:
            pending[info].get_info()
            return

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
            done=self.get_network_state))

    def get_network_state(self):
        send_command(Command(
            dongle=self.dongle,
            request=network_status_request_handle,
            response=self.response,
            timeout=self.timeout,
            done=self.get_endpoint_list))

    def get_endpoint_list(self):
        send_command(Command(
            dongle=self.dongle,
            request=endpoint_list_request_handle,
            response=self.response,
            timeout=self.timeout,
            done=self.get_endpoint_descriptor))

    def get_endpoint_descriptor(self):
        for endpoint in self.info['endpoint']:
            send_command(Command(
                dongle=self.dongle,
                request=endpoint_descriptor_request_handle,
                response=self.response,
                timeout=self.timeout,
                done=self.counting), payload=endpoint)

    def counting(self):
        self.counter = self.counter + 1
        if self.counter == len(self.info['endpoint']):
            print("descriptor finish")
            del self.info['endpoint']
            self.finish()