import os

import rapidjson
import werkzeug
import yaml
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from . import devices
from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.mqtt.Launcher_API import dongle_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import Response
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError
from ..json_schemas import config_schema

from ..util import check_device_exist, check_device_state, config_validation
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
                return Response(data=DBDevice(**paras).retrieve()).pack()
            except Exception as e:
                logger.exception("request error")
                return Response("bad parameters:"+str(request.args), code=90000)
        return Response(data=DBDevice().retrieve()).pack()


class DeviceResource(Resource):

    commands = ['identify', 'reset', 'label', 'online']
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
        return Response(data=device).pack()

    @check_device_state
    def put(self, mac, device):
        args = request.get_json()
        ip = device['ip']
        state = device['state']
        try:
            for key in args.keys():
                if key not in self.commands:
                    return Response(key, code=90002).pack()
            for key in args.keys():
                if key != 'reset':
                    if state == 2:
                        return Response(mac, code=10002).pack()
                    if key == 'label':
                        # label size should not more than 64 characters
                        if len(args[key]['data']) > 63:
                            return Response('data', code=90005).pack()
                if state == 3:
                    return Response(mac, code=10003).pack()
                if state == 9:
                    return Response(mac, code=10009).pack()
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
                    response = dongle_command_2(ip, mac, args)
                    return Response(**response).pack()
        except Exception as e:
            return Response(str(e), code=90000).pack()


class DeviceConfigResource(Resource):
    @check_device_state
    def get(self, mac, device):
        if not device['configured']:
            return Response(mac, code=60000).pack()
        if device['state'] == 9:
            return Response(mac, code=60001).pack()
        ip = device['ip']
        response = dongle_command_2(ip, mac, {
            "config": {
            }
        })
        return Response(**response).pack()

    @check_device_state
    def put(self, mac, device):
        if device['state'] == 9:
            return Response(mac, code=60001).pack()
        args = request.get_json()
        ip = device['ip']
        if 'filename' in args:
            # check this file exist or not
            file = args['filename']
            path = os.path.join(base_dir, './files') + '/' + file
            if not os.path.isfile(path):
                return Response(file, code=50000).pack()
            else:
                with open(path, 'r') as f:
                    data = yaml.safe_load(f.read())
                    response = dongle_command_2(ip, mac, {
                        "config": data
                    })
        elif 'config' in args:
            # verify the config is meet JSON schema requirement
            try:
                validate(instance=args, schema=config_schema,
                         format_checker=draft7_format_checker)
                result, error = config_validation(args['config'])
                if not result:
                    return Response(error, code=90005).pack()
                response = dongle_command_2(ip, mac, args)
            except SchemaError as e:
                logger.exception('illegal schema: %s', e.message)
                return Response(e.message, code=90003).pack()
            except ValidationError as e:
                logger.exception('json validation failed:%s', e.message)
                return Response(e.message, code=90004).pack()
        else:
            return Response('filename or config', code=90001).pack()
        return Response(**response).pack()

    @check_device_state
    def post(self, mac, device):
        if device['state'] == 9:
            return Response(mac, code=60001).pack()
        ip = device['ip']
        # verify the file is meet JSON schema requirement or not
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        content = args.get('file')
        if not content:
            return Response(None, code=50001).pack()
        try:
            y = yaml.safe_load(content.read())
            validate(instance={'config': y}, schema=config_schema,
                     format_checker=draft7_format_checker)
            result, error = config_validation(y)
            if not result:
                return Response(error, code=90005).pack()
            # single device configuration may take more than 10 seconds depends on number of endpoints,
            # so set timeout to at least 30 seconds
            response = dongle_command_2(ip, mac, {
                "config": y
            }, timeout=30)
            return Response(**response).pack()
        except SchemaError as e:
            logger.exception('illegal schema: %s', e.message)
            return Response(e.message, code=90003).pack()
        except ValidationError as e:
            logger.exception('json validation failed:%s', e.message)
            return Response(e.message, code=90004).pack()
        except Exception as e:
            logger.exception('load YAML failed:%s', str(e))
            return Response(str(e), code=90000).pack()
        pass

