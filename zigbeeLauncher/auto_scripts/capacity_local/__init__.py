import asyncio
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Optional

from dacite import from_dict

from zigbeeLauncher import base_dir
from zigbeeLauncher.auto_scripts import State, Status, Result, ScriptName
from zigbeeLauncher.auto_scripts.script import Script
from zigbeeLauncher.auto_scripts.wiser_api import WiserAPI, WiserMQTT
from zigbeeLauncher.auto_scripts.zlth_api import ZLTHAPI
from zigbeeLauncher.logging import autoLogger as logger


@dataclass
class Config:
    ip: str
    repeat: int
    batch: int
    count: Optional[int] = -1


class Testing(Script, WiserAPI):

    def on_connect(self, connected):
        if self.state == State.PREPARING:
            if connected:
                self.log(Status.INFO, "Wiser Standard Hub {} connected".format(self.setting.ip))
            else:
                self.log(Status.ERROR, "Wiser Standard Hub {} disconnect".format(self.setting.ip))
                self.update(State.FINISH, Result.STOP)
                self.stop()

    def on_device_add(self, id, device):
        self.log(Status.INFO, f"HUB: device {device.MacAddress} joined")
        # if device:
        #     if device.MacAddress in self.pending:
        #         self.lock.acquire()
        #         # verify it on ZLTH
        #         if self.zlth.is_joined(device.MacAddress):
        #             self.log(Status.INFO, "{} joined".format(device.MacAddress))
        #             self.joined.append(device.MacAddress)
        #             if device.MacAddress in self.pending:
        #                 self.pending.remove(device.MacAddress)
        #         else:
        #             self.log(Status.WARNING, "ZLTH: device {} not join".format(device.MacAddress))
        #         self.lock.release()

    def on_device_del(self, id):
        if self.state != State.PREPARING:
            self.log(Status.WARNING, f"HUB: device {id} leave")

    def __init__(self, status_callback=None):
        Script.__init__(self,
                        ScriptName.CAPACITY_LOCAL,
                        os.path.join(base_dir, 'scripts/'+ScriptName.CAPACITY_LOCAL+'.json'),
                        status_callback)
        WiserAPI.__init__(self)
        self.wiser = None
        self.zlth = None
        self.result = []
        self.joined = []
        self.pending = []
        self.failed = []
        self.offset = 0
        self.trigger = []
        self.channel = 0
        self.load_config()

    def load_config(self):
        if not self.config:
            logger.error("Cannot get config")
            self.update(State.FINISH, Result.STOP)
        else:
            self.setting = from_dict(data_class=Config, data=self.config)
            if not self.setting:
                self.log(Status.ERROR, "Invalid config")
                self.update(State.FINISH, Result.STOP)
            else:
                self.ready = True

    def update_result(self, status, descriptor):
        if self.result:
            for item in self.result:
                if item.get('repeat') == self.setting.repeat:
                    item['trigger'] = len(self.trigger)
                    item['joined'] = len(self.joined)
                    item['record'].append(descriptor)
                    return

        self.result.append({
            "repeat": self.setting.repeat,
            "status": status,
            "target": self.setting.count if self.setting.count != -1 else len(self.zlth.dongles),
            "trigger": len(self.trigger),
            "joined": len(self.joined),
            "record": [descriptor]
        })

    def start(self):
        self.update(State.START, Result.SUCCESS)
        try:
            self.running = True
            self.zlth = ZLTHAPI()
            self.preparing()
        except Exception as e:
            logger.exception("ERROR:")
            self.log(Status.ERROR, repr(e))
            if not self.state or self.state == State.PREPARING:
                self.update(State.FINISH, Result.FAILED)
                self.stop()
            else:
                self.log(Status.INFO, "retry this run")
                if self.is_permit():
                    self.permit_join(0)
                self.working()

    def stop(self):
        self.running = False
        if self.wiser:
            self.wiser.stop()
        self.wiser = None
        if self.is_permit():
            self.permit_join(0)

    def preparing(self):
        self.update(State.PREPARING, Result.SUCCESS)
        self.log(Status.INFO, 'preparing testing environment')
        if not self.setting.ip:
            raise Exception('HUB: failed to get gateway ip')
        if isinstance(self.zlth.dongles, bool) or not self.zlth.dongles:
            raise Exception('ZLTH: no available dongles')
        if not self.wiser:
            # first connection
            self.wiser = WiserMQTT(self.setting.ip, self)
            self.wiser.start()
        while True:
            if self.wiser.connected:
                break
            else:
                time.sleep(1)
        self.get_network()
        self.log(Status.INFO, "preparing done")
        self.working()

    def working(self):
        if not self.running:
            return
        self.update(State.WORKING, Result.SUCCESS)
        if self.setting.repeat:
            if not self.running:
                return
            self.log(Status.INFO, "Repeat:{}".format(self.setting.repeat))
            self.offset = 0
            self.joined = []
            self.trigger = []
            self.pending = []
            self.failed = []
            self.get_devices()
            self.hub_reset()
        else:
            self.log(Status.INFO, "Finish")
            self.log(Status.INFO, json.dumps(self.result, indent=4))
            for item in self.result:
                if item['status'] == Result.FAILED:
                    self.update(State.FINISH, Result.FAILED)
                    return
            self.update(State.FINISH, Result.SUCCESS)
            self.stop()

    def joining(self):
        """
        trigger batch devices joining network
        :return:
        """
        if not self.running:
            return
        self.update(State.WORKING, Result.SUCCESS)
        batch = self.setting.batch
        self.pending = []
        for i, dongle in enumerate(self.zlth.dongles):
            if not self.running:
                return
            if batch == 0:
                break
            if self.setting.count != -1 and len(self.trigger) == self.setting.count:
                self.log(Status.INFO, f"expected devices {self.setting.count} are trigger to joined")
                break
            if i < self.offset:
                continue
            self.offset = i + 1
            if not dongle.connected:
                self.log(Status.WARNING, "ZLTH: device {} is offline".format(dongle.mac))
                continue
            if dongle.state != 1:
                self.log(Status.WARNING, "ZLTH: device {} is not ready".format(dongle.mac))
                continue
            self.log(Status.INFO, "ZLTH: trigger {} join...".format(dongle.mac))
            if not self.zlth.join(dongle.mac, [self.channel]):
                raise Exception("ZLTH: failed to trigger device {} join".format(dongle.mac))
            batch -= 1
            self.pending.append(dongle.mac)
            self.trigger.append(dongle.mac)
            # self.trigger += 1
        if batch == self.setting.batch:
            self.log(Status.INFO, "ZLTH: all devices added")
            self.verify()
            self.setting.repeat -= 1
            self.working()
        else:
            self.log(Status.INFO, "HUB: open permit join")
            self.permit_join(254)
            if not self.is_permit():
                raise Exception("HUB: failed to open permit join")
            self.log(Status.INFO, "ZLTH: trigger {} devices done".format(self.setting.batch))

            if self.checking():
                # close permit join
                self.log(Status.INFO, "HUB: close permit join")
                self.permit_join(0)
                if self.is_permit():
                    raise Exception("HUB: permit join window not close")
                self.get_devices()
            self.joining()

    def checking(self):
        """
        check IOT platform and dongle every 5 seconds,
        if device registered and joined(state=6),
        remove this record from pending list, stop loop if
        pending list is empty or permit join close
        :return:
            True: pending list is empty
            False: permit join timeout
        """
        start = int(time.time())
        while self.running and (int(time.time()) - start < 260):
            if not self.pending:
                self.log(Status.INFO, "pending devices are joined")
                return True
            if not self.is_permit():
                self.log(Status.WARNING, "permit join close")
                break
            # check pending device are joined to hub
            for item in self.pending:
                device = self.zlth.get_device(item)
                # check pending devices are in joining mode
                if device.state == 1:
                    self.log(Status.WARNING, f"{item} not in joining mode")
                    self.zlth.join(item, [self.channel])
                elif device.state == 6:
                    if self.is_joined(item):
                        self.log(Status.INFO, f"{item} joined")
                        self.joined.append(item)
                        self.pending.remove(item)
                    else:
                        self.log(Status.WARNING, f"{item} joined but not show in hub")
                        self.update_result(Result.FAILED, f'{item} joined but not show in hub')

            for item in self.failed:
                device = self.zlth.get_device(item)
                if device.state == 6 and self.is_joined(item):
                    self.log(Status.INFO, f"{item} joined in another batch")
                    self.joined.append(item)
                    self.pending.remove(item)

            # self.get_devices()
            # if self.devices:
            #     for device in self.devices:
            #         if device.MacAddress in self.pending and self.zlth.is_joined(device.MacAddress):
            #             self.log(Status.INFO, f"{device.MacAddress} joined")
            #             self.joined += 1
            #             self.pending.remove(device.MacAddress)
            #         if item.node_id in self.failed and self.zlth.is_joined(item.node_id):
            #             self.log(Status.INFO, f"{item.node_id} joined in other batch")
            #             self.joined += 1
            #             self.failed.remove(item.node_id)
            # # check pending devices are in joining mode
            # for item in self.pending:
            #     device = self.zlth.get_device(item)
            #     if device.state == 1:
            #         self.log(Status.WARNING, f"{item} not in joining mode")
            #         self.zlth.join(item, [self.channel])
            time.sleep(5)
        if self.running:
            # verify current batch all joined or not in case missing some join notification
            self.get_devices()
            for device in self.pending:
                for item in self.devices:
                    if item.MacAddress in self.pending and self.zlth.is_joined(device):
                        self.pending.remove(device)
                        self.log(Status.INFO, f"{device} joined after timeout")
            if not self.pending:
                return True
            self.log(Status.ERROR, "timeout, devices {} not joined".format(self.pending))
            for device in self.pending:
                self.failed.append(device)
                if not self.zlth.reset(device) or not self.zlth.is_reset(device):
                    self.log(Status.WARNING, f"{device} reset failed")

            # self.update_result(FAILED, 'permit join timeout, devices {} not joined'.format(self.pending))
        return False

    def verify(self):
        """
        verify all device are joined
        :return:
        """
        time.sleep(10)
        result = True
        for device in self.trigger:
            if not self.running:
                return
            dongle = self.zlth.get_device(device)
            if not dongle:
                result = False
                self.log(Status.ERROR, "dongle {} disappear".format(device))
                self.update_result(Result.FAILED, 'dongle {} disappear'.format(device))
            elif not dongle.connected:
                result = False
                self.log(Status.ERROR, "dongle {} is offline".format(device))
                self.update_result(Result.FAILED, 'dongle {} is offline'.format(device))
            elif dongle.state != 6:
                result = False
                if device in self.joined:
                    self.log(Status.ERROR, f"device {device} left")
                    self.joined.remove(device)
                    self.update_result(Result.FAILED, f'device {device} left')
                else:
                    self.log(Status.ERROR, f"device {device} is not joined")
                    self.update_result(Result.FAILED, f'device {device} is not joined')
        self.get_devices()
        for device in self.devices:
            if device.State == 0:
                self.log(Status.WARNING, f"device {device.MacAddress} is offline")
                self.update_result(Result.FAILED, f"device {device.MacAddress} is offline")
                result = False

        if result:
            self.update_result(Result.SUCCESS, 'all devices are joined')
        else:
            self.log(Status.ERROR, "verify failed")

    def hub_reset(self):
        # reset all devices
        self.log(Status.INFO, "HUB: remove all devices")
        if self.devices:
            for device in self.devices:
                self.reset_device(device.id)
        self.zlth_reset()

    def zlth_reset(self):
        self.zlth.refresh()
        self.log(Status.INFO, "ZLTH: reset all dongles")
        self.log(Status.INFO, "ZLTH: get {} dongles".format(len(self.zlth.dongles)))
        # reset dongle first
        for dongle in self.zlth.dongles:
            if not dongle.connected:
                self.log(Status.WARNING, f"ZLTH: device {dongle.mac} is offline")
            elif dongle.state != 1:
                self.zlth.leave(dongle.mac)
        time.sleep(5)
        self.log(Status.INFO, "ZLTH: check all dongles are reset")
        self.zlth.refresh()
        for dongle in self.zlth.dongles:
            if not dongle.connected:
                self.log(Status.WARNING, f"ZLTH: device {dongle.mac} is offline")
            elif dongle.state != 1:
                self.log(Status.WARNING, f"ZLTH: device {dongle.mac} is not reset, state:{dongle.state}")
        self.zlth.refresh()
        self.joining()
