import os

import rapidjson
import werkzeug
import yaml
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from . import devices
from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import dongle_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import pack_response
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError
from ..json_schemas import config_schema

from ..util import check_device_exist, check_device_state
from ... import base_dir


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
                return pack_response({'code':0, 'response':DBDevice(**paras).retrieve()})
            except Exception as e:
                logger.exception("request error")
                return pack_response({'code':90000}, status=500, error="bad parameters:"+str(request.args))
        return pack_response({'code':0, 'response':DBDevice().retrieve()})
        # return render_template('show_all_devices.html', devices=Device.query.all())


class DeviceResource(Resource):

    commands = ['identify', 'reset', 'label']
    schema = {
        "type": "object",
        "properties": {
            "identify": {
                "type": "object",
                "properties": {},
                "description": "identify request"
            },
            "reset": {
                "type": "object",
                "properties": {},
                "description": "reset request"
            },
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

    @check_device_exist
    def get(self, mac, device):
        return pack_response({'code':0, 'response':device})

    @check_device_state
    def put(self, mac, device):
        args = request.get_json()
        ip = device['ip']
        try:
            for key in args.keys():
                if key not in self.commands:
                    return pack_response({'code': 90002}, status=500, command=key)
            for key in args.keys():
                try:
                    validate(instance=args, schema=self.schema,
                             format_checker=draft7_format_checker)
                except SchemaError as e:
                    logger.exception('illegal schema: %s', e.message)
                    return pack_response({'code':90003}, status=500, error=e.message)
                except ValidationError as e:
                    logger.exception('json validation failed:%s', e.message)
                    return pack_response({'code':90004}, status=500, error=e.message)
                else:
                    response = dongle_command_2(ip, mac, args)
                    code = response['code']
                    if code != 0:
                        return pack_response(response, status=500)
                    else:
                        return pack_response(response)
        except Exception as e:
            return pack_response({'code':90000}, status=500, error=str(e))


class DeviceConfigResource(Resource):
    @check_device_state
    def get(self, mac, device):
        ip = device['ip']
        response = dongle_command_2(ip, mac, {
            "config": {
            }
        })
        code = response['code']
        if code != 0:
            return pack_response(response, status=500)
        else:
            return pack_response(response)

    @check_device_state
    def put(self, mac, device):
        args = request.get_json()
        ip = device['ip']
        if 'filename' in args:
            # check this file exist or not
            file = args['filename']
            path = os.path.join(base_dir, './files') + '/' + file
            if not os.path.isfile(path):
                return pack_response({'code':50000}, status=500, file=file)
            else:
                with open(path, 'r') as f:
                    data = yaml.safe_load(f.read())
                    response = dongle_command_2(ip, mac, {
                        "config": {
                            'data': data
                        }
                    })
        elif 'config' in args:
            # verify the config is meet JSON schema requirement
            try:
                validate(instance=args['config'], schema=config_schema,
                         format_checker=draft7_format_checker)
                response = dongle_command_2(ip, mac, {
                    "config": {
                        args['config']
                    }
                })
            except SchemaError as e:
                logger.exception('illegal schema: %s', e.message)
                return pack_response({'code':90003}, status=500, error=e.message)
            except ValidationError as e:
                logger.exception('json validation failed:%s', e.message)
                return pack_response({'code':90004}, status=500, error=e.message)
        else:
            return pack_response({'code':90001}, status=500)
        code = response['code']
        if code != 0:
            return pack_response(response, status=500)
        else:
            return pack_response(response)

    @check_device_state
    def post(self, mac, device):
        ip = device['ip']
        # verify the file is meet JSON schema requirement or not
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        content = args.get('file')
        try:
            y = yaml.safe_load(content.read())
            validate(instance=y, schema=config_schema,
                     format_checker=draft7_format_checker)

            response = dongle_command_2(ip, mac, {
                "config": {
                    y
                }
            })
            code = response['code']
            if code != 0:
                return pack_response(response, status=500)
            else:
                return pack_response(response), 200
        except SchemaError as e:
            logger.exception('illegal schema: %s', e.message)
            return pack_response({'code':90003}, status=500, error=e.message)
        except ValidationError as e:
            logger.exception('json validation failed:%s', e.message)
            return pack_response({'code':90004}, status=500, error=e.message)
        except Exception as e:
            logger.exception('load YAML failed:%s', e.message)
            return pack_response({'code':50001}, status=500, file=content.filename)
        pass

