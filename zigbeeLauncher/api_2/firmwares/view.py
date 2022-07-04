import base64
import os

import requests
import werkzeug.datastructures
from flask import request
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from ..response import Response
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
            return Response(data=data).pack()

    def delete(self):
        args = request.get_json()
        if 'filename' not in args:
            return Response('filename', code=90001).pack()
        file =args['filename']
        path = os.path.join(base_dir, './firmwares') + '/' + file
        if not os.path.isfile(path):
            return Response(file, code=50000).pack()
        else:
            os.remove(os.path.join(path))
            return Response().pack()

    def post(self):
        """
        保存新的固件, 可以接收多个文件
        :param mac:
        :return:
        """
        files = request.files.getlist('file')
        try:
            for file in files:
                filename = secure_filename(file.filename)
                file.save(os.path.join('./firmwares', filename))
        except Exception as e:
            logger.exception("request error")
            return Response(str(e), code=90000).pack()
        return Response().pack()

    def put(self):
        """
        对指定设备应用指定固件
        :return:
        """
        args = request.get_json()
        if 'devices' not in args and 'filename' not in args:
            return Response(code=90001).pack()
        else:
            file = args['filename']
            path = os.path.join(base_dir, './firmwares') + '/' + file
            if not os.path.isfile(path):
                return Response(file, code=50000).pack()
            else:
                # send this file to another simulator
                result, code = handle_devices(args['devices'])
                if code != 200:
                    return result, 500
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
                                return Response(**response).pack()

                    return Response(**response).pack()
