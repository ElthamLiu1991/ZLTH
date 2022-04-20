import logging

from flask import current_app

from . import db
from .device import Device, DeviceSchema
from zigbeeLauncher.logging import databaseLogger as log
from zigbeeLauncher import app
from .simulator import Simulator, SimulatorSchema
from .zigbee import Zigbee, ZigbeeSchema, ZigbeeEndpoint, ZigbeeEndpointSchema, ZigbeeEndpointCluster, \
    ZigbeeEndpointClusterSchema, ZigbeeEndpointClusterAttribute, ZigbeeEndpointClusterAttributeSchema


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
                self.delete()
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
                self.delete()
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
                            data['extended_pan_id'],
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


class DBZigbeeEndpoint(DBInterface):
    def __init__(self, **kwargs):
        super(DBZigbeeEndpoint, self).__init__(table=ZigbeeEndpoint, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                self.delete()
            zigbeeEndpoint = ZigbeeEndpoint(data['mac'],
                                            data['endpoint'],
                                            data['profile'],
                                            data['device_id'],
                                            data['device_version'])
            self._add(zigbeeEndpoint)
        except Exception as e:
            log.exception("inset zigbeeEndpoint to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(ZigbeeEndpointSchema(many=True))


class DBZigbeeEndpointCluster(DBInterface):
    def __init__(self, **kwargs):
        super(DBZigbeeEndpointCluster, self).__init__(table=ZigbeeEndpointCluster, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                self.delete()
            zigbeeEndpointCluster = ZigbeeEndpointCluster(data['mac'],
                                                          data['endpoint'],
                                                          data['server'],
                                                          data['cluster'],
                                                          data['manufacturer'],
                                                          data["manufacturer_code"],
                                                          data['name'])
            self._add(zigbeeEndpointCluster)
        except Exception as e:
            log.exception("inset zigbeeEndpointCluster to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(ZigbeeEndpointClusterSchema(many=True))


class DBZigbeeEndpointClusterAttribute(DBInterface):
    def __init__(self, **kwargs):
        super(DBZigbeeEndpointClusterAttribute, self).__init__(table=ZigbeeEndpointClusterAttribute, **kwargs)

    def add(self, data):
        try:
            if self.retrieve():
                self.delete()
            zigbeeEndpointClusterAttribute = ZigbeeEndpointClusterAttribute(data['mac'],
                                                                            data['endpoint'],
                                                                            data['server'],
                                                                            data['cluster'],
                                                                            data['attribute'],
                                                                            data['type'],
                                                                            data['value'],
                                                                            data['name'])
            self._add(zigbeeEndpointClusterAttribute)
        except Exception as e:
            log.exception("inset zigbeeEndpointClusterAttribute to database failed:%s", e)

    def update(self, data):
        self._update(data)

    def delete(self):
        self._delete()

    def retrieve(self):
        return self._retrieve(ZigbeeEndpointClusterAttributeSchema(many=True))
