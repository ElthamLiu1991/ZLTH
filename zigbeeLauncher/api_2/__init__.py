from flask_restful import Api
from zigbeeLauncher.settings import NestableBlueprint
from .devices import DeviceResource, DevicesResource
from .simulators import SimulatorResource, SimulatorsResource
from .files import files, FileResource
from .firmwares import firmwares, FirmwareResource
from .zigbees import ZigbeesResource, ZigbeeResource

api = NestableBlueprint('api_2', __name__, url_prefix='/api/2')
device_api = Api(api)
device_api.add_resource(DevicesResource, '/devices/')
device_api.add_resource(DeviceResource, '/devices/<string:mac>')

zigbee_api = Api(api)
zigbee_api.add_resource(ZigbeesResource, '/zigbees/')
zigbee_api.add_resource(ZigbeeResource, '/zigbees/<string:mac>')

simulator_api = Api(api)
simulator_api.add_resource(SimulatorsResource, '/simulators/')
simulator_api.add_resource(SimulatorResource, '/simulators/<string:mac>')

files_api = Api(api)
files_api.add_resource(FileResource, '/files')

firmwares_api = Api(api)
firmwares_api.add_resource(FirmwareResource, '/firmwares')
from . import *
