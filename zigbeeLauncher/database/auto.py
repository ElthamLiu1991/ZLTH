from . import db, ma


class Auto(db.Model):
    id = db.Column("id", db.Integer(), primary_key=True)
    script = db.Column(db.String())
    state = db.Column(db.String())
    status = db.Column(db.String())
    record = db.Column(db.String())
    config = db.Column(db.String())

    def __init__(self, script, state, status, record, config):
        self.script = script
        self.state = state
        self.status = status
        self.record = record
        self.config = config


class AutoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Auto
        load_instance = True
