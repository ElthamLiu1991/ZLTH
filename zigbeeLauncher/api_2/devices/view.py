import os

import rapidjson
import werkzeug
import yaml
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from jsonschema import validate
from jsonschema._format import draft7_format_checker

from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.logging import flaskLogger as logger
from ..json_schemas import config_schema

from ..util import check_device_exist, check_device_state, config_validation, send_command
from ... import base_dir
from ...exceptions import exception, DeviceOffline, InvalidPayload, Unsupported, DeviceNotFound, DeviceNotReady


class DevicesResource(Resource):
    """
    /devices
    """

    def get(self):
        @exception
        def handle():
            paras = request.args
            devices = DBDevice(**paras).retrieve()
            return devices

        return handle()


class DeviceResource(Resource):
    """
    /devices/<mac>
    """

    def get(self, mac):
        @exception
        def handle():
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                return device[0]

        return handle()

    def put(self, mac):
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

        @exception
        def handle():
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                device = device[0]

            if not device.get('connected'):
                raise DeviceOffline(mac)
            try:
                validate(instance=request.get_json(), schema=schema,
                         format_checker=draft7_format_checker)
            except Exception as e:
                raise InvalidPayload(e.description)
            for k, v in request.get_json().items():
                if k not in commands:
                    raise Unsupported(k)
                return send_command(ip=device.get('ip'), mac=mac, command={k: v})

        return handle()


class DeviceConfigResource(Resource):
    """
    /devices/<mac>/config
    """

    def get(self, mac):
        @exception
        def handle():
            device = DBDevice(mac=mac).retrieve()
            if not device:
                raise DeviceNotFound(mac)
            else:
                device = device[0]
                if not device.get('connected'):
                    raise DeviceOffline(mac)
                if not device.get('configured'):
                    raise DeviceNotReady(mac)
                return send_command(ip=device.get('ip'), mac=mac, command={'config': {}})

        return handle()

    # @check_device_state
    # def get(self, mac, device):
    #     if not device['configured']:
    #         return Response(mac, code=60000).pack()
    #     if device['state'] == 9:
    #         return Response(mac, code=60001).pack()
    #     ip = device['ip']
    #     response = dongle_command_2(ip, mac, {
    #         "config": {
    #         }
    #     })
    #     return Response(**response).pack()

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
