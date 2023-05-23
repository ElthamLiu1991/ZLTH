import json
import os.path
import time
from dataclasses import dataclass
from functools import wraps
from typing import Optional, Any

from dacite import from_dict, MissingValueError, WrongTypeError

from zigbeeLauncher import base_dir
from zigbeeLauncher.auto_scripts import State, Status, Result, ScriptName
from zigbeeLauncher.auto_scripts.dcf_api import DCFZLTHSetting, DCFAPI, DCFZLTHRequest
from zigbeeLauncher.auto_scripts.hub_api import HubAPI
from zigbeeLauncher.auto_scripts.script import Script
from zigbeeLauncher.auto_scripts.tuya_api import TUYAAPI, DPStatus, DeviceResponse
from zigbeeLauncher.auto_scripts.zlth_api import ZLTHAPI
from zigbeeLauncher.data_model import Attribute
from zigbeeLauncher.logging import autoLogger as logger


@dataclass
class MacVid:
    mac: str
    vid: str


@dataclass
class Device:
    name: str
    pid: str
    functions: list[str]
    mac_vid: Optional[list[MacVid]]
    setting: Optional[DCFZLTHSetting]


@dataclass
class Config:
    duration: int
    vid: str
    interval: int
    validation: int
    devices: list[Device]


class Testing(Script):
    def __init__(self, status_callback):
        super().__init__(script=ScriptName.STABILITY,
                         path=os.path.join(base_dir, 'scripts/' + ScriptName.STABILITY + '.json'),
                         status_callback=status_callback)
        status_callback(State.READY, Status.INFO)
        self.tuya = None
        self.zlth = None
        # self.hub = None
        self.test_result = {}
        self.devices = {}
        self.summary = 0
        self.success = 0
        self.failed = 0
        self.capacity = 0
        self.start_time = None
        self.test_duration = None

    def load_config(self):
        self.ready = False
        if not self.config:
            logger.error("Get config failed")
            self.update(State.FINISH, Result.STOP)
        else:
            try:
                self.setting = from_dict(data_class=Config, data=self.config)
            except MissingValueError as e:
                self.error = f"Invalid config, {str(e)}"
            except WrongTypeError as e:
                self.error = f"Invalid config, {str(e)}"
            else:
                if self.setting.interval < 20:
                    self.error = 'interval should more than 20 seconds'
                elif self.setting.validation not in range(1, 11):
                    self.error = 'validation range should be [1, 10]'
                else:
                    self.ready = True

    def update_result(self, result, descriptor):
        self.result = result
        detail = {
            "summary": self.summary,
            "success": self.success,
            "failed": self.failed,
            "rate": '0%' if self.summary == 0 else str(round(self.success / self.summary * 100, 2)) + '%'
        }
        if self.test_result:
            self.test_result.update(detail)
            self.test_result['record'].append(descriptor)
        else:
            self.test_result = {
                "duration": self.setting.duration,
                "result": result,
                "capacity": self.capacity,
                "devices": self.devices,
                "record": [descriptor]
            }
            self.test_result.update(detail)

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

    def stop(self):
        self.running = False

    def preparing(self):
        """
        1. get IOT token
        2. check hub is online
        3. get available ZLTH dongles
        4. load DCF
        5. map device IOT virtual ID to ZLTH dongle mac
        :return:
        """
        self.log(Status.INFO, "preparing testing environment")
        self.update(State.PREPARING, Result.SUCCESS)
        # check hub ip is available
        # self.hub = HubAPI(self.record, self.setting.ip)
        # if not self.hub.connection:
        #     raise Exception(f'cannot connect to hub: {self.setting.ip}')
        if not self.zlth.dongles:
            raise Exception('ZLTH: no available dongles')
        else:
            self.log(Status.INFO, f'found {len(self.zlth.dongles)} dongles')
        if not self.tuya.token:
            raise Exception('HUB: failed to get tuya IOT token')
        else:
            self.log(Status.INFO, f'TUYA IOT token: {self.tuya.token}')
        if not self.tuya.is_online():
            raise Exception('HUB: hub is offline')
        # load DCF setting based on config
        for device in self.setting.devices:
            dcf = DCFAPI(device.name, device.functions)
            if not dcf.ready:
                raise Exception(f'DCF: load {device.name} failed')
            device.setting = dcf

        # get tuya devices and check PID
        devices = self.tuya.get_sub_devices()
        if not devices:
            raise Exception('TUYA: failed to get sub devices')
        self.capacity = len(devices)
        for device in devices:
            if not self.tuya.is_online(device.id):
                raise Exception(f'TUYA: {device.node_id} is offline')
            for item in self.setting.devices:
                if device.product_id == item.pid:
                    if item.mac_vid:
                        item.mac_vid.append(MacVid(mac=device.node_id, vid=device.id))
                        self.devices[item.name] += 1
                    else:
                        item.mac_vid = [MacVid(mac=device.node_id, vid=device.id)]
                        self.devices[item.name] = 1
                    break
                if not item.mac_vid:
                    raise Exception(f"TUYA: cannot found {item.pid} in device list")
        self.log(Status.INFO, "preparing done")
        self.working()

    def working(self):
        """
        :return:
        """
        self.update(State.WORKING, Result.SUCCESS)
        self.start_time = int(time.time())
        self.test_duration = self.setting.duration * 600
        timestamp = 0
        try:
            while self.running:
                for item in self.setting.devices:
                    for device in item.mac_vid:
                        for function in item.functions:
                            if not self.running:
                                raise Exception("STOP")
                            setting = item.setting.setting.get(function)

                            if setting.requestable:
                                self._send_request(timestamp, function, device, setting.endpoint, setting.request)
                                timestamp = int(time.time())
                            if setting.reportable:
                                self._trigger_report(timestamp, function, device, setting.endpoint, setting.report)
                                timestamp = int(time.time())
        except Exception:
            pass
        if self.running:
            self.log(Status.INFO, "FINISH")
            self.update_result(Result.SUCCESS, 'test finish')
            self.log(Status.INFO, json.dumps(self.test_result, indent=4))
            self.update(State.FINISH, self.test_result.get('result'))
            self.running = False

            # store hub files
            # if self.hub.is_connected():
            #     self.hub.set_folder()
            #     self.hub.get_hub_files()
            # else:
            #     self.log(Status.ERROR, f"hub {self.setting.ip} not connect")

    def _timeout(self):
        if int(time.time()) - self.start_time < self.test_duration:
            return False
        else:
            return True

    def _wait_interval_timeout(self, timestamp):
        while self.running and int(time.time()) - timestamp < self.setting.interval:
            pass
        if not self.running:
            return False
        if self._timeout():
            self.log(Status.INFO, "test finish")
            raise Exception("test finish")
        return True

    def _check_device_status(self, device):
        info = self.tuya.get_device_info(device.vid)
        if not info:
            # device is removed from IOT
            raise Exception(f'{device} deleted from IOT')
        elif not info.online:
            # device is offline in IOT
            raise Exception(f'{device} offline')
        return info

    def _send_request(self, timestamp, code, device: MacVid, endpoint, request: DCFZLTHRequest):
        """

        :param timestamp: interval timestamp
        :param code: IOT function code
        :param device: MacVid object, include device mac address and IOT virtual ID
        :param endpoint: zigbee mac address
        :param request: DCFZLTHRequest object
        :return:
        """
        for item in request.data:
            if not self._wait_interval_timeout(timestamp):
                return
            try:
                timestamp = int(time.time())
                self.summary += 1
                # check hub is online
                if not self.tuya.is_online(self.setting.vid):
                    raise Exception("hub is offline")
                # send request
                self.log(Status.INFO, f'sending request {code} to {device}, value:{item.value}')
                if not self.tuya.request(device.vid, DPStatus(code=code, value=item.value)):
                    self.log(Status.ERROR, f"send failed")
                    if self._check_device_status(device):
                        raise Exception("other error")
                time.sleep(self.setting.validation)
                self.log(Status.INFO, f'verifying')
                # verify on ZLTH dongle
                response = self.zlth.read(device.mac, Attribute(
                    endpoint=endpoint,
                    cluster=request.attr.cluster,
                    server=True,
                    attribute=request.attr.attribute,
                    manufacturer=request.attr.manufacturer,
                    manufacturer_code=request.attr.manufacturer_code
                ))
                if response is None:
                    raise Exception(f"get {endpoint}:{request.attr.cluster_name}:"
                                    f"{request.attr.attribute_name} from {device} failed")
                if response == item.verify:
                    self.success += 1
                    self.log(Status.INFO, f'verifying success, counter: {self.success}/{self.summary}')
                else:
                    raise Exception(f'request: {device} '
                                    f'endpoint:{endpoint}:'
                                    f'cluster:{request.attr.cluster_name}:'
                                    f'attribute:{request.attr.attribute_name} '
                                    f'verifying failed,'
                                    f'expect {item.verify}, actually {response}')
            except Exception as e:
                self.failed += 1
                self.log(Status.ERROR, str(e))
                self.update_result(Result.FAILED, f'{str(e)}, {self.success}/{self.summary}')

    def _get_code_value(self, info: Device, code):
        if not info:
            return None
        for item in info.status:
            if item.code == code:
                return item.value
        return None

    def _trigger_report(self, timestamp, code, device, endpoint, report: DCFZLTHRequest):
        for item in report.data:
            if not self._wait_interval_timeout(timestamp):
                return
            timestamp = int(time.time())
            # update attribute
            self.log(Status.INFO,
                     f'trigger {device}:{endpoint}:{report.attr.cluster_name}:{report.attr.attribute_name} update to {item.value}')
            if not self.zlth.write(device.mac, Attribute(
                    endpoint=endpoint,
                    cluster=report.attr.cluster,
                    server=True,
                    attribute=report.attr.attribute,
                    type=report.attr.type_name,
                    value=item.value,
                    manufacturer=report.attr.manufacturer,
                    manufacturer_code=report.attr.manufacturer_code
            )):
                self.log(Status.WARNING,
                         f"trigger update failed")
                continue
            try:
                # verify on IOT
                time.sleep(self.setting.validation)
                self.summary += 1
                # check hub is online
                if not self.tuya.is_online(self.setting.vid):
                    raise Exception("hub is offline")
                self.log(Status.INFO, f'verifying')
                info = self._check_device_status(device)
                value = self._get_code_value(info, code)
                if not value:
                    raise Exception(f'{device} {code} not found')
                if value == item.verify:
                    self.success += 1
                    self.log(Status.INFO, f'verifying success, counter: {self.success}/{self.summary}')
                else:
                    raise Exception(f'report: {device} '
                                    f'{code} '
                                    f'verifying failed, '
                                    f'expect {item.verify}, actually {value}')
            except Exception as e:
                self.failed += 1
                self.log(Status.ERROR, str(e))
                self.update_result(Result.FAILED, f'{str(e)}, {self.success}/{self.summary}')
