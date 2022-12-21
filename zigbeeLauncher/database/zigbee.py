from . import db, ma


class Zigbee(db.Model):
    mac = db.Column(db.String(30), primary_key=True)
    device_type = db.Column(db.String(15))
    channel = db.Column(db.Integer())
    pan_id = db.Column(db.Integer())
    extended_pan_id = db.Column(db.String(32))
    node_id = db.Column(db.Integer())

    def __init__(self, mac, device_type, channel, pan_id, extended_pan_id, node_id):
        self.mac = mac
        self.device_type = device_type
        self.channel = channel
        self.pan_id = pan_id
        self.extended_pan_id = str(extended_pan_id)
        self.node_id = node_id


class ZigbeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Zigbee
        load_instance = True

