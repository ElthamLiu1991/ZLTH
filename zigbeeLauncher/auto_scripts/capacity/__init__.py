import json
import os
import threading
import time

from zigbeeLauncher.auto_scripts import PREPARING, ERROR, INFO, WORKING, START, WARNING, DONE, FINISH, SUCCESS, FAILED, \
    auto_record, STOP
from zigbeeLauncher.auto_scripts.script import Script
from zigbeeLauncher.auto_scripts.tuya_api import TUYAAPI
from zigbeeLauncher.auto_scripts.zlth_api import ZLTHAPI
from zigbeeLauncher.logging import autoLogger as logger
from zigbeeLauncher import base_dir, socketio


class Testing(Script):

    def __init__(self, status_callback):
        super().__init__(script='capacity', path=os.path.join(base_dir, 'scripts/capacity.json'), status_callback=status_callback)
        self.tuya = None
        self.zlth = None
        self.joined = []
        self.result = []
        self.pending = []
        self.dongle_offset = 0
        self.trigger = 0
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
            self.log(ERROR, "Cannot get config")
            self.update(FINISH, STOP)

    def _update_result(self, status, descriptor):
        if self.result:
            for item in self.result:
                if item.get('repeat') == self.repeat:
                    item['record'].append(descriptor)

        self.result.append({
            'repeat': self.repeat, 'status': status, 'target': self.count, 'devices': self.trigger, 'record': [descriptor]
        })

    def set_config(self, config):
        self.config = config
        self._load_config()

    def start(self):
        try:
            self.running = True
            self.tuya = TUYAAPI(self.vid)
            self.zlth = ZLTHAPI()
            self.preparing()
        except Exception as e:
            logger.exception("ERROR:")
            self.log(ERROR, repr(e))
            self.update(FINISH, STOP)
            self.stop()

    def stop(self):
        self.running = False

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
        self.log(INFO, 'preparing testing environment')
        self.update(PREPARING, SUCCESS)
        if not self.vid:
            raise Exception('please provide gateway vid')
        if not self.zlth.dongles:
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
        if self.repeat:
            self.log(INFO, "Repeat:{}".format(self.repeat))
            self.dongle_offset = 0
            self.trigger = 0
            self.pending = []
            # reset device
            self.hub_reset()
        else:
            self.log(INFO, "Finish")
            self.log(INFO, repr(self.result))
            for item in self.result:
                if item['status'] == FAILED:
                    self.update(FINISH, FAILED)
                    return
            self.update(FINISH, SUCCESS)
            self.running = False

    def joining(self):
        """
        trigger batch devices joining network
        :return:
        :exception
            1. trigger dongle permit join failed
            2. open/close permit join window
        """
        self.update(WORKING, SUCCESS)
        batch = self.batch
        offset = 0
        for i, dongle in enumerate(self.zlth.dongles):
            if not self.running:
                return
            if batch == 0:
                break
            if self.dongle_offset != 0 and i <= self.dongle_offset:
                continue
            offset = i+1
            if not dongle.connected:
                self.log(WARNING, "ZLTH: device {} is offline".format(dongle.mac))
                continue
            if dongle.state != 1:
                self.log(WARNING, "ZLTH: device {} is not ready".format(dongle.mac))
                continue
            self.log(INFO, "ZLTH: trigger {} join...".format(dongle.mac))
            if not self.zlth.join(dongle.mac, [self.channel]):
                raise Exception("ZLTH: failed to trigger device {} join".format(dongle.mac))
            batch -= 1
            self.pending.append(dongle.mac)
            self.trigger += 1
            if self.count != -1 and self.trigger == self.count:
                self.log(INFO, "{} devices are operated")
                break
        if batch == self.batch:
            self.log(INFO, "ZLTH: all devices added")
            self.verify()
            self.repeat -= 1
            self.working()
        else:
            if not self.tuya.permit_join(254):
                raise Exception("HUB: failed to open permit join")
            if not self.tuya.is_permit(True):
                raise Exception("HUB: permit join window not open")
            self.log(INFO, "ZLTH: trigger {} devices done".format(self.batch))
            self.dongle_offset = offset
            if self.checking():
                # close permit join
                self.log(INFO, "HUB: close permit join")
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
            for device in self.pending:
                # check device register and ZLTH status is joined
                if self.tuya.is_register(device) and self.zlth.is_joined(device):
                    self.log(INFO, "{} joined".format(device))
                    self.joined.append(device)
                    self.pending.remove(device)
            if not self.pending:
                self.log(INFO, "pending devices are joined")
                return True
            time.sleep(5)
        if self.running:
            # verify current batch all joined or not in case missing some join notification
            for device in self.pending:
                if self.zlth.is_joined(device):
                    self.pending.remove(device)

            if not self.pending:
                return True
            self.log(ERROR, "timeout, devices {} not joined".format(self.pending))
            self._update_result(FAILED, 'permit join timeout, devices {} not joined'.format(self.pending))
        return False

    def verify(self):
        """
        verify all device are joined
        :return:
        """
        result = True
        for device in self.joined:
            dongle = self.zlth.get_device(device)
            if not dongle:
                result = False
                self.log(ERROR, "dongle {} disappear".format(device))
                self._update_result(FAILED, 'dongle {} disappear'.format(device))
            elif not dongle.connected:
                result = False
                self.log(ERROR, "dongle {} is offline".format(device))
                self._update_result(FAILED, 'dongle {} is offline'.format(device))
            elif dongle.state != 6:
                result = False
                self.log(ERROR, "device {} is not joined".format(device))
                self._update_result(FAILED, 'device {} is not joined'.format(device))
        if result:
            self._update_result(SUCCESS, 'all device are joined')

    def hub_reset(self):
        """
        remove all device from hub
        :return:
        """
        self.log(INFO, "remove all devices from IOT")
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
        self.log(INFO, "ZLTH: reset all dongles")
        self.log(INFO, "ZLTH: get {} dongles".format(len(self.zlth.dongles)))
        # reset dongle first
        for dongle in self.zlth.dongles:
            if dongle.connected and dongle.state != 1:
                self.zlth.leave(dongle.mac)
        time.sleep(5)
        self.log(INFO, "ZLTH: check all dongles are reset")
        self.zlth.refresh()
        for dongle in self.zlth.dongles:
            if dongle.connected and not self.zlth.is_reset(dongle.mac):
                self.log(WARNING, "ZLTH: device {} is not reset".format(dongle.mac))
        self.zlth.refresh()
        self.joining()