import logging

from flask import current_app

from . import db
from .auto import AutoSchema, Auto
from .device import Device, DeviceSchema
from zigbeeLauncher.logging import databaseLogger as log
from zigbeeLauncher import app
from .simulator import Simulator, SimulatorSchema
from .zigbee import Zigbee, ZigbeeSchema


class DBInterface:
    def __init__(self, table, **kwargs):
        self.table = table
        self.filter = kwargs

    def _add(self, data):
        try:
            with app.app_context():
                db.session.add(data)
                db.session.commit()
        except Exception as e:
            log.warning("failed to insert data:%s", e)
            db.session.rollback()

    def _update(self, data):
        try:
            with app.app_context():
                self.table.query.filter_by(**self.filter).update(data)
                db.session.commit()
        except Exception as e:
            log.warning("failed to update data:%s", e)
            db.session.rollback()
        pass

    def _delete(self):
        try:
            with app.app_context():
                if self.table.query.filter_by(**self.filter).delete():
                    db.session.commit()
        except Exception as e:
            log.warning("failed to delete data:%s", e)
            db.session.rollback()
        pass

    def _retrieve(self, schema):
        with app.app_context():
            if self.filter:
                result = self.table.query.filter_by(**self.filter)
            else:
                result = self.table.query.all()
            return schema.dump(result)


class DBDevice(DBInterface):
    def __init__(self, **kwargs):
        super(DBDevice, self).__init__(table=Device, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                # self.delete()
                self.update({
                    'ip': data['ip'],
                    'name': data['name'],
                    'mac': data['mac'],
                    'label': data['label'],
                    'connected': data['connected'],
                    'configured': data['configured'],
                    'state': data['state'],
                    'swversion': data['swversion'],
                    'hwversion': data['hwversion']
                })
            else:
                device = Device(data["ip"],
                                data["name"],
                                data["mac"],
                                data["label"],
                                data["connected"],
                                data["configured"],
                                data["state"],
                                data["swversion"],
                                data["hwversion"])
                self._add(device)
        except Exception as e:
            log.warning("inset device to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(DeviceSchema(many=True))


class DBSimulator(DBInterface):
    def __init__(self, **kwargs):
        super(DBSimulator, self).__init__(table=Simulator, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                # self.delete()
                # update
                self.update({
                    'ip': data['ip'],
                    'name': data['name'],
                    'mac': data['mac'],
                    'label': data['label'],
                    'connected': data['connected'],
                    'version': data['version']
                })
            else:
                simulator = Simulator(data["ip"],
                                      data["name"],
                                      data["mac"],
                                      data["label"],
                                      data["connected"],
                                      data["version"])
                self._add(simulator)
        except Exception as e:
            log.warning("inset simulator to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(SimulatorSchema(many=True))


class DBZigbee(DBInterface):
    def __init__(self, **kwargs):
        super(DBZigbee, self).__init__(table=Zigbee, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                self.delete()
            zigbee = Zigbee(data['mac'],
                            data['device_type'],
                            data['channel'],
                            data['pan_id'],
                            hex(data['extended_pan_id'])[2:],
                            data['node_id'])
            self._add(zigbee)
        except Exception as e:
            log.exception("inset zigbee to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(ZigbeeSchema(many=True))


class DBAuto(DBInterface):
    def __init__(self, **kwargs):
        super(DBAuto, self).__init__(table=Auto, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                # self.delete()
                # update
                self.update({
                    'script': data['script'],
                    'state': data['state'],
                    'status': data['status'],
                    'record': data['record'],
                    'config': data['config'],
                })
            else:
                auto = Auto(data["script"],
                            data["state"],
                            data['status'],
                            data["record"],
                            data["config"])
                self._add(auto)
        except Exception as e:
            log.warning("inset auto to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(AutoSchema(many=True))
