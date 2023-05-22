from flasgger import swag_from
from flask import request
from flask_restful import Resource

from zigbeeLauncher.database.interface import DBDevice
from zigbeeLauncher.exceptions import exception


class Devices(Resource):
    @swag_from('../docs/devices/devices_specs.yml')
    def get(self):
        @exception
        def handle():
            paras = request.args
            devices = DBDevice(**paras).retrieve()
            return devices

        return handle()