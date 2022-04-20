from flask_restful import Api
from zigbeeLauncher.settings import NestableBlueprint
from .devices import DeviceResource, DevicesResource
from .simulators import SimulatorResource, SimulatorsResource
from .files import files, FileResource
from .firmwares import firmwares, FirmwareResource

api = NestableBlueprint('api_1', __name__, url_prefix='/api/1')
device_api = Api(api)
device_api.add_resource(DevicesResource, '/devices/')
device_api.add_resource(DeviceResource, '/devices/<string:mac>')

simulator_api = Api(api)
simulator_api.add_resource(SimulatorsResource, '/simulators/')
simulator_api.add_resource(SimulatorResource, '/simulators/<string:mac>')

files_api = Api(api)
files_api.add_resource(FileResource, '/files')

firmwares_api = Api(api)
firmwares_api.add_resource(FirmwareResource, '/firmwares')
from . import *
