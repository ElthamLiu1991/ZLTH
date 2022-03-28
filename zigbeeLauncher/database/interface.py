import logging

from flask import current_app

from . import db
from .device import Device, DeviceSchema
from zigbeeLauncher.logging import databaseLogger as log
from zigbeeLauncher import app
from .simulator import Simulator


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

    def _retrieve(self):
        with app.app_context():
            device_schema = DeviceSchema(many=True)
            if self.filter:
                result = self.table.query.filter_by(**self.filter)
            else:
                result = self.table.query.all()
            return device_schema.dump(result)


class DBDevice(DBInterface):
    def __init__(self, **kwargs):
        super(DBDevice, self).__init__(table=Device, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                # update
                self.update(data)
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
        return self._retrieve()


class DBSimulator(DBInterface):
    def __init__(self, **kwargs):
        super(DBSimulator, self).__init__(table=Simulator, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                # update
                self.update(data)
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
        return self._retrieve()
