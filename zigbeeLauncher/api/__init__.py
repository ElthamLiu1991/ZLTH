from flask_restful import Api

from zigbeeLauncher.api import devices
from zigbeeLauncher.settings import NestableBlueprint

api_blueprint = NestableBlueprint("api", __name__, url_prefix='/api/2')
api = Api(api_blueprint)

devices.register(api)
