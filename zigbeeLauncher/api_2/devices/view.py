import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from . import devices
from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import dongle_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import pack_response
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError


class DevicesResource(Resource):
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
                return pack_response(0, DBDevice(**paras).retrieve())
            except Exception as e:
                logger.exception("request error")
                return pack_response(90000, error="bad parameters:"+str(request.args)), 500
        return pack_response(0, DBDevice().retrieve())
        # return render_template('show_all_devices.html', devices=Device.query.all())


def label_command(ip, device, body):
    """
    1. 验证payload是否提供完全
    2. 验证各项数据是否合法
    """
    schema = {
    }
    try:
        validate(instance=body, schema=schema, format_check=draft7_format_checker)
    except SchemaError as e:
        logger.exception('json validation failed, %s', str(e))
        return pack_response(90003, error=str(e)), 500
    except ValidationError as e:
        logger.exception('illegal schema:%s', str(e))
        return pack_response(90004, error=str(e)), 500
    else:
        dongle_command_2(ip, device, body)
        return pack_response(0), 200


identify_schema = {
            "type": "object",
            "properties": {
              "identify": {
                "type": "object",
                "properties": {},
                "description": "identify command"
              }
            },
            "required": [
              "identify"
            ]
          }

reset_schema = {
            "type": "object",
            "properties": {
              "reset": {
                "type": "object",
                "properties": {},
                "description": "reset command"
              }
            },
            "required": [
              "reset"
            ]
          }

label_schema = {
                "type": "object",
                "properties": {
                  "label": {
                    "type": "object",
                    "properties": {
                      "data": {
                        "type": "string",
                        "description": "label data"
                      }
                    },
                    "required": [
                      "data"
                    ],
                    "description": "label command"
                  }
                },
                "required": [
                  "label"
                ]
              }


class DeviceResource(Resource):

    commands = ['identify', 'reset', 'label']

    def get(self, mac):
        if DBDevice(mac=mac).retrieve():
            return pack_response(0, DBDevice(mac=mac).retrieve()[0]), 200
        else:
            return pack_response(10000, device=mac), 404

    def put(self, mac):
        args = request.get_json()
        device = DBDevice(mac=mac).retrieve()
        if device:
            try:
                state = device[0]['state']
                if state == 2 or state == 3:
                    return pack_response(10002, device=mac), 500
                connected = device[0]['connected']
                ip = device[0]['ip']
                if connected:
                    for key in args.keys():
                        if key not in self.commands:
                            return pack_response(90002, command=key), 500
                    for key in args.keys():
                        try:
                            validate(instance=args, schema=eval(key+'_schema'),
                                     format_checker=draft7_format_checker)
                        except SchemaError as e:
                            logger.exception('illegal schema: %s', e.message)
                            return pack_response(90003, error=e.message)
                        except ValidationError as e:
                            logger.exception('json validation failed:%s', e.message)
                            return pack_response(90004, error=e.message)
                        else:
                            dongle_command_2(ip, mac, args)
                    return pack_response(0), 200
                else:
                    return pack_response(10001, device=mac), 500
            except Exception as e:
                return pack_response(90000, error=str(e)), 500
        else:
            return pack_response(10000, device=mac), 404
