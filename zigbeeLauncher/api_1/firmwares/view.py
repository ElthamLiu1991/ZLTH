import base64
import os

import requests
import werkzeug.datastructures
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from ..response import pack_response
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from zigbeeLauncher.mqtt import get_mac_address
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import simulator_command
from zigbeeLauncher.logging import flaskLogger as logger


class FirmwareResource(Resource):

    def get(self):
        """
        获取保存的固件列表
        :return:
        """
        data = []
        for root, dirs, files in os.walk('./firmwares'):
            data = data + files
            return pack_response(0, data)

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
            content.save(os.path.join('./firmwares', filename))
            return pack_response(0)
        except Exception as e:
            logger.exception("request error")
            return pack_response(90000, error=str(e)), 500

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
            if device:
                device = device[0]
                if not device["connected"]:
                    return pack_response(10001, device=mac), 500
                if device["ip"] not in simulators:
                    if get_mac_address() != device['ip']:
                        try:
                            files = {
                                'file': open('./firmwares/' + args.get('filename'), 'rb')
                            }
                            # 调用POST /firmwares将文件发送给同一个局域网的simulator
                            simulator = DBSimulator(ip=device['ip']).retrieve()
                            if simulator:
                                simulator = simulator[0]
                                if not simulator['connected']:
                                    return pack_response(20001, device=simulator['ip']), 500
                                try:
                                    r = requests.post('http://' + simulator['ip'] + ':5000/api/1/firmwares',
                                                      files=files, timeout=5)
                                    if r.status_code != 200:
                                        return pack_response(20002, device=simulator['ip'], error=""), 500
                                except Exception as e:
                                    logger.exception("request error")
                                    return pack_response(20003, device=simulator['ip']), 500
                            else:
                                return pack_response(20000, device=device['ip']), 500
                        except Exception as e:
                            logger.exception("request error")
                            return pack_response(90000, error=str(e)), 500
                    simulators[device['ip']] = [mac]
                else:
                    simulators[device['ip']].append(mac)
            else:
                return pack_response(10000, device=mac), 500
        print("simulator:", simulators)

        for mac in simulators.keys():
            simulator_command(mac, {
                "command": "firmware", "payload": {
                    "filename": args.get('filename'),
                    "devices": simulators[mac]
                }
            })
        return pack_response(0)