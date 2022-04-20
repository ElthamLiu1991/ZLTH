import base64
import os

import werkzeug.datastructures
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import simulator_command_2


class FileResource(Resource):

    def get(self):
        """
        获取保存的固件列表
        :return:
        """
        data = []
        for root, dirs, files in os.walk('./files'):
            data = data + files
            return data, 200

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
            filename = secure_filename(content.filename)
            content.save(os.path.join('./files', filename))
            return {"success": {}}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def put(self):
        """
        对指定设备应用指定固件
        :return:
        """
        # 按照设备筛选simulator ip和设备名称
        parser = reqparse.RequestParser()
        parser.add_argument("filename", type=str, required=True, help="please provide command")
        parser.add_argument("devices", type=str, action='append', required=True, help="please provide device list")
        args = parser.parse_args()
        simulators = {}
        devices = args.get("devices")
        for mac in devices:
            device = DBDevice(mac=mac).retrieve()
            if device and device[0]["ip"] not in simulators:
                simulators[device[0]['ip']] = [mac]
            else:
                simulators[device[0]['ip']].append(mac)
        print("simulator files:", simulators)
        # encode file to base64
        with open('./files/'+args.get('filename'), 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            for simulator in simulators.keys():
                simulator_command_2(simulator, {
                    "files": {
                        "filename": args.get('filename'),
                        "devices": simulators[simulator],
                        "data": data
                    }
                })
        return {"success": {}}, 200
