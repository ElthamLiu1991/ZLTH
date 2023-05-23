"""
get simulator/device from database
send command via current simulator MQTT client
"""
import time
import uuid
from dataclasses import dataclass
from typing import Any, Optional

from dacite import from_dict

from zigbeeLauncher.data_model import Join, Message, CommandDevice, Attribute
from zigbeeLauncher.database.interface import DBSimulator, DBDevice
from zigbeeLauncher.dongle.dongle import DongleMetaData
from zigbeeLauncher.simulator.handler import handle_device_command
from zigbeeLauncher.util import Global, get_ip_address
from zigbeeLauncher.wait_response import wait_response


def send_command(ip, mac, command, timeout=10):
    timestamp = int(round(time.time() * 1000))
    uid = str(uuid.uuid1())
    # 加入request等待队列
    task = wait_response(timestamp, uid, timeout)
    message = Message(uuid=uid, timestamp=timestamp, data=command, code=0, message="")
    if ip == get_ip_address():
        handle_device_command(message, ip, mac, ip)
    else:
        simulator = Global.get(Global.SIMULATOR)
        simulator.client.send_device_command(ip, mac, message)

    timeout, data = task.result()
    if timeout or data.code != 0:
        return None
    else:
        return data


class ZLTHAPI:
    def __init__(self):
        self.simulator = Global.get(Global.SIMULATOR)
        self.simulators = []
        self.dongles = []
        self._get_simulators()
        self._get_devices()

    def _get_simulators(self):
        for item in DBSimulator().retrieve():
            self.simulators.append(from_dict(data_class=DBSimulator.DataModel, data=item))

    def _get_devices(self):
        for item in DBDevice().retrieve():
            self.dongles.append(from_dict(data_class=DBDevice.DataModel, data=item))

    def _send(self, mac, command):
        device = self.get_device(mac)
        if not device:
            return None
        else:
            return send_command(device.ip, mac, command)

    def refresh(self):
        self._get_devices()

    def get_simulator(self, ip):
        simulator = DBSimulator(mac=ip).retrieve()
        if simulator:
            return from_dict(data_class=DBSimulator.DataModel, data=simulator[0])
        return None

    def get_device(self, mac):
        dongle = DBDevice(mac=mac).retrieve()
        if dongle:
            return from_dict(data_class=DBDevice.DataModel, data=dongle[0])
        return None

    def is_joined(self, mac):
        device = self.get_device(mac)
        if device and device.state == DongleMetaData.DongleState.JOINED:
            return True
        return False

    def is_reset(self, mac):
        device = self.get_device(mac)
        if device and device.state == DongleMetaData.DongleState.UN_COMMISSIONED:
            return True
        return False

    def join(self, mac, channels, pan_id=None, extended_pan_id=None):
        command = CommandDevice(join=Join(channels=channels, pan_id=pan_id, extended_pan_id=extended_pan_id))
        result = self._send(mac, command)
        return True if result and result.code == 0 else False

    def leave(self, mac):
        result = self._send(mac, CommandDevice(leave={}))
        return True if result and result.code == 0 else False

    def reset(self, mac):
        result = self._send(mac, CommandDevice(reset={}))
        return True if result and result.code == 0 else False

    def read(self, mac, attribute: Attribute):
        command = CommandDevice(attribute=attribute)
        result = self._send(mac, command)
        if result and result.code == 0:
            return result.data.get('value')
        return None

    def write(self, mac, attribute: Attribute):
        command = CommandDevice(attribute=attribute)
        result = self._send(mac, command)
        return True if result and result.code == 0 else False
