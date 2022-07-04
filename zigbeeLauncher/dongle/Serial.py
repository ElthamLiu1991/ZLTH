import time
from asyncio import transports, Protocol
from binascii import unhexlify, hexlify
from multiprocessing import Queue
from typing import Optional

from zigbeeLauncher.dongle.Task import Tasks
from zigbeeLauncher.logging import dongleLogger as logger


class Serial(Protocol):
    def __init__(self):
        self.queue = Queue(0) # buffer for store data from dongle
        self.transport = None
        self._exit = False
        self.received = None
        self.connected = None
        self.disconnected = None
        self._state = False

    def ready(self, received=None, connected=None, disconnected=None):
        self.received = received
        self.connected = connected
        self.disconnected = disconnected

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport
        logger.info("Port connected:%s", self.transport.serial.name)
        transport.serial.rts = False
        self._state = True
        if self.connected:
            self.connected()
        self.write('01')

    def connection_lost(self, exc: Optional[Exception]) -> None:
        logger.warning("Port disconnected:%s", self.transport.serial.name)
        self._state = False
        if self.disconnected:
            self.disconnected()

    def write(self, data):
        # self.now = time.time()
        if isinstance(data, bytes) or isinstance(data, bytearray):
            self.transport.write(data)
        else:
            self.transport.write(unhexlify(data))

    def data_received(self, data: bytes) -> None:
        """
        add data to serial receive queue
        :param data:
        :return:
        """
        # print('time consumption:', time.time()-self.now)
        if self.received:
            self.received(data)
        pass
