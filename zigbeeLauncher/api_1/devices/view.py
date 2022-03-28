from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from zigbeeLauncher.api_1.devices import devices
from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import dongle_command
from zigbeeLauncher.logging import flaskLogger as logger


@devices.route("/", methods=['GET'])
def show_devices():
    """
    获取数据库device表并传给前端
    :return: device所有数据
    """
    if request.args:
        paras = {}
        for key in request.args:
            paras[key] = request.args[key]
        return jsonify(DBDevice(**paras).retrieve())
    return jsonify(DBDevice().retrieve())
    # return render_template('show_all_devices.html', devices=Device.query.all())


class DeviceResource(Resource):

    def get(self, mac):
        return jsonify(DBDevice(mac=mac).retrieve())

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
                    return {"success": {}}, 200
                else:
                    return {"error":"Device is offline"}, 400
            except Exception as e:
                return {"error": str(e)}, 500
        else:
            return {}, 404

        return [], 400
