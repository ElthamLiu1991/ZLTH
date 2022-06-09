from . import db, ma


class Zigbee(db.Model):
    mac = db.Column(db.String(30), primary_key=True)
    device_type = db.Column(db.String(15))
    channel = db.Column(db.Integer())
    pan_id = db.Column(db.String())
    extended_pan_id = db.Column(db.String(16))
    node_id = db.Column(db.String())

    def __init__(self, mac, device_type, channel, pan_id, extended_pan_id, node_id):
        self.mac = mac
        self.device_type = device_type
        self.channel = channel
        self.pan_id = pan_id
        self.extended_pan_id = extended_pan_id
        self.node_id = node_id


class ZigbeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Zigbee
        load_instance = True


class ZigbeeEndpoint(db.Model):
    id = db.Column('id', db.Integer(), primary_key=True)
    mac = db.Column(db.String(30))
    endpoint = db.Column(db.Integer())
    profile = db.Column(db.String(5))
    device_id = db.Column(db.String(5))
    device_version = db.Column(db.Integer())

    def __init__(self, mac, endpoint, profile, device_id, device_version):
        self.mac = mac
        self.endpoint = endpoint
        self.profile = profile
        self.device_id = device_id
        self.device_version = device_version


class ZigbeeEndpointSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ZigbeeEndpoint
        load_instance = True


class ZigbeeEndpointCluster(db.Model):
    id = db.Column('id', db.Integer(), primary_key=True)
    mac = db.Column(db.String(30))
    endpoint = db.Column(db.Integer())
    server = db.Column(db.Boolean())
    cluster = db.Column(db.String(5))
    manufacturer = db.Column(db.Boolean())
    manufacturer_code = db.Column(db.String(5))
    name = db.Column(db.String(30))

    def __init__(self, mac, endpoint, server, cluster, manufacturer,
                 manufacturer_code, name):
        self.mac = mac
        self.endpoint = endpoint
        self.server = server
        self.cluster = cluster
        self.manufacturer = manufacturer
        self.manufacturer_code = manufacturer_code
        self.name = name


class ZigbeeEndpointClusterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ZigbeeEndpointCluster
        load_instance = True


class ZigbeeEndpointClusterAttribute(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    mac = db.Column(db.String(30))
    endpoint = db.Column(db.Integer())
    server = db.Column(db.Boolean())
    cluster = db.Column(db.String(5))
    attribute = db.Column(db.String(5))
    type = db.Column(db.String(2))
    value = db.Column(db.String(30))
    name = db.Column(db.String(30))

    def __init__(self, mac, endpoint, server, cluster, attribute, type, value, name):
        self.mac = mac
        self.endpoint = endpoint
        self.server = server
        self.cluster = cluster
        self.attribute = attribute
        self.type = type
        self.value = value
        self.name = name


class ZigbeeEndpointClusterAttributeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ZigbeeEndpointClusterAttribute
        load_instance = True
