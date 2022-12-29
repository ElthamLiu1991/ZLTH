import json
import os
import threading
import time

from zigbeeLauncher.auto_scripts import State, Status, Result
from zigbeeLauncher.auto_scripts.script import Script
from zigbeeLauncher.auto_scripts.tuya_api import TUYAAPI
from zigbeeLauncher.auto_scripts.zlth_api import ZLTHAPI
from zigbeeLauncher.logging import autoLogger as logger
from zigbeeLauncher import base_dir, socketio


class Testing(Script):

    def __init__(self, status_callback):
        super().__init__(script='capacity', path=os.path.join(base_dir, 'scripts/capacity.json'), status_callback=status_callback)
        status_callback(State.READY, Status.INFO)
        self.tuya = None
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
            self.vid = self.config.get("gateway_vid")
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
            self.tuya = TUYAAPI(self.vid)
            self.zlth = ZLTHAPI()
            self.preparing()
        except Exception as e:
            logger.exception("ERROR:")
            self.log(Status.ERROR, repr(e))
            self.update(State.FINISH, Result.FAILED)
            self.stop()

    def stop(self):
        self.running = False
        if self.tuya.is_permit(True):
            self.tuya.permit_join(0)

    def preparing(self):
        """
        checking available ZLTH dongles
        get IOT token
        check hub is online
        get zigbee network channel
        :return:
        :exception:
            1. not ZLTH dongle available
            2. get IOT token failed
            3. hub is offline
            4. not zigbee network
        """
        self.log(Status.INFO, 'preparing testing environment')
        self.update(State.PREPARING, Result.SUCCESS)
        if not self.vid:
            raise Exception('please provide gateway vid')
        if isinstance(self.zlth.dongles, bool) or not self.zlth.dongles:
            raise Exception('ZLTH: no available dongles')
        if not self.tuya.token:
            raise Exception('HUB: failed to get tuya IOT token')
        if not self.tuya.is_online():
            raise Exception('HUB: hub is offline')
        self.channel = self.tuya.get_channel()
        if not self.channel:
            raise Exception('HUB: cannot get zigbee network channel')
        self.working()

    def working(self):
        if not self.running:
            return

        self.update(State.WORKING, Result.SUCCESS)
        if self.repeat:
            self.log(Status.INFO, "Repeat:{}".format(self.repeat))
            self.offset = 0
            self.joined = []
            self.trigger = []
            self.pending = []
            # reset device
            self.hub_reset()
        else:
            self.log(Status.INFO, "Finish")
            self.log(Status.INFO, json.dumps(self.result, indent=4))
            for item in self.result:
                if item['status'] == Result.FAILED:
                    self.update(State.FINISH, Result.FAILED)
                    return
            self.update(State.FINISH, Result.SUCCESS)
            self.running = False

    def joining(self):
        """
        trigger batch devices joining network
        :return:
        :exception
            1. trigger dongle permit join failed
            2. open/close permit join window
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
            self.offset = i+1
            if not dongle.connected:
                self.log(Status.WARNING, "ZLTH: device {} is offline".format(dongle.mac))
                continue
            if dongle.state != 1:
                self.log(Status.WARNING, f"ZLTH: device {dongle.mac} is not ready, state:{dongle.state}")
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
            if not self.tuya.permit_join(254):
                raise Exception("HUB: failed to open permit join")
            if not self.tuya.is_permit(True):
                raise Exception("HUB: permit join window not open")
            self.log(Status.INFO, "ZLTH: trigger {} devices done".format(self.batch))

            if self.checking():
                # close permit join
                self.log(Status.INFO, "HUB: close permit join")
                if not self.tuya.permit_join(0):
                    raise Exception("HUB: failed to close permit join")
                if not self.tuya.is_permit(False):
                    raise Exception("HUB: permit join window not close")
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
        while self.running and self.tuya.is_permit(True):
            if not self.pending:
                self.log(Status.INFO, "pending devices are joined")
                return True
            registered = self.tuya.get_sub_devices()
            if registered:
                for item in registered:
                    if item.node_id in self.pending and self.zlth.is_joined(item.node_id):
                        self.log(Status.INFO, "{} joined".format(item.node_id))
                        self.joined.append(item.node_id)
                        self.pending.remove(item.node_id)
            # check pending devices are in joining mode
            for item in self.pending:
                device = self.zlth.get_device(item)
                if device.state == 1:
                    self.log(Status.WARNING, f"{item} not in joining mode")
                    self.zlth.join(item, [self.channel])

            time.sleep(5)
        if self.running:
            # verify current batch all joined or not in case missing some join notification
            for device in self.pending:
                if self.tuya.is_register(device) and self.zlth.is_joined(device):
                    self.pending.remove(device)
                    self.log(Status.INFO, f"{device} joined after timeout")
            if not self.pending:
                return True
            self.log(Status.ERROR, "timeout, devices {} not joined".format(self.pending))
            # reset pending devices
            for device in self.pending:
                if not self.zlth.reset(device) or not self.zlth.is_reset(device):
                    self.log(Status.WARNING, f"{device} reset failed")
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
            self._update_result(Result.SUCCESS, 'all device are joined')

    def hub_reset(self):
        """
        remove all device from hub
        :return:
        """
        self.log(Status.INFO, "remove all devices from IOT")
        devices = self.tuya.get_sub_devices()
        if devices:
            for device in devices:
                self.tuya.delete_device(device.id)
        self.zlth_reset()

    def zlth_reset(self):
        """
        reset all dongles
        :return:
        """
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