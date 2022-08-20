import os

from flask import Flask, render_template
from .database import db, ma
from .settings import DevelopmentConfig
from flask_cors import CORS
from flask_socketio import SocketIO, emit

base_dir = os.path.abspath('./')

app = Flask(__name__,
            static_folder=os.path.join(base_dir, 'templates'),
            template_folder=os.path.join(base_dir, 'templates'),
            static_url_path='')

app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

CORS(app, supports_credentials=True)

socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:fallback>')
def fallback(fallback):       # Vue Router 的 mode 为 'hash' 时可移除该方法
    if fallback.startswith('css/') or fallback.startswith('js/')\
            or fallback.startswith('img/') or fallback == 'favicon.ico':
        return app.render_template(fallback)
    else:
        return app.render_template('index.html')


def create_app():
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    ma.init_app(app)
    from .database.device import Device
    from .database.simulator import Simulator
    from .database.zigbee import Zigbee, ZigbeeEndpoint
    db.create_all(app=app)
    from .api_2 import api as v2
    app.register_blueprint(v2)
    # run Simulator
    from .mqtt import init
    init()
    from . import request_and_response
    request_and_response.init()
    #return app
    return socketio, app
