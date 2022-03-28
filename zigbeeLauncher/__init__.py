from flask import Flask
from .database import db, ma
from .settings import DevelopmentConfig


app = Flask(__name__)


def create_app():

    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    ma.init_app(app)
    from .database.device import Device
    from .database.simulator import Simulator
    db.create_all(app=app)
    from .api_1 import api as v1
    app.register_blueprint(v1)
    # run Simulator
    from .mqtt import init
    init("simulator")
    init("launcher")
    return app
