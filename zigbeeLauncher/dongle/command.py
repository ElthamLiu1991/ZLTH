import abc
import asyncio
from binascii import hexlify

from zigbeeLauncher.logging import dongleLogger as logger
from zigbeeLauncher.serial_protocol.sp import SPResponse


class Request:
    def __init__(self):
        pass

    @abc.abstractmethod
    def response(self, mac, uuid, timestamp, sp_response:SPResponse, sender):
        """
        command response handler
        :param mac: dongle mac address
        :param uuid: message uuid
        :param timestamp: message timestamp
        :param sp_response: serial protocol response
        :param sender: who send this command
        :return:
        """
        pass

    @abc.abstractmethod
    def timeout(self, mac, sequence, uuid, timestamp):
        """
        request timeout handle, may call multiple times if retry > 1
        :param mac: dongle mac address
        :param sequence: command sequence
        :param uuid: message uuid
        :param timestamp: message timestamp
        :return:
        """
        pass


class Command:
    def __init__(self, mac, serial, sequence, uuid, timestamp, sender):
        self.mac = mac
        self.serial = serial
        self.uuid = uuid
        self.timestamp = timestamp
        self.sender = sender
        self._sequence = sequence

        self.retry = 0
        self._done = False
        self._cancel = False
        self._result = False
        self._data = None

        self._request = None
        self.response = None
        self.timeout = None

    def ready(self, request=None, response=None, timeout=None, retry=3, data=None):
        """
        pack command call back handler
        :param request: serial request API
        :param response: user response callback
        :param timeout: user timeout callback
        :param retry: retry setting
        :param data: request data ready to send
        :return:
        """
        self._request = request
        self.response = response
        self.timeout = timeout
        self.retry = retry
        self._data = data

    async def send(self, *args, **kwargs):
        logger.info(f'pack request, {self._sequence}, {args}, {kwargs}')
        # self._data = self._request(self._sequence, *args, **kwargs)
        if not self._data:
            self._data = self._request.serialize(self._sequence)
        await self._send()
    
    def cancel(self):
        self.retry = 0
        self._cancel = True
        self._done = True

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, request):
        self._request = request

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, sequence):
        self._sequence = sequence
        
    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, sp_response:SPResponse):
        """
        serial response, call user response callback
        :param sp: serial response instance
        :return:
        """
        self._done = True
        self._result = True if sp_response.code == 0 else False

        if self.response:
            self.response(self.mac, self.uuid, self.timestamp, sp_response, self.sender)

    @property
    def result(self):
        return self._result

    async def _send(self):
        self.serial(self._data)
        try:
            await asyncio.wait_for(self._waiting(), timeout=5)
        except asyncio.TimeoutError:
            logger.error(f'serial request timeout, {self.mac}, {self._sequence}, {self.uuid}, {self.timestamp}, {self.request}')
            if not self._cancel and self.timeout:
                self.timeout(self.mac, self._sequence, self.uuid, self.timestamp)
                await self._retry()
        return True

    async def _retry(self):
        self.retry -= 1
        if self.retry:
            logger.warning(f'resend, remain:{self.retry}')
            await self._send()
        else:
            # response false
            logger.error(f'command timeout, {self.mac}, {self._sequence}, {self.uuid}, {self.timestamp}, {self.request}')
            self._result = False
            if not self._cancel and self.response:
                response = SPResponse(200, "timeout")
                self.response(self.mac, self.uuid, self.timestamp, response, self.sender)

    async def _waiting(self):
        if self._done:
            await asyncio.sleep(0.01)
        while not self._done:
            await asyncio.sleep(0.01)
        return
