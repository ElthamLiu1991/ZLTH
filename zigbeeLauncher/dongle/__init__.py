import asyncio
import platform
from multiprocessing import Pool
from threading import Thread

from zigbeeLauncher.logging import dongleLogger as logger
import serial
import serial.tools.list_ports
import serial_asyncio

from zigbeeLauncher.dongle.Dongle import Dongles
from zigbeeLauncher.dongle.Dongle import dongles, Dongles
from zigbeeLauncher.dongle.Serial import Serial
from zigbeeLauncher.dongle.Task import Tasks


async def serial_manager():
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
                    # 判断端口重名的问题
                    same_name = False
                    for key, value in dongles.items():
                        if name == value.property.port:
                            # logger.warning("%s, A same name dongle %s, already initial, "
                            #                "please check with your system manager", serial_number, name)
                            same_name = True
                            break
                    if same_name:
                        continue
                        # use coroutine
                    # tasks = Tasks()
                    # task = serial_asyncio.create_serial_connection(tasks.loop,
                    #                                                Serial,
                    #                                                name,
                    #                                                baudrate=460800)
                    # future = tasks.add(task)
                    tasks = Tasks()
                    try:
                        dongle = Dongles(serial_number, port.name)
                        dongles[serial_number] = dongle
                        transport, protocol = await serial_asyncio.create_serial_connection(tasks.loop,
                                                                                            Serial,
                                                                                            name,
                                                                                            baudrate=460800)
                        dongle.ready(protocol)
                        dongle.activated()
                    except serial.serialutil.SerialException:
                        logger.exception("Open serial {} failed".format(port.name))
                        if serial_number in dongles:
                            del dongles[serial_number]
            await asyncio.sleep(0.01)
        except Exception as e:
            logger.exception("Serial management error:%s", e)
            if serial_number in dongles:
                del dongles[serial_number]
        await asyncio.sleep(0.1)


def init():
    tasks = Tasks()
    tasks.add(serial_manager())
    return
