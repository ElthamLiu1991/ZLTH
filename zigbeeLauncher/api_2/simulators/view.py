import time

import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from . import simulators
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from zigbeeLauncher.mqtt.Launcher_API import simulator_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import Response
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError


class SimulatorsResource(Resource):

    def get(self):
        """
        获取数据库device表并传给前端
        :return: device所有数据
        """
        if request.args:
            try:
                paras = {}
                for key in request.args:
                    paras[key] = request.args[key]
                items = DBSimulator(**paras).retrieve()
            except Exception as e:
                logger.exception("request error")
                return Response("bad parameters:" + str(request.args), code=90000).pack()
        else:
            items = DBSimulator().retrieve()
        for simulator in items:
            simulator['devices'] = []
            # 获取devices
            devices = DBDevice(ip=simulator['ip']).retrieve()
            for device in devices:
                simulator['devices'].append(device['mac'])
        return Response(data=items).pack()
        # return render_template('show_all_devices.html', devices=Device.query.all())


class SimulatorResource(Resource):
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

    def get(self, mac):
        if DBSimulator(mac=mac).retrieve():
            simulator = DBSimulator(mac=mac).retrieve()[0]
            simulator['devices'] = []
            # 获取devices
            devices = DBDevice(ip=simulator['ip']).retrieve()
            for device in devices:
                simulator['devices'].append(device['mac'])
            return Response(data=simulator).pack()
        else:
            return Response(mac, code=20000).pack()

    def put(self, mac):
        args = request.get_json()
        simulator = DBSimulator(mac=mac).retrieve()
        if simulator:
            try:
                connected = simulator[0]['connected']
                ip = simulator[0]['ip']
                if connected:
                    for key in args.keys():
                        if key not in self.commands:
                            return Response(key, code=90002).pack()
                    for key in args.keys():
                        if key == 'label':
                            # label size should not more than 64 characters
                            if len(args[key]['data']) > 63:
                                return Response('data', code=90005).pack()
                        try:
                            validate(instance=args, schema=self.schema,
                                     format_checker=draft7_format_checker)
                        except SchemaError as e:
                            logger.exception('illegal schema: %s', e.message)
                            return Response(e.message, code=90003).pack()
                        except ValidationError as e:
                            logger.exception('json validation failed:%s', e.message)
                            return Response(e.message, code=90004).pack()
                        else:
                            response = simulator_command_2(ip, args)
                            return Response(**response).pack()
                else:
                    return Response(mac, code=20001).pack()
            except Exception as e:
                return Response(str(e), code=90000).pack()
        else:
            return Response(mac, code=20000).pack()
