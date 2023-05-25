from . import db, ma


class Simulator(db.Model):
    ip = db.Column(db.String(20))
    name = db.Column(db.String(30))
    mac = db.Column(db.String(30), primary_key=True)
    label = db.Column(db.String(50))
    connected = db.Column(db.Boolean())
    version = db.Column(db.String(10))
    broker = db.Column(db.String(20))
    port = db.Column(db.INTEGER())

    def __init__(self, ip=None, name=None, mac=None, label=None, connected=None, version=None, broker=None, port=None):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.label = label
        self.connected = connected
        self.version = version
        self.broker = broker
        self.port = port


class SimulatorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Simulator
        load_instance = True
