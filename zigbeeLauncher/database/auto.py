from . import db, ma


class Auto(db.Model):
    id = db.Column("id", db.Integer(), primary_key=True)
    script = db.Column(db.String())
    state = db.Column(db.String())
    result = db.Column(db.String())
    record = db.Column(db.String())
    config = db.Column(db.String())

    def __init__(self, script, state, result, record, config):
        self.script = script
        self.state = state
        self.result = result
        self.record = record
        self.config = config


class AutoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Auto
        load_instance = True
