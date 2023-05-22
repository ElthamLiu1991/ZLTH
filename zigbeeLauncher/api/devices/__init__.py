from zigbeeLauncher.api.devices.view import Devices


def register(api):
    api.add_resource(Devices, '/devices')