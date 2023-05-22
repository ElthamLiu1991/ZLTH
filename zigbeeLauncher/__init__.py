import os
from engineio.async_drivers import threading
from flask import Flask, render_template
from .database import db, ma
from .settings import DevelopmentConfig
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flasgger import Swagger

base_dir = os.path.abspath('./')

app = Flask(__name__,
            static_folder=os.path.join(base_dir, 'templates'),
            template_folder=os.path.join(base_dir, 'templates'),
            static_url_path='')

# app.jinja_env.variable_start_string = '{['
# app.jinja_env.variable_end_string = ']}'

CORS(app, supports_credentials=True)

socketio = SocketIO(app, async_mode="threading")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:fallback>')
def fallback(fallback):  # Vue Router 的 mode 为 'hash' 时可移除该方法
    if fallback.startswith('css/') or fallback.startswith('js/') \
            or fallback.startswith('img/') or fallback == 'favicon.ico':
        return app.render_template(fallback)
    else:
        return app.render_template('index.html')


def create_app(port):
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    ma.init_app(app)
    from .database.device import Device
    from .database.simulator import Simulator
    from .database.zigbee import Zigbee
    from .database.auto import Auto
    db.create_all(app=app)
    # from .api_2 import api as v2
    # app.register_blueprint(v2)
    set_swagger(app, port)
    from .api import api_blueprint
    app.register_blueprint(api_blueprint)
    # from .api_1 import api_blueprint
    # app.register_blueprint(api_blueprint)
    # run Simulator
    from .simulator import init
    init()
    from . import wait_response
    wait_response.init()
    # return app
    return socketio, app


def set_swagger(app, port):
    config = {
        "openapi": "3.0.3",
        "info": {
            "title": "ZLTH OpenAPI",
            "description": "This is the ZLTH OpenAPI",
            "version": "1.2.0"
        },
        "servers": [
            {
                "url": f"http://localhost:{port}"
            }
        ],
        "contact": {
            "email": "dengpan.liu@se.com"
        },
        "tags": [
            {
                "name": "Simulators",
                "description": "Everything about simulator"
            },
            {
                "name": "Devices",
                "description": "Everything about devices"
            },
            {
                "name": "Zigbees",
                "description": "Everything about Zigbee"
            },
            {
                "name": "Firmwares",
                "description": "Everything about firmware"
            },
            {
                "name": "Configs",
                "description": "Everything about configuration"
            },
            {
                "name": "Autos",
                "description": "Everything about automation testing"
            },
        ],
        "components": {
            "schemas": {
                "DevicesResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "integer",
                            "description": "error code",
                            "example": 200
                        },
                        "message": {
                            "type": "string",
                            "description": "error description",
                            "example": ""
                        },
                        "timestamp": {
                            "type": "integer",
                            "description": "message timestamp",
                            "example": 1684732490105
                        },
                        "uuid": {
                            "type": "string",
                            "description": "message UUID",
                            "example": "93a5d74c-f85f-11ed-9e16-1826492a4080"
                        },
                        "data":{
                            "type": "array",
                            "description": "devices information",
                            "items":{
                                "$ref":"#/components/schemas/Device"
                            }
                        }
                    }
                },
                "Device": {
                    "type": "object",
                    "properties": {
                        "configured": {
                            "type": "boolean",
                            "description": "device configuration state",
                            "example": "true"
                        },
                        "connected": {
                            "type": "boolean",
                            "description": "device online/offline state",
                            "example": "true"
                        },
                        "hwversion": {
                            "type": "string",
                            "description": "device hardware version",
                            "example": "1.0.1"
                        },
                        "ip": {
                            "type": "string",
                            "description": "simulator IP address this device belongs to",
                            "example": "192.168.1.100"
                        },
                        "label": {
                            "type": "string",
                            "description": "user label, maximum 63 characters",
                            "example": "this is my device"
                        },
                        "mac": {
                            "type": "string",
                            "description": "device MAC address",
                            "example": "94DEB8FFFEF119E1"
                        },
                        "state": {
                            "type": "integer",
                            "description": "device working state, 1=Uncommissioned, 2=Bootloader, 3=Upgrading, 4=Pairing, 5=Commissioning, 6=Joined, 7=Orphan, 8=Leaving, 9=Configuring",
                            "enum": [
                                1, 2, 3, 4, 5, 6, 7, 8, 9
                            ],
                            "example": 1
                        },
                        "swversion": {
                            "type": "string",
                            "description": "device firmware version",
                            "example": "1.0.6"
                        }
                    }
                }
            }
        }
    }
    Swagger(app, config=config, merge=True)
