import logging
from dataclasses import dataclass, asdict

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

    @dataclass
    class DataModel:
        ip: str
        mac: str
        name: str
        connected: bool
        state: int
        label: str
        configured: bool
        swversion: str
        hwversion: str

    def add(self, instance: DataModel):
        try:
            if self.retrieve():
                # self.delete()
                self.update(instance.__dict__)
            else:
                device = Device(**instance.__dict__)
                self._add(device)
        except Exception as e:
            log.warning("inset device to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self, many=True):
        return self._retrieve(DeviceSchema(many=many))


class DBSimulator(DBInterface):
    def __init__(self, **kwargs):
        super(DBSimulator, self).__init__(table=Simulator, **kwargs)

    @dataclass
    class DataModel:
        ip: str
        mac: str
        label: str
        version: str
        name: str
        connected: bool
        broker: str

    def add(self, instance: DataModel):
        try:
            if self.retrieve():
                # self.delete()
                # update
                self.update(instance.__dict__)
            else:
                simulator = Simulator(**instance.__dict__)
                self._add(simulator)
        except Exception as e:
            log.warning("inset simulator to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self, many=True):
        return self._retrieve(SimulatorSchema(many=many))


class DBZigbee(DBInterface):
    def __init__(self, **kwargs):
        super(DBZigbee, self).__init__(table=Zigbee, **kwargs)

    @dataclass
    class DataModel:
        mac: str
        device_type: str
        channel: int
        node_id: int
        pan_id: int
        extended_pan_id: str

    def add(self, instance: DataModel):
        try:
            if self.retrieve():
                self.delete()
            zigbee = Zigbee(**instance.__dict__)
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

    @dataclass
    class DataModel:
        script: str
        state: str
        result: str
        record: str
        config: str

    def add(self, instance: DataModel):
        try:
            if self.retrieve():
                # self.delete()
                # update
                self.update(**instance.__dict__)
            else:
                auto = Auto(**instance.__dict__)
                self._add(auto)
        except Exception as e:
            log.warning("inset auto to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(AutoSchema(many=True))
