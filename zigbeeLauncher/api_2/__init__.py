from flask_restful import Api
from zigbeeLauncher.settings import NestableBlueprint
from .autos.view import AutoResource, AutoScriptsResource, \
    AutoScriptsConfigResource, AutoOperationResource, AutoOperationRecordsResource
from .configs.view import ConfigFilesResource, ConfigFileResource, ConfigDevicesResource, ConfigResource
from .devices import DeviceResource, DevicesResource, DeviceConfigResource
from .logs import LogsResource
from .simulators import SimulatorResource, SimulatorsResource
from .firmwares import firmwares, FirmwareResource
from .zigbees import ZigbeesResource, ZigbeeResource, ZigbeeAttributesResource

api = NestableBlueprint('api_2', __name__, url_prefix='/api/2')
device_api = Api(api)
device_api.add_resource(DevicesResource, '/devices')
device_api.add_resource(DeviceResource, '/devices/<string:mac>')
device_api.add_resource(DeviceConfigResource, '/devices/<string:mac>/config')

zigbee_api = Api(api)
zigbee_api.add_resource(ZigbeesResource, '/zigbees')
zigbee_api.add_resource(ZigbeeResource, '/zigbees/<string:mac>')
zigbee_api.add_resource(ZigbeeAttributesResource, '/zigbees/<string:mac>/attributes')

simulator_api = Api(api)
simulator_api.add_resource(SimulatorsResource, '/simulators')
simulator_api.add_resource(SimulatorResource, '/simulators/<string:mac>')

firmwares_api = Api(api)
firmwares_api.add_resource(FirmwareResource, '/firmwares')

configs_api = Api(api)
configs_api.add_resource(ConfigResource, '/configs')
configs_api.add_resource(ConfigFilesResource, '/configs/files')
configs_api.add_resource(ConfigFileResource, '/configs/files/<string:file>')
configs_api.add_resource(ConfigDevicesResource, '/configs/devices')

auto_api = Api(api)
auto_api.add_resource(AutoResource, '/auto')
auto_api.add_resource(AutoOperationResource, '/auto/<string:operation>')
auto_api.add_resource(AutoOperationRecordsResource, '/auto/records/<string:record>')
auto_api.add_resource(AutoScriptsResource, '/auto/scripts/<string:script>')
auto_api.add_resource(AutoScriptsConfigResource, '/auto/scripts/<string:script>/config')

logs_api = Api(api)
logs_api.add_resource(LogsResource, '/logs')

from . import *
