import time

import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from jsonschema import validate, draft7_format_checker

from ..util import send_command
from zigbeeLauncher.exceptions import exception, InvalidRequest, DeviceNotFound, DeviceOffline, Unsupported, InvalidPayload


class SimulatorsResource(Resource):
    """
    /simulators or /simulators?ip=192.168.121.1
    """
    def get(self):
        @exception
        def handle():
            paras = request.args
            simulators = DBSimulator(**paras).retrieve()

            for simulator in simulators:
                simulator['devices'] = []
                # 获取devices
                devices = DBDevice(ip=simulator['ip']).retrieve()
                for device in devices:
                    simulator['devices'].append(device['mac'])
            # return Response(data=simulators).pack()
            return simulators

        return handle()


class SimulatorResource(Resource):
    """
    /simulators/<mac>
    """
    def get(self, mac):
        @exception
        def handle():
            simulator = DBSimulator(mac=mac).retrieve()
            if not simulator:
                raise DeviceNotFound(mac)
            else:
                simulator = simulator[0]
                simulator['devices'] = []
                # 获取devices
                devices = DBDevice(ip=simulator['ip']).retrieve()
                for device in devices:
                    simulator['devices'].append(device['mac'])
                return simulator

        return handle()

    def put(self, mac):
        commands = ['label']
        schema = {
            "type": "object",
            "properties": {
                "label": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "label"
                        }
                    },
                    "description": "label modification request",
                    "required": [
                        "data"
                    ]
                }
            }
        }

        @exception
        def handle():
            simulator = DBSimulator(mac=mac).retrieve()
            if not simulator:
                raise DeviceNotFound(mac)
            else:
                simulator = simulator[0]
                if not simulator.get('connected'):
                    raise DeviceOffline(mac)
                try:
                    validate(instance=request.get_json(), schema=schema,
                             format_checker=draft7_format_checker)
                except Exception as e:
                    raise InvalidPayload(e.description)
                for k, v in request.get_json().items():
                    if k not in commands:
                        raise Unsupported(k)
                    return send_command(ip=simulator.get('ip'), command={k: v})

        return handle()
