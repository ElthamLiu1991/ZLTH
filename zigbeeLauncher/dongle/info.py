from zigbeeLauncher.dongle.command import Request
from zigbeeLauncher.data_model import Message
from zigbeeLauncher.serial_protocol.sp_01 import GetZigbee, ZigbeeResponse
from zigbeeLauncher.serial_protocol.sp_f0 import GetInfo, GetLabel, GetState, InfoResponse, LabelResponse, StateResponse
from zigbeeLauncher.tasks import Tasks
from zigbeeLauncher.logging import dongleLogger as logger


class Info(Request):
    """
    初始化dongle, 读取configured, state, label, zigbee等信息
    重试次数：5次
    状态判断：如果dongle处于bootloader或者upgrade状态，直接返回默认数据
    超时判断：如果达到最大重试次数，直接返回默认数据

    """
    def __init__(self, dongle):
        super().__init__()
        self.dongle = dongle
        self.retry = 5

        # self.start()
        task = Tasks()
        task.add(self.start())

    def response(self, mac, uuid, timestamp, sp_response, sender):
        logger.info(f'response {mac}, {uuid}, {timestamp}, {sp_response}')
        if sp_response.code:
            self.finish()
        # self.dongle.send_info()

    def timeout(self, mac, sequence, uuid, timestamp):
        logger.warning(f'timeout {mac}, {uuid}, {timestamp}, {self.dongle.state}')
        if self.dongle.state in [self.dongle.DongleState.BOOTLOADER, self.dongle.DongleState.UPGRADING]:
            logger.warning(f'Get info timeout, dongle not ready: {self.dongle.name}, {self.dongle.mac}, {self.dongle.state}')
            self.dongle.cancel(sequence)
            self.finish()
        return

    def finish(self):
        self.dongle._ready = True
        self.dongle.send_info()

    async def start(self):
        """
        发送命令获取info，失败->结束，成功->下一个状态
        :return:
        """
        request = self.dongle.pack_request(
            request=GetInfo(),
            response=self.response,
            timeout=self.timeout,
            retry=self.retry
        )
        await request.send()

        if request.result:
            await self.get_label()

    async def get_label(self):
        request = self.dongle.pack_request(
            request=GetLabel(),
            response=self.response,
            timeout=self.timeout,
            retry=self.retry
        )
        await request.send()
        if request.result:
            await self.get_state()

    async def get_state(self):
        request = self.dongle.pack_request(
            request=GetState(),
            response=self.response,
            timeout=self.timeout,
            retry=self.retry
        )
        await request.send()
        if request.result:
            await self.get_network_state()

    async def get_network_state(self):
        request = self.dongle.pack_request(
            request=GetZigbee(),
            response=self.response,
            timeout=self.timeout,
            retry=self.retry
        )
        await request.send()
        if request.result:
            self.finish()