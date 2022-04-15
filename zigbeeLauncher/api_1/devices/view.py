import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from . import devices
from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import dongle_command
from zigbeeLauncher.logging import flaskLogger as logger
from ..response import pack_response


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


class DeviceResource(Resource):

    def get(self, mac):
        if DBDevice(mac=mac).retrieve():
            return pack_response(0, DBDevice(mac=mac).retrieve()[0]), 200
        else:
            return pack_response(10000, device=mac), 404

    def put(self, mac):
        parser = reqparse.RequestParser()
        parser.add_argument("command", type=str, required=True, help="please provide command")
        parser.add_argument("payload", type=dict, required=False)
        args = parser.parse_args()
        device = DBDevice(mac=mac).retrieve()
        if device:
            try:
                if device[0]['connected']:
                    dongle_command(device[0]["ip"], mac, args)
                    return pack_response(0), 200
                else:
                    return pack_response(10001, device=mac), 500
            except Exception as e:
                return pack_response(90000, error=str(e)), 500
        else:
            return pack_response(10000, device=mac), 404
