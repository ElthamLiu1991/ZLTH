import json
import os
import time
from dataclasses import dataclass
from typing import Optional

from dacite import from_dict, MissingValueError, WrongTypeError

from zigbeeLauncher.auto_scripts import State, Status, Result, ScriptName
from zigbeeLauncher.auto_scripts.hub_api import HubAPI
from zigbeeLauncher.auto_scripts.script import Script
from zigbeeLauncher.auto_scripts.tuya_api import TUYAAPI
from zigbeeLauncher.auto_scripts.zlth_api import ZLTHAPI, Device_base
from zigbeeLauncher.logging import autoLogger as logger
from zigbeeLauncher import base_dir


@dataclass
class Config:
    vid: str
    repeat: int
    batch: int
    ip: str
    count: Optional[int]
    dongles: Optional[list[str]]
    simulators: Optional[list[str]]


class Testing(Script):

    def __init__(self, status_callback):
        super().__init__(script=ScriptName.CAPACITY,
                         path=os.path.join(base_dir, 'scripts/' + ScriptName.CAPACITY + '.json'),
                         status_callback=status_callback)
        status_callback(State.READY, Status.INFO)
        self.tuya = None
        self.zlth = None
        self.hub = None
        self.test_result = []
        self.joined = []
        self.pending = []
        self.failed = []
        self.offset = 0
        self.trigger = []
        self.channel = 0

        self.dongles = []
        self.ready_dongles = []

    def load_config(self):
        if not self.config:
            logger.error("Cannot get config")
            self.update(State.FINISH, Result.STOP)
        else:
            try:
                self.setting = from_dict(data_class=Config, data=self.config)
            except MissingValueError as e:
                self.error = f"Invalid config, {str(e)}"
            except WrongTypeError as e:
                self.error = f"Invalid config, {str(e)}"
            else:
                if self.setting.batch < 1:
                    self.error = 'batch should be more than 0'
                else:
                    self.ready = True

    def update_result(self, result, descriptor):
        if self.test_result:
            for item in self.test_result:
                if item.get('repeat') == self.setting.repeat:
                    item['trigger'] = len(self.trigger)
                    item['joined'] = len(self.joined)
                    item['record'].append(descriptor)
                    return

        self.test_result.append({
            "repeat": self.setting.repeat,
            "result": result,
            "target": self.setting.count if self.setting.count else len(self.dongles),
            "trigger": len(self.trigger),
            "joined": len(self.joined),
            "record": [descriptor]
        })

    def start(self):
        self.update(State.START, Result.SUCCESS)
        try:
            self.running = True
            self.tuya = TUYAAPI(self.setting.vid)
            self.zlth = ZLTHAPI()
            self.preparing()
        except Exception as e:
            logger.exception("ERROR:")
            self.log(Status.ERROR, repr(e))
            self.update(State.FINISH, Result.FAILED)
            self.stop()
        else:
            self.working()

    def stop(self):
        self.running = False
        if self.hub:
            self.hub.stop()
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
        # check hub ip is available
        self.hub = HubAPI(self.record, self.setting.ip, self.tuya)
        if not self.hub.connect:
            raise Exception(f'cannot connect to hub: {self.setting.ip}')
        if isinstance(self.zlth.dongles, bool) or not self.zlth.dongles:
            raise Exception('ZLTH: no available dongles')
        if not self.tuya.token:
            raise Exception('HUB: failed to get tuya IOT token')
        if not self.tuya.is_online():
            raise Exception('HUB: hub is offline')
        self.channel = self.tuya.get_channel()
        if not self.channel:
            raise Exception('HUB: cannot get zigbee network channel')
        if self.setting.dongles and self.setting.simulators:
            raise Exception(f'assigned dongles and simulators both is unsupported')
        # count, dongles, simulators only can be assigned one of them
        if self.setting.count:
            if self.setting.dongles or self.setting.simulators:
                raise Exception(f'only support assigned count or dongles or simulators')
            if self.setting.count > len(self.zlth.dongles):
                raise Exception(f'only find {len(self.zlth.dongles)} dongles, less than {self.setting.count}')
            for i, dongle in enumerate(self.zlth.dongles):
                if i < self.setting.count:
                    self.dongles.append(dongle.mac)
                else:
                    break
        elif self.setting.dongles:
            if self.setting.simulators:
                raise Exception(f'count or dongles or simulators cannot be assigned at the same time')
            if len(self.setting.dongles) > len(self.zlth.dongles):
                raise Exception(f'only find {len(self.zlth.dongles)} dongles, less than {len(self.setting.dongles)}')
            # check setting.dongles all can be found in zlth.dongles
            for mac in self.setting.dongles:
                if not self.zlth.has_device(mac):
                    raise Exception(f'cannot find {mac} in dongle list')
            self.dongles = self.setting.dongles.copy()
        elif self.setting.simulators:
            for ip in self.setting.simulators:
                simulator = self.zlth.has_simulator(ip)
                if not simulator:
                    raise Exception(f'cannot find {ip} in simulator list')
                self.dongles.extend(simulator.devices)
            if not self.dongles:
                raise Exception(f'no available dongles in {self.setting.simulators}')
        else:
            # all dongles
            for dongle in self.zlth.dongles:
                self.dongles.append(dongle.mac)

        self.log(Status.INFO, "preparing done")

    def working(self):
        if not self.running:
            return
        self.update(State.WORKING, Result.SUCCESS)
        while self.running and self.setting.repeat:
            for result in self.test_result:
                if result.get('repeat') == self.setting.repeat + 1:
                    self.log(Status.INFO, f"result: {json.dumps(result, indent=4)}")
                    break
            self.log(Status.INFO, f"Repeat:{self.setting.repeat}")
            self.ready_dongles = self.dongles.copy()
            self.log(Status.INFO, f"testing {len(self.ready_dongles)} devices totally")
            self.joined = []
            self.trigger = []
            self.pending = []
            self.failed = []
            # reset device
            try:
                self.hub_reset()
            except Exception as e:
                logger.exception("working error:")
                self.log(Status.INFO, f"working error: {str(e)}, goto next run")
                self.update_result(Result.FAILED, str(e))
                # self.update(State.FINISH, Result.FAILED)
                if self.tuya.is_permit(True):
                    self.tuya.permit_join(0)
                self.setting.repeat -= 1
            finally:
                # store hub files
                if self.hub.is_connected():
                    self.hub.set_folder(self.setting.repeat+1)
                    self.hub.get_hub_files()
                else:
                    self.log(Status.WARNING, f"hub {self.setting.ip} not connect")
                if not self.hub.connect() and not self.running:
                    self.log(Status.ERROR, f"connect to hub {self.setting.ip} failed")
        if self.running:
            self.log(Status.INFO, "Finish")
            self.result = Result.SUCCESS
            for item in self.test_result:
                if item.get('result') == Result.FAILED:
                    self.result = Result.FAILED
                    break
            self.update(State.FINISH, self.result)
            self.log(Status.INFO, json.dumps(self.test_result, indent=4))
            self.running = False

            # store hub files
            if self.hub.is_connected():
                self.hub.set_folder(self.setting.repeat + 1)
                self.hub.get_hub_files()
            else:
                self.log(Status.WARNING, f"hub {self.setting.ip} not connect")

    # self.update(State.WORKING, Result.SUCCESS)
        # if self.setting.repeat:
        #     for result in self.test_result:
        #         if result.get('repeat') == self.setting.repeat:
        #             self.log(Status.INFO, f"result: {json.dumps(result, indent=4)}")
        #             break
        #     self.log(Status.INFO, "Repeat:{}".format(self.setting.repeat))
        #     self.ready_dongles = self.dongles.copy()
        #     self.log(Status.INFO, f"testing {len(self.ready_dongles)} devices totally")
        #     self.joined = []
        #     self.trigger = []
        #     self.pending = []
        #     self.failed = []
        #     # reset device
        #     self.hub_reset()
        # else:
        #     self.log(Status.INFO, "Finish")
        #     self.result = Result.SUCCESS
        #     for item in self.test_result:
        #         if item.get('result') == Result.FAILED:
        #             self.result = Result.FAILED
        #             break
        #     self.update(State.FINISH, self.result)
        #     self.log(Status.INFO, json.dumps(self.test_result, indent=4))
        #     self.running = False

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

        batch = self.setting.batch
        self.pending = []
        for mac in self.ready_dongles[:]:
            if not self.running:
                return
            if batch == 0:
                break
            # check require count devices are trigger to join
            if self.setting.count and len(self.trigger) == self.setting.count:
                self.log(Status.INFO, f"expected devices {self.setting.count} are trigger to joined")
                break
            # # check dongle is available
            # if not dongle.connected:
            #     self.log(Status.WARNING, "ZLTH: device {} is offline".format(dongle.mac))
            #     continue
            # if dongle.state != 1:
            #     self.log(Status.WARNING, f"ZLTH: device {dongle.mac} is not ready, state:{dongle.state}")
            #     continue
            self.log(Status.INFO, f"ZLTH: trigger {mac} join...")
            if not self.zlth.join(mac, [self.channel]):
                self.log(Status.ERROR, f'trigger join failed')
                # check dongle connected and state
                dongle = self.zlth.get_device(mac)
                if not dongle:
                    self.log(Status.ERROR, f'get {mac} failed')
                else:
                    if not dongle.connected:
                        self.log(Status.ERROR, f'{mac} disconnected')
                        self.ready_dongles.remove(mac)
                        continue
                    elif dongle.state != 4:
                        self.log(Status.ERROR, f'{mac} is not in commission mode, {dongle.state}')
                        self.ready_dongles.remove(mac)
                        continue
                    else:
                        self.log(Status.INFO, f"{mac} is in commission mode")
            batch -= 1
            self.pending.append(mac)
            self.trigger.append(mac)
            self.ready_dongles.remove(mac)

        if batch == self.setting.batch:
            self.log(Status.INFO, "ZLTH: all devices added")
            self.verify()
            self.setting.repeat -= 1
        else:
            if not self.tuya.permit_join(254):
                raise Exception("HUB: failed to open permit join")
            if not self.tuya.is_permit(True):
                raise Exception("HUB: permit join window not open")
            self.log(Status.INFO, f"ZLTH: trigger {len(self.pending)} devices to join")

            if self.checking():
                # close permit join
                self.log(Status.INFO, "HUB: close permit join")
                if not self.tuya.permit_join(0):
                    raise Exception("HUB: failed to close permit join")
                if not self.tuya.is_permit(False):
                    raise Exception("HUB: permit join window not close")
            self.joining()

    def _device_join_and_register(self, device: Device_base):
        if device.state == 6 or device.state == 7:
            if self.tuya.is_register(device.mac):
                if device.mac not in self.joined:
                    self.joined.append(device.mac)
                if device.mac in self.pending:
                    self.pending.remove(device.mac)
                return True
            else:
                self.log(Status.WARNING, f"{device.mac} joined but not register, state:{device.state}")
                return False
        return False

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
            if not self.tuya.is_permit(True):
                self.log(Status.WARNING, "permit join close")
                break
            if not self.tuya.is_online(self.setting.vid):
                self.log(Status.ERROR, "hub is offline")
                self.update_result(Result.FAILED, "hub is offline")
                break
            for mac in self.pending:
                device = self.zlth.get_device(mac)
                # check pending devices are in joining mode
                if not device.connected:
                    self.log(Status.WARNING, f"{mac} disconnected")
                    # remove device from pending
                    self.pending.remove(mac)
                if device.state == 1:
                    self.log(Status.WARNING, f"{mac} not in joining mode")
                    self.zlth.join(mac, [self.channel])
                elif self._device_join_and_register(device):
                    self.log(Status.INFO, f"{device.mac} joined and register")

            for mac in self.failed:
                device = self.zlth.get_device(mac)
                if self._device_join_and_register(device):
                    self.log(Status.INFO, f"{device.mac} joined and register in other batch")
                    self.failed.remove(mac)
            time.sleep(5)
        if self.running:
            # verify current batch all joined or not in case missing some join notification
            for mac in self.pending:
                device = self.zlth.get_device(mac)
                if self._device_join_and_register(device):
                    self.log(Status.INFO, f"{mac} joined after timeout")
                elif self.tuya.is_register(mac):
                    self.log(Status.WARNING, f"{mac} registered but not join")
                elif self.zlth.is_joined(mac):
                    self.log(Status.WARNING, f"{mac} joined but not register")

            if not self.pending:
                return True
            self.log(Status.ERROR,
                     f"No.{int(len(self.trigger) / self.setting.batch)}timeout, devices {self.pending} not joined")
            # reset pending devices
            for mac in self.pending:
                self.failed.append(mac)
                if not self.zlth.leave(mac) or not self.zlth.is_reset(mac):
                    self.log(Status.WARNING, f"{mac} reset failed")
            # self.update_result(FAILED, 'permit join timeout, devices {} not joined'.format(self.pending))
        return False

    def verify(self):
        """
        verify all device are joined
        :return:
        """
        # wait 10 seconds
        time.sleep(10)
        self.log(Status.INFO, "verify")
        result = True
        for index, mac in enumerate(self.trigger):
            if not self.running:
                return
            dongle = self.zlth.get_device(mac)
            if not dongle:
                result = False
                self.log(Status.ERROR, f"dongle {mac} disappear")
                self.update_result(Result.FAILED, f'dongle {mac} disappear')
            elif not dongle.connected:
                result = False
                self.log(Status.ERROR, f"No.{index} dongle {mac} is offline")
                self.update_result(Result.FAILED, f'No.{index} dongle {mac} is offline')
            elif dongle.state == 1:
                result = False
                if mac in self.joined:
                    self.log(Status.ERROR, f"No.{index} device {mac} left")
                    self.joined.remove(mac)
                    self.update_result(Result.FAILED, f'No.{index} device {mac} left')
                else:
                    self.log(Status.ERROR, f"No.{index} device {mac} is not joined")
                    self.update_result(Result.FAILED, f'No.{index} device {mac} is not joined')
            elif dongle.state == 4:
                result = False
                self.log(Status.ERROR, f"No.{index} dongle {mac} still in commission mode")
            else:
                if dongle.state == 7:
                    self.log(Status.ERROR, f"No.{index} dongle {mac} state is 7")
                # check dongle register or not
                if not self.tuya.is_register(mac):
                    result = False
                    self.log(Status.ERROR, f"No.{index} device {mac} is joined but not register")
                    self.log(Status.ERROR, f"IOT device list: {self.tuya.get_sub_devices()}")
                    self.update_result(Result.FAILED, f'No.{index} device {mac} is joined but not register')
        # check online state
        devices = self.tuya.get_sub_devices()
        if devices:
            for device in devices:
                if not self.tuya.is_online(device.id):
                    self.log(Status.WARNING, f"device {device.node_id} is offline")
                    self.update_result(Result.FAILED, f"device {device.node_id} is offline")
                    result = False
        if result:
            self.log(Status.INFO, "verify success")
            self.update_result(Result.SUCCESS, 'all device are joined')
        else:
            self.log(Status.ERROR, "verify failed")

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
        self.log(Status.INFO, f"ZLTH: reset {len(self.dongles)} dongles")
        # reset dongle if need
        for mac in self.dongles:
            dongle = self.zlth.get_device(mac)
            if not dongle:
                self.log(Status.ERROR, f"ZLTH: get {mac} failed")
            else:
                if not dongle.connected:
                    self.log(Status.ERROR, f"ZLTH: {mac} is disconnected")
                elif dongle.state != 1:
                    self.zlth.leave(mac)
        time.sleep(5)

        self.joining()
