from flask_restful import Api
from zigbeeLauncher.settings import NestableBlueprint
from .devices import devices, DeviceResource
from .files import files, FileResource
from .firmwares import firmwares, FirmwareResource

api = NestableBlueprint('api_1', __name__, url_prefix='/api/1')
api.register_blueprint(devices)
device_api = Api(api)
device_api.add_resource(DeviceResource, '/devices/<string:mac>')

files_api = Api(api)
files_api.add_resource(FileResource, '/files')

firmwares_api = Api(api)
firmwares_api.add_resource(FirmwareResource, '/firmwares')
from . import *
