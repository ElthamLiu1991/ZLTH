import asyncio
import json
import os
import threading
import time

from zigbeeLauncher import base_dir
from zigbeeLauncher.auto_scripts import State, Status, Result
from zigbeeLauncher.auto_scripts.script import Script
from zigbeeLauncher.auto_scripts.wiser_api import WiserAPI, WiserMQTT
from zigbeeLauncher.auto_scripts.zlth_api import ZLTHAPI
from zigbeeLauncher.logging import autoLogger as logger


class Testing(Script, WiserAPI):

    def on_connect(self, connected):
        if self.state == State.PREPARING:
            self.set_client(self.wiser)
            if connected:
                self.log(Status.INFO, "Wiser Standard Hub {} connected".format(self.ip))
            else:
                self.log(Status.ERROR, "Wiser Standard Hub {} disconnect".format(self.ip))
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
        if self.stage != State.PREPARING:
            self.log(Status.WARNING, f"HUB: device {id} leave")

    def __init__(self, status_callback=None):
        Script.__init__(self,
                        "capacity_local",
                        os.path.join(base_dir, 'scripts/capacity_local.json'),
                        status_callback)
        WiserAPI.__init__(self)
        self.wiser = None
        self.zlth = None
        self.joined = []
        self.result = []
        self.pending = []
        self.offset = 0
        self.trigger = []
        self.channel = 0
        self._load_config()

    def _load_config(self):
        if self.config:
            self.ip = self.config.get('gateway_ip')
            self.count = self.config.get('count')
            if not self.count:
                self.count = -1
            self.repeat = self.config.get("repeat")
            if not self.repeat:
                self.repeat = 1
            self.batch = self.config.get('batch')
            if not self.batch:
                self.batch = 1
        else:
            logger.error("Get config failed, stop")
            self.log(Status.ERROR, "Cannot get config")
            self.update(State.FINISH, Result.STOP)

    def _update_result(self, status, descriptor):
        if self.result:
            for item in self.result:
                if item.get('repeat') == self.repeat:
                    item['trigger'] = len(self.trigger)
                    item['joined'] = self.joined
                    item['record'].append(descriptor)
                    return

        self.result.append({
            "repeat": self.repeat,
            "status": status,
            "target": self.count if self.count != -1 else len(self.zlth.dongles),
            "trigger": len(self.trigger),
            "joined": self.joined,
            "record": [descriptor]
        })

    def set_config(self, config):
        self.config = config
        self._load_config()

    def start(self):
        self.update(State.START, Result.SUCCESS)
        try:
            self.running = True
            self.zlth = ZLTHAPI()
            self.preparing()
        except Exception as e:
            logger.exception("Status.ERROR:")
            self.log(Status.ERROR, repr(e))
            self.update(State.FINISH, Result.FAILED)
            self.stop()

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
        if not self.ip:
            raise Exception('HUB: failed to get gateway ip')
        if isinstance(self.zlth.dongles, bool) or not self.zlth.dongles:
            raise Exception('ZLTH: no available dongles')
        if not self.wiser:
            # first connection
            self.wiser = WiserMQTT(self)
            self.wiser.start()
        while True:
            if self.wiser.connected:
                break
            else:
                time.sleep(1)
        self.set_client(self.wiser)
        self.get_network()
        self.working()

    def working(self):
        if not self.running:
            return
        self.update(State.WORKING, Result.SUCCESS)
        if self.repeat:
            if not self.running:
                return
            self.log(Status.INFO, "Repeat:{}".format(self.repeat))
            self.offset = 0
            self.joined = []
            self.trigger = []
            self.pending = []
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
        batch = self.batch
        self.pending = []
        for i, dongle in enumerate(self.zlth.dongles):
            if not self.running:
                return
            if batch == 0:
                break
            if self.count != -1 and len(self.trigger) == self.count:
                self.log(Status.INFO, f"expected devices {self.count} are trigger to joined")
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
        if batch == self.batch:
            self.log(Status.INFO, "ZLTH: all devices added")
            self.verify()
            self.repeat -= 1
            self.working()
        else:
            self.log(Status.INFO, "HUB: open permit join")
            self.permit_join(254)
            if not self.is_permit():
                raise Exception("HUB: failed to open permit join")
            self.log(Status.INFO, "ZLTH: trigger {} devices done".format(self.batch))

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
        while self.running and self.is_permit():
            if not self.pending:
                self.log(Status.INFO, "pending devices are joined")
                return True
            # check pending device are joined to hub
            self.get_devices()
            if self.devices:
                for device in self.devices:
                    if device.MacAddress in self.pending and self.zlth.is_joined(device.MacAddress):
                        self.log(Status.INFO, f"{device.MacAddress} joined")
                        self.joined.append(device.MacAddress)
                        self.pending.remove(device.MacAddress)
            # check pending devices are in joining mode
            for item in self.pending:
                device = self.zlth.get_device(item)
                if device.state == 1:
                    self.log(Status.WARNING, f"{item} not in joining mode")
                    self.zlth.join(item, [self.channel])
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
            for device in self.pending:
                if not self.zlth.reset(device) or not self.zlth.is_reset(device):
                    self.log(Status.WARNING, f"{device} reset failed")

            self.log(Status.ERROR, "timeout, devices {} not joined".format(self.pending))
            # self._update_result(FAILED, 'permit join timeout, devices {} not joined'.format(self.pending))
        return False

    def verify(self):
        """
        verify all device are joined
        :return:
        """
        result = True
        for device in self.trigger:
            if not self.running:
                return
            dongle = self.zlth.get_device(device)
            if not dongle:
                result = False
                self.log(Status.ERROR, "dongle {} disappear".format(device))
                self._update_result(Result.FAILED, 'dongle {} disappear'.format(device))
            elif not dongle.connected:
                result = False
                self.log(Status.ERROR, "dongle {} is offline".format(device))
                self._update_result(Result.FAILED, 'dongle {} is offline'.format(device))
            elif dongle.state != 6:
                result = False
                self.log(Status.ERROR, "device {} is not joined".format(device))
                self._update_result(Result.FAILED, 'device {} is not joined'.format(device))

        if result:
            self._update_result(Result.SUCCESS, 'all devices are joined')

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
            elif dongle.state == 6:
                self.zlth.leave(dongle.mac)
            elif dongle.state != 1:
                self.zlth.reset(dongle.mac)
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
