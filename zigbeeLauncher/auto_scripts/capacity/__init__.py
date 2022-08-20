import json
import os
import threading
import time

from zigbeeLauncher.auto_scripts import PREPARING, ERROR, INFO, WORKING, START, WARNING, DONE, FINISH, SUCCESS, FAILED, \
    auto_record, STOP
from zigbeeLauncher.auto_scripts.tuya_api import *
from zigbeeLauncher.auto_scripts.zlth_api import *
from zigbeeLauncher.logging import autoLogger as logger
from zigbeeLauncher import base_dir, socketio

SCRIPT = 'capacity'


class Testing(threading.Thread):
    _script = 'capacity'
    _status = SUCCESS
    _repeat = 1
    _batch = 1
    _stop = False
    _dongles = []

    def name(self):
        return self._script

    def __init__(self, status_callback=None):
        threading.Thread.__init__(self)
        with open(os.path.join(base_dir, 'scripts/capacity.json'), encoding='utf-8') as f:
            self.config = json.loads(f.read())
        self.status_update = status_callback

    def preparing(self):
        if self.status_update:
            self.status_update(PREPARING, self._status)
        try:
            auto_record(PREPARING, INFO, 'preparing testing environment')
            if 'gateway_vid' not in self.config:
                auto_record(PREPARING, ERROR, 'failed to get gateway virtual id')
                logger.error('Please provide gateway virtual id')
                raise
            if not set_gateway_vid(self.config['gateway_vid']):
                auto_record(PREPARING, ERROR, 'failed to get tuya token')
                logger.error('Get tuya token failed')
                raise
                # check gateway status
            if not get_gateway_online_state():
                auto_record(PREPARING, ERROR, 'gateway is offline')
                logger.error('Gateway is offline')
                raise
            if 'repeat' in self.config:
                self._repeat = self.config['repeat'] + 1
            if 'batch' in self.config:
                self._batch = self.config['batch']
            # get dongles list
            result, dongles = get_devices()
            if not result:
                auto_record(PREPARING, ERROR, 'ZLTH service not response')
                logger.error("ZLTH not response")
                raise
            if not dongles:
                auto_record(PREPARING, ERROR, 'not available ZLTH dongle')
                logger.error("Not available ZLTH dongles")
                raise
            auto_record(PREPARING, INFO, 'preparing testing environment Done')
            auto_record(PREPARING, INFO,
                        '{} testing ready, ZLTH dongles: {}, batch: {}, repeat: {}'.format(
                            self._script, len(dongles), self._batch, self._repeat - 1))

        except RuntimeError as e:
            logger.error("preparing failed, finish")
            self._status = FAILED
            if self.status_update:
                self.status_update(PREPARING, self._status)
            return False
        return True

    def stop(self):
        self._stop = True

    def run(self):
        if self.status_update:
            self.status_update(WORKING, self._status)
        iterate = 0
        while not self._stop and iterate < self._repeat:
            auto_record(START, INFO, 'Iterate:{}'.format(iterate))
            auto_record(WORKING, INFO, "reset devices ...")
            devices = get_sub_devices()
            # leave devices from tuya
            self.leave_device_from_tuya(devices)
            # leave device from ZLTH
            self.leave_device_from_zlth()
            auto_record(WORKING, INFO, "reset devices done")
            time.sleep(5)
            result, self._dongles = get_devices()
            offset = 0
            retry = 5
            verify_list = []
            try:
                while not self._stop:
                    if not self.adding(retry):
                        if retry == 0:
                            raise
                        retry -= 1
                        time.sleep(2)
                        continue
                    pending = []
                    offset = self.joining(pending, offset)
                    if not pending:
                        break
                    verify_list = verify_list + pending
                    if not self.checking(pending):
                        self._status = FAILED
                    self.close()
                    if self._stop:
                        break
                    if offset == len(self._dongles) - 1:
                        break
                if self.verify(verify_list):
                    if self._stop:
                        break
                    auto_record(DONE, INFO, "Iterate:{} {}".format(iterate, SUCCESS))
                else:
                    self._status = FAILED
                    auto_record(DONE, INFO, "Iterate:{} {}".format(iterate, FAILED))
                iterate += 1
            except RuntimeError as e:
                self._status = FAILED
                break
        if self._stop:
            self._status = STOP
            auto_record(FINISH, INFO, STOP)
        elif self._status == FAILED:
            auto_record(FINISH, ERROR, FAILED)
        else:
            auto_record(FINISH, INFO, SUCCESS)
        if self.status_update:
            self.status_update(FINISH, self._status)

    def leave_device_from_tuya(self, devices):
        auto_record(WORKING, INFO, "unregister devices from APP ...")
        for device in devices:
            # auto_record(WORKING, INFO, "unregister {} from APP ...".format(device['node_id'].upper()))
            delete_device(device['id'])
            # auto_record(WORKING, INFO, "unregister {} from Done".format(device['node_id'].upper()))
        auto_record(WORKING, INFO, 'unregister devices from APP done')

    def leave_device_from_zlth(self):
        auto_record(WORKING, INFO, "leaving network from ZLTH ...")
        result, self._dongles = get_devices()
        for device in self._dongles:
            mac = device['mac']
            if device['state'] != 1:
                # auto_record(WORKING, INFO, "leaving network {} ...".format(mac))
                result, data = device_leave(mac)
                if not result:
                    auto_record(WORKING, WARNING, "leaving network {} failed".format(mac))
                    logger.warning("%s leave network failed", mac)
                # auto_record(WORKING, INFO, "leaving network {} done".format(mac))
        auto_record(WORKING, INFO, "leaving network from ZLTH done")

    def adding(self, retry):
        # open permit join
        auto_record(WORKING, INFO, "open permit join window[{}] ...".format(retry))
        if not permit_join(180):
            auto_record(WORKING, WARNING, "open permit join window[{}] failed".format(retry))
            logger.error("Send permit jon command failed")
            return False
        time.sleep(1)
        if not get_gateway_permit_join_state():
            auto_record(WORKING, WARNING, "open permit join window[{}] failed".format(retry))
            logging.error("Open permit join window failed")
            return False
        auto_record(WORKING, INFO, "open permit join window[{}] done".format(retry))
        return True

    def close(self):
        # open permit join
        auto_record(WORKING, INFO, "close permit join window ...")
        if not permit_join(0):
            auto_record(WORKING, WARNING, "close permit join window failed")
            logger.error("Send permit jon command failed")
            return False
        time.sleep(1)
        if get_gateway_permit_join_state():
            auto_record(WORKING, WARNING, "close permit join window failed")
            logging.error("close permit join window failed")
            return False
        auto_record(WORKING, INFO, "close permit join window done")
        return True

    def joining(self, pending, offset):
        new_offset = 0
        batch = self._batch
        logger.info("Add %s devices at once", self._batch)
        auto_record(WORKING, INFO, "add {} devices ...".format(self._batch))
        for index, device in enumerate(self._dongles):
            if offset != 0 and index <= offset:
                continue
            new_offset = index
            if batch == 0:
                break
            mac = device['mac']
            connected = device['connected']
            state = device['state']
            if not connected:
                auto_record(WORKING, WARNING, "device {} is offline".format(mac))
                logger.warning("Dongle %s is offline", mac)
                continue
            if state != 1:
                auto_record(WORKING, WARNING, "device {} is not ready".format(mac))
                logger.warning("Dongle %s is not ready for joining:%d", mac, state)
                continue
            auto_record(WORKING, INFO, "adding {} to network ..".format(mac))
            result, response = device_join(mac)
            if not result:
                auto_record(WORKING, ERROR, "device {} not response".format(mac))
                logger.error("Trigger dongle %s joining failed", mac)
                continue
            batch -= 1
            pending.append(mac)
        auto_record(WORKING, INFO, "add {} devices done".format(self._batch))
        return new_offset

    def checking(self, pending):
        logger.info("Waiting for commissioned")
        auto_record(WORKING, INFO, "check device registration on tuya ...")
        while not self._stop and get_gateway_permit_join_state():
            # get device list from tuya
            devices = get_sub_devices()
            for device in devices:
                mac = device['node_id'].upper()
                if mac in pending and device['online']:
                    auto_record(WORKING, INFO, "device {} registered".format(mac))
                    logger.info("Device %s registered", mac)
                    # check state in dongle
                    result, data = get_device(mac)
                    if not result:
                        auto_record(WORKING, ERROR, "device {} not exist".format(mac))
                    elif data['state'] != 6:
                        auto_record(WORKING, ERROR, "device {} not commissioned".format(mac))
                        logger.error("Device %s commission failed", mac)
                    else:
                        auto_record(WORKING, INFO, "device {} commissioned".format(mac))
                        pending.remove(mac)
            if not pending:
                auto_record(WORKING, INFO, "check device registration on tuya done")
                return True
            time.sleep(5)
        if self._stop:
            return True
        auto_record(WORKING, ERROR, "permit jon timeout, {} not registered".format(pending))
        logger.error("Permit join timeout, %s join failed", pending)
        return False

    def verify(self, devices):
        ret = True
        auto_record(WORKING, INFO, "verify all devices state ...")
        for mac in devices:
            if self._stop:
                return True
            result, data = get_device(mac)
            if not result:
                auto_record(WORKING, ERROR, "device {} not exist".format(mac))
                ret = False
            elif data['state'] != 6:
                auto_record(WORKING, ERROR, "device {} not commissioned".format(mac))
                ret = False
                logger.error("Device %s commission failed", mac)
        auto_record(WORKING, INFO, "verify all devices state done")
        return ret
