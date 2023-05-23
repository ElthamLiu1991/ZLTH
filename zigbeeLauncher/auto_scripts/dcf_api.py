import json
import os
from dataclasses import dataclass
from typing import Any, Optional

from dacite import from_dict

from zigbeeLauncher import base_dir
from zigbeeLauncher.logging import autoLogger as logger
from zigbeeLauncher.zigbee.data_type import data_type_name_table


@dataclass
class DCFAttribute:
    manufacturer: bool
    manufacturer_code: int
    cluster: int
    cluster_name: str
    attribute: int
    attribute_name: Optional[str]
    type: int
    type_name: Optional[str]
    reportable: bool
    remote: bool


@dataclass
class DCFZLTHData:
    value: Any
    verify: Any


@dataclass
class DCFZLTHRequest:
    domain: str
    attribute: str
    data: list[DCFZLTHData]
    attr: Optional[DCFAttribute]


@dataclass
class DCFZLTHSetting:
    endpoint: int
    requestable: bool
    request: Optional[DCFZLTHRequest]
    reportable: bool
    report: Optional[DCFZLTHRequest]
    pid: Optional[list[str]]


class DCFAPI:
    def __init__(self, device, functions=[]):
        self.device = device
        self.functions = functions
        self.setting = {}
        self.ready = True
        self.load_dcf()

    def load_dcf(self):
        try:
            functions = self.functions.copy()
            logger.info(f"load zlth {functions}")
            with open(os.path.join(base_dir, 'dcf/'+self.device+'.json'), encoding='utf-8') as f:
                dcf_device = json.loads(f.read())
                for k, v in dcf_device['zlth'].items():
                    if not functions:
                        break
                    if k not in functions:
                        continue
                    setting = from_dict(data_class=DCFZLTHSetting, data=v)
                    if not setting:
                        logger.error(f"zlth decode {k} failed")
                        break
                    if setting.request:
                        dcf_attribute = self.load_attribute(setting.request.domain, setting.request.attribute)
                        if not dcf_attribute:
                            logger.error(f"dcf attribute decode {setting.request.domain} {setting.request.attribute} failed")
                            break
                        # setting.request.__dict__.update({'attribute': dcf_attribute})
                        setting.request.attr = dcf_attribute
                    if setting.report:
                        dcf_attribute = self.load_attribute(setting.report.domain, setting.report.attribute)
                        if not dcf_attribute:
                            logger.error(f"dcf attribute decode {setting.report.domain} {setting.report.attribute} failed")
                            break
                        dcf_attribute.type_name = data_type_name_table.get(dcf_attribute.type)
                        dcf_attribute.attribute_name = k
                        # setting.report.__dict__.update({'attribute': dcf_attribute})
                        setting.report.attr = dcf_attribute
                    # get pid
                    for env, pid in dcf_device['tuya']['pid'].items():
                        if setting.pid:
                            setting.pid.append(pid)
                        else:
                            setting.pid = [pid]

                    self.setting[k] = setting
                    functions.remove(k)
                if functions:
                    logger.error(f"zlth pack {functions} failed")
                    self.ready = False
        except Exception:
            logger.exception("load dcf device failed:")

    def load_attribute(self, domain, attribute):
        try:
            with open(os.path.join(base_dir, 'dcf/'+domain+'.json'), encoding='utf-8') as f:
                dcf_domain = json.loads(f.read())
                for name, setting in dcf_domain['attributes']['zigbee'].items():
                    if name == attribute:
                        return from_dict(data_class=DCFAttribute, data=setting)
        except Exception:
            logger.exception(f"load dcf attribute failed:")
            return None