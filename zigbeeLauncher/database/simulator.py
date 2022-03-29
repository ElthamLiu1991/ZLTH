from . import db, ma


class Simulator(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    ip = db.Column(db.String(20))
    name = db.Column(db.String(30))
    mac = db.Column(db.String(30))
    label = db.Column(db.String(50))
    connected = db.Column(db.Boolean())
    version = db.Column(db.String(10))

    def __init__(self, ip, name, mac, label, connected, version):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.label = label
        self.connected = connected
        self.version = version


class SimulatorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Simulator
        load_instance = True
