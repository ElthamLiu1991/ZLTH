import base64
import os

import requests
import werkzeug.datastructures
from flask import request
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename

from ..response import Response
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from zigbeeLauncher.simulator import get_mac_address, get_ip_address
from zigbeeLauncher.logging import flaskLogger as logger
from ..util import handle_devices, send_command
from ... import base_dir
from ...exceptions import exception, InvalidPayload, NotFound, DeviceNotFound, DeviceOffline, Unreachable


class FirmwareResource(Resource):
    """
    /firmwares
    """
    def get(self):
        @exception
        def handle():
            data = []
            for root, dirs, files in os.walk('./firmwares'):
                data += files
                return data
        return handle()

    def delete(self):
        @exception
        def handle():
            try:
                file = f"./firmwares/{request.get_json()['filename']}"
            except Exception as e:
                raise InvalidPayload('missing filename')
            # path = os.path.join(base_dir, '/firmwares') + '/'+ filename
            if not os.path.isfile(file):
                raise NotFound(file)
            # os.remove(os.path.join(base_dir, f'./firmwares/{filename}'))
            os.remove(file)
            return {}
        return handle()

    def post(self):
        @exception
        def handle():
            for file in request.files.getlist('file'):
                filename = secure_filename(file.filename)
                file.save(f'./firmwares/{filename}')
            return {}
        return handle()

    def put(self):
        @exception
        def handle():
            try:
                filename = request.get_json()['filename']
                file = f'./firmwares/{filename}'
                devices = request.get_json()['devices']
                print("devices:", devices)
            except Exception as e:
                raise InvalidPayload('missing filename or devices')
            if not os.path.isfile(file):
                raise NotFound(file)
            simulators = {}
            for mac in devices:
                device = DBDevice(mac=mac).retrieve()
                if not device:
                    raise DeviceNotFound(mac)
                else:
                    device = device[0]
                if not device.get('connected'):
                    raise DeviceOffline(mac)
                ip = device.get('ip')
                if ip not in simulators:
                    simulators.update({ip: [mac]})
                else:
                    simulators[ip].append(mac)

                # simulator = DBSimulator(ip=ip).retrieve()
                # if not simulator:
                #     raise NotFound(f'simulator:{ip}')
                # simulator = device.get('ip')
                # if simulator not in simulators:
                #     simulators.update({simulator: [mac]})
                # else:
                #     simulators[simulator].append(mac)
            # if device belongs to another simulator, post file to that simulator first
            for ip, devices in simulators.items():
                print(f'ip:{ip}, devices:{devices}')
                if ip != get_ip_address():
                    simulator = DBSimulator(ip=ip).retrieve()
                    if not simulator:
                        print(f"cannot find {ip} in simulator database")
                        continue
                    url = f'http://{ip}:{simulator[0].get("port")}/api/2/firmwares'
                    files = {'file': open(file, 'rb')}
                    try:
                        r = requests.post(url, files=files)
                    except Exception as e:
                        raise Unreachable(ip)
                    logger.info(r.json())
                result = send_command(ip=ip, command={
                    'firmware': {
                        'filename': filename,
                        'devices': devices
                    }
                })
                if result.code != 0:
                    return result
            return {}
        return handle()
    # def put(self):
    #     """
    #     对指定设备应用指定固件
    #     :return:
    #     """
    #     args = request.get_json()
    #     if 'devices' not in args and 'filename' not in args:
    #         return Response(code=90001).pack()
    #     else:
    #         file = args['filename']
    #         path = os.path.join(base_dir, './firmwares') + '/' + file
    #         if not os.path.isfile(path):
    #             return Response(file, code=50000).pack()
    #         else:
    #             # send this file to another simulator
    #             result, code = handle_devices(args['devices'])
    #             if code != 200:
    #                 return result, 500
    #             else:
    #                 # TODO: if involve other simulator, send this file to other simulator via HTTP
    #                 with open(path, 'rb') as f:
    #                     data = base64.b64encode(f.read()).decode()
    #                     for ip in result.keys():
    #                         if ip == get_ip_address():
    #                             response = simulator_command_2(ip, {
    #                                 "firmware": {
    #                                     "filename": file,
    #                                     "devices": result[ip]
    #                                 }
    #                             })
    #                         else:
    #                             response = simulator_command_2(ip, {
    #                                 "firmware": {
    #                                     "filename": file,
    #                                     "data": data,
    #                                     "devices": result[ip]
    #                                 }
    #                             })
    #                         code = response['code']
    #                         if code != 0:
    #                             return Response(**response).pack()
    #
    #                 return Response(**response).pack()
