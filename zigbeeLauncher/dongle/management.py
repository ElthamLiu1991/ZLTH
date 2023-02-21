import asyncio
import platform
from zigbeeLauncher.logging import dongleLogger as logger
import serial
import serial.tools.list_ports
import serial_asyncio

from zigbeeLauncher.dongle.dongle import Dongle
from zigbeeLauncher.dongle.serial import Serial
from zigbeeLauncher.tasks import Tasks
from zigbeeLauncher.util import Global


async def serial_manager():
    while True:
        try:
            new_port_list = list(serial.tools.list_ports.comports())
            for port in new_port_list:
                dongles = Global.get(Global.DONGLES)
                # 判断串口设备是否为ZLTH dongle
                if not port.serial_number or len(port.serial_number) < 5 or port.serial_number[:5] != "ZLTH_":
                    continue
                mac = port.serial_number[5:]
                if mac not in dongles:
                    # ports.append(port.name)
                    # logger.info("Found a new port:%s, %s", port.name, port.mac)
                    if platform.system() != "Windows":
                        name = '/dev/' + port.name
                    else:
                        name = port.name
                    # 判断端口重名的问题
                    same = False
                    for _, dongle in dongles.items():
                        if name == dongle.name:
                            logger.error(f'found a same name serial device {name}, {mac} with {dongle.name}, {dongle.mac}')
                            same = True
                            break
                    if same:
                        continue

                    tasks = Tasks()
                    try:
                        dongle = Dongle(mac, name)
                        dongles[mac] = dongle
                        transport, protocol = await serial_asyncio.create_serial_connection(tasks.loop,
                                                                                            Serial,
                                                                                            name,
                                                                                            baudrate=460800)
                        dongle.ready(protocol)
                        dongle.activated()
                    except serial.serialutil.SerialException:
                        logger.exception(f"open serial {name} failed")
                        if mac in dongles:
                            del dongles[mac]
            await asyncio.sleep(0.01)
        except Exception as e:
            logger.exception("Serial management error:%s", e)
            # if mac in dongles:
            #     del dongles[mac]
        await asyncio.sleep(0.1)


def init():
    tasks = Tasks()
    tasks.add(serial_manager())
    return
