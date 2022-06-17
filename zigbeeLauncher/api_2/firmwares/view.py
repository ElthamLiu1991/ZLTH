import base64
import os

import requests
import werkzeug.datastructures
from flask import request
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from ..response import pack_response
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from zigbeeLauncher.mqtt import get_mac_address, get_ip_address
from zigbeeLauncher.mqtt.Launcher_API import simulator_command_2
from zigbeeLauncher.logging import flaskLogger as logger
from ..util import handle_devices
from ... import base_dir


class FirmwareResource(Resource):

    def get(self):
        """
        获取保存的固件列表
        :return:
        """
        data = []
        for root, dirs, files in os.walk('./firmwares'):
            data = data + files
            return pack_response({'code': 0, 'response': data})

    def post(self):
        """
        保存新的固件
        :param mac:
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        content = args.get('file')
        try:
            if not content:
                return pack_response({'code': 90000}, status=500, error='file not found')
            filename = secure_filename(content.filename)
            content.save(os.path.join('./firmwares', filename))
            return pack_response({'code': 0})
        except Exception as e:
            logger.exception("request error")
            return pack_response({'code': 90000}, status=500, error=str(e))

    def put(self):
        """
        对指定设备应用指定固件
        :return:
        """
        args = request.get_json()
        if 'devices' not in args and 'filename' not in args:
            return pack_response({'code': 90001}, status=500)
        else:
            file = args['filename']
            path = os.path.join(base_dir, './firmwares') + '/' + file
            if not os.path.isfile(path):
                return pack_response({'code': 50000}, status=500, file=file)
            else:
                # send this file to another simulator
                result, code = handle_devices(args['devices'])
                if code != 200:
                    return result, code
                else:
                    with open(path, 'rb') as f:
                        data = base64.b64encode(f.read()).decode()
                        for ip in result.keys():
                            if ip == get_ip_address():
                                response = simulator_command_2(ip, {
                                    "firmware": {
                                        "filename": file,
                                        "devices": result[ip]
                                    }
                                })
                            else:
                                response = simulator_command_2(ip, {
                                    "firmware": {
                                        "filename": file,
                                        "data": data,
                                        "devices": result[ip]
                                    }
                                })
                            code = response['code']
                            if code != 0:
                                return pack_response(response, status=500)

                    return pack_response(response)
