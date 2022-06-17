import time

import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from . import simulators
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from zigbeeLauncher.mqtt.Launcher_API import simulator_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import pack_response
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
                return pack_response({'code': 90000}, status=500, error="bad parameters:" + str(request.args))
        else:
            items = DBSimulator().retrieve()
        for simulator in items:
            simulator['devices'] = []
            # 获取devices
            devices = DBDevice(ip=simulator['ip']).retrieve()
            for device in devices:
                simulator['devices'].append(device['mac'])
        return pack_response({'code': 0, 'response': items})
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
            return pack_response({'code': 0, 'response': simulator})
        else:
            return pack_response({'code': 20000}, status=404, device=mac)

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
                            return pack_response({'code': 90002}, 500, command=key)
                    for key in args.keys():
                        try:
                            validate(instance=args, schema=self.schema,
                                     format_checker=draft7_format_checker)
                        except SchemaError as e:
                            logger.exception('illegal schema: %s', e.message)
                            return pack_response({'code': 90003}, status=500, error=e.message)
                        except ValidationError as e:
                            logger.exception('json validation failed:%s', e.message)
                            return pack_response({'code': 90004}, status=500, error=e.message)
                        else:
                            response = simulator_command_2(ip, args)
                            code = response['code']
                            if code != 0:
                                return pack_response(response, status=500)
                            else:
                                return pack_response(response)
                else:
                    return pack_response({'code': 20001}, status=500, device=mac)
            except Exception as e:
                return pack_response({'code': 90000}, status=500, error=str(e))
        else:
            return pack_response({'code': 20000}, status=404, device=mac)
