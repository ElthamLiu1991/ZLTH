import asyncio
import platform
import time
from binascii import unhexlify

import threading
import serial
import serial.tools.list_ports
import serial_asyncio

class Tasks():
    _instance = None
    _flag = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance=super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._flag:
            self._flag = True
            print("task loopp init")
            self.loop = asyncio.new_event_loop()  # 获取一个事件循环
            threading.Thread(target=self.run).start()

    def run(self) -> None:
        print("run task loop")
        _run = True
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def add(self, task):
        return asyncio.run_coroutine_threadsafe(
            task, self.loop
        )


class Output(asyncio.Protocol):
    time_diff = 0

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False
        #self.write(1)
        for i in range(10):
            self.write(1)

    def write(self, data):
        self.time_diff = time.time()
        self.transport.write(unhexlify('AA55F0040200EF25'))

    def data_received(self, data):
        print("receive data:", time.time()-self.time_diff)

    def connection_lost(self, exc):
        print('port closed')
        asyncio.get_event_loop().stop()

dongles = {}

async def get_dongles():
    while True:
        try:
            new_port_list = list(serial.tools.list_ports.comports())
            for port in new_port_list:
                if not port.serial_number or len(port.serial_number) < 5 or port.serial_number[:5] != "ZLTH_":
                    continue
                serial_number = port.serial_number[5:]
                if serial_number not in dongles:
                    # ports.append(port.name)
                    # logger.info("Found a new port:%s, %s", port.name, port.serial_number)
                    if platform.system() != "Windows":
                        name = '/dev/' + port.name
                    else:
                        name = port.name
                    tasks = Tasks()
                    try:
                        transport, protocol = await serial_asyncio.create_serial_connection(tasks.loop,
                                                                                            Output,
                                                                                            name,
                                                                                            baudrate=460800)
                        dongles[serial_number] = protocol
                    except serial.serialutil.SerialException:
                        print("Open serial {} failed".format(port.name))
                        if serial_number in dongles:
                            del dongles[serial_number]
            await asyncio.sleep(0.001)
        except Exception as e:
            print("Serial management error:", e)
            if serial_number in dongles:
                del dongles[serial_number]

        await asyncio.sleep(0.01)

tasks = Tasks()
tasks.add(get_dongles())
time.sleep(5)
while True:
    print('write data:')
    for mac, dongle in dongles.items():
        dongle.write(1)
    time.sleep(2)