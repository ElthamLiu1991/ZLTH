import json
from functools import wraps

import requests
from zigbeeLauncher.logging import flaskLogger as logger
from zigbeeLauncher.api_2.response import pack_response
from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee
from zigbeeLauncher.mqtt import get_mac_address


def handle_devices(devices):
    devices_dict = {}
    for mac in devices:
        device = DBDevice(mac=mac).retrieve()
        if not device:
            return pack_response({
                "code": 10000
            }, status=500, device=mac)
        else:
            device = device[0]
            if not device["connected"]:
                return pack_response({
                    "code": 10001
                }, status=500, device=mac)
            else:
                ip = device['ip']
                if ip not in devices_dict:
                    devices_dict[ip] = []
                devices_dict[ip].append(mac)
    for ip in devices_dict:
        simulator = DBSimulator(ip=ip).retrieve()
        if not simulator:
            return pack_response({
                "code": 20000
            }, status=500, device=ip)
        else:
            simulator = simulator[0]
            if not simulator['connected']:
                return pack_response({
                    "code": 20001
                }, status=500, device=ip)
    return devices_dict, 200


def check_zigbee_exist(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        mac = kwargs['mac']
        zigbee = DBZigbee(mac=mac).retrieve()
        if not zigbee:
            return pack_response({'code':10000}, status=404, device=mac)
        else:
            kwargs['zigbee'] = zigbee[0]
            return function(*args, **kwargs)

    return wrapper


def check_device_exist(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        mac = kwargs['mac']
        device = DBDevice(mac=mac).retrieve()
        if not device:
            return pack_response({'code':10000}, status=404, device=mac)
        else:
            kwargs['device'] = device[0]
            return function(*args, **kwargs)

    return wrapper


def check_device_state(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        mac = kwargs['mac']
        device = DBDevice(mac=mac).retrieve()
        if not device:
            return pack_response({'code': 10000}, status=404, device=mac)
        else:
            device = device[0]
            connected = device['connected']
            if not connected:
                return pack_response({'code': 10001}, status=500, device=mac)
            else:
                state = device['state']
                if state == 2 or state == 3:
                    return pack_response({'code':10002}, status=500, device=mac)
                else:
                    kwargs['device'] = device
                    return function(*args, **kwargs)

    return wrapper
