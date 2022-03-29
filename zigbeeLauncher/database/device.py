from . import db, ma


class Device(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    ip = db.Column(db.String(20))
    name = db.Column(db.String(30))
    mac = db.Column(db.String(30))
    label = db.Column(db.String(50))
    connected = db.Column(db.Boolean())
    configured = db.Column(db.Boolean())
    state = db.Column(db.Integer())
    swversion = db.Column(db.String(10))
    hwversion = db.Column(db.String(10))

    def __init__(self, ip, name, mac, label, connected, configured, state,
                 swversion, hwversion):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.label = label
        self.connected = connected
        self.configured = configured
        self.state = state
        self.swversion = swversion
        self.hwversion = hwversion


class DeviceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Device
        load_instance = True
