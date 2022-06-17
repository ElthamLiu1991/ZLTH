import threading
from binascii import unhexlify
from multiprocessing import Queue

import serial
from zigbeeLauncher.logging import dongleLogger as logger


class Serial(threading.Thread):
    def __init__(self, port, received=None, connected=None, disconnected=None):
        threading.Thread.__init__(self)
        self.port = port
        self.received = received
        self.connected = connected
        self.disconnected = disconnected
        # self.queue = Queue(0)  # buffer for store data from dongle
        self._exit = False
        self._serial = None
        self._max_read_size = 256
        self._state = False
        self._open()

    def _open(self):
        try:
            self._serial = serial.Serial(self.port, 460800, timeout=0.000001)
            if self._serial.isOpen():
                self._state = True
                if self.connected:
                    self.connected()
                return
            else:
                logger.error("open dongle %s failed", self.port)
        except serial.SerialException as e:
            logger.exception("open dongle %s failed", self.port)
        self._state = False

    def run(self):
        while not self._exit:
            try:
                data = self._serial.read(self._max_read_size)
            except serial.SerialException as e:
                self._state = False
                self._serial.close()
                logger.exception('read dongle %s failed', self.port)
                if self.disconnected:
                    self.disconnected()
                return
            else:
                if data and self.received:
                    self.received(data)
        print("exit dongle serial")

    def write(self, data):
        try:
            if isinstance(data, bytes):
                self._serial.write(data)
            else:
                self._serial.write(unhexlify(data))
        except serial.SerialException as e:
            self._state = False
            self._serial.close()
            logger.exception('write dongle %s failed', self.port)
            return False
        return True

    def stop(self):
        self._exit = True

    def is_open(self):
        return self._state
