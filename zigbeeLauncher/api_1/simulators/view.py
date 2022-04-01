import rapidjson
from flask import jsonify, render_template, request
from flask_restful import Api, Resource, reqparse
from zigbeeLauncher.api_1.simulators import simulators
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from zigbeeLauncher.mqtt.WiserZigbeeLauncher import simulator_command
from zigbeeLauncher.logging import flaskLogger as logger
from zigbeeLauncher.api_1.response import pack_response


@simulators.route("/", methods=['GET'])
def show_simulators():
    """
    获取数据库device表并传给前端
    :return: device所有数据
    """
    if request.args:
        try:
            paras = {}
            for key in request.args:
                paras[key] = request.args[key]
            items = DBSimulator(**paras).retrieve()
        except Exception as e:
            logger.exception("request error")
            return pack_response(90000, error="bad parameters:"+str(request.args)), 500
    else:
        items = DBSimulator().retrieve()
    for simulator in items:
        simulator['devices'] = []
        # 获取devices
        devices = DBDevice(ip=simulator['ip']).retrieve()
        for device in devices:
            simulator['devices'].append(device['mac'])
    return jsonify(pack_response(0, items))
    # return render_template('show_all_devices.html', devices=Device.query.all())


class SimulatorResource(Resource):

    def get(self, mac):
        if DBSimulator(mac=mac).retrieve():
            simulator = DBSimulator(mac=mac).retrieve()[0]
            simulator['devices'] = []
            # 获取devices
            devices = DBDevice(ip=simulator['ip']).retrieve()
            for device in devices:
                simulator['devices'].append(device['mac'])
            return pack_response(0, simulator), 200
        else:
            return pack_response(20000, device=mac), 404

    def put(self, mac):
        parser = reqparse.RequestParser()
        parser.add_argument("command", type=str, required=True, help="please provide command")
        parser.add_argument("payload", type=dict, required=False)
        args = parser.parse_args()
        simulator = DBSimulator(mac=mac).retrieve()
        if simulator:
            try:
                if simulator[0]['connected']:
                    simulator_command(mac, args)
                    return pack_response(0), 200
                else:
                    return pack_response(20001, device=mac), 500
            except Exception as e:
                return pack_response(90000, error=str(e)), 500
        else:
            return pack_response(20000, device=mac), 404
