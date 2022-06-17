import platform
from threading import Thread

from zigbeeLauncher.logging import dongleLogger as logger
import serial
import serial.tools.list_ports
import serial_asyncio

from zigbeeLauncher.dongle.Dongle import Dongles
from zigbeeLauncher.dongle.Dongle import dongles, Dongles
from zigbeeLauncher.dongle.Serial import Serial
from zigbeeLauncher.dongle.Task import Tasks
from zigbeeLauncher.mqtt import set_value


def serial_management():
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
                    # use coroutine
                    tasks = Tasks()
                    task = serial_asyncio.create_serial_connection(tasks.loop,
                                                                   Serial,
                                                                   name,
                                                                   baudrate=460800)
                    future = tasks.add(task)
                    # 保存name:serial_number, future元组到ports
                    try:
                        dongle = Dongles(serial_number, port.name)
                        protocol = future.result()[1]
                        dongle.ready(protocol)
                        dongles[serial_number] = dongle
                        dongle.activated()
                    except serial.serialutil.SerialException as e:
                        # logger.exception("Open serial {} failed".format(port.name))
                        pass
                    # use multi-threading
                    # dongle = Dongles(serial_number, port.name)
                    # if dongle.isReady(port.name):
                    #     dongles[serial_number] = dongle
                    #     dongle.activated()
        except Exception as e:
            logger.exception("Serial management error:%s", e)


def init():
    thread = Thread(target=serial_management)
    thread.start()
    set_value('dongle', True)
    return
