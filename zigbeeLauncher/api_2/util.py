import json
from functools import wraps

import requests
from zigbeeLauncher.logging import flaskLogger as logger
from zigbeeLauncher.api_2.response import pack_response
from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee
from zigbeeLauncher.mqtt import get_mac_address
from zigbeeLauncher.zigbee import type_exist, format_validation, value_validation


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
                if state == 2:
                    return pack_response({'code': 10002}, status=500, device=mac)
                elif state == 3:
                    return pack_response({'code': 10003}, status=500, device=mac)
                elif state == 9:
                    return pack_response({'code': 10009}, status=500, device=mac)
                else:
                    kwargs['device'] = device
                    return function(*args, **kwargs)

    return wrapper


def config_validation(config):
    def command_validation(command):
        if not 0 <= command['id'] <= 0xFF:
            return False, 'command:{}:id'.format(command['id'])
        if 'manufacturer_code' in command and not 0 <= command['manufacturer_code'] <= 0xFFFF:
            return False, 'command:{}:manufacturer_code'.format(command['id'])
        return True, None

    def attribute_validation(attribute):
        if not 0 <= attribute['id'] <= 0xFFFF:
            return False, 'attribute:{}:id'.format(attribute['id'])
        if 'manufacturer_code' in attribute and not 0 <= attribute['manufacturer_code'] <= 0xFFFF:
            return False, 'attribute:{}:manufacturer_code'.format(attribute['id'])
        if not type_exist(attribute['type']):
            return False, 'attribute:{}:type:not exist'.format(attribute['id'])
        if not format_validation(attribute['type'], attribute['default']):
            return False, 'attribute:{}:format error'.format(attribute['id'])
        if not value_validation(attribute['type'], attribute['default']):
            return False, 'attribute:{}:default'.format(attribute['id'])
        return True, None

    def cluster_validation(cluster):
        if not 0 <= cluster['id'] <= 0xFFFF:
            return False, 'clusters:{}:id'.format(cluster['id'])
        if 'manufacturer_code' in cluster and not 0 <= cluster['manufacturer_code'] <= 0xFFFF:
            return False, 'clusters:{}:manufacturer_code'.format(cluster['id'])
        for attribute in cluster['attributes']:
            result, error = attribute_validation(attribute)
            if not result:
                return result, 'clusters:{}:'.format(cluster['id'])+error
        for command in cluster['commands']['C->S']:
            result, error = command_validation(command)
            if not result:
                return result, 'clusters:{}:'.format(cluster['id']) + error
        for command in cluster['commands']['S->C']:
            result, error = command_validation(command)
            if not result:
                return result, 'clusters:{}:'.format(cluster['id']) + error
        return True, None

    # 验证node
    node = config['node']
    if node['device_type'] not in [
        'coordinator',
        'router',
        'end_device',
        'sleepy_end_device',
        'unknown'
    ]:
        return False, 'node: device_type'
    if not 0 <= node['manufacturer_code'] <= 0xFFFF:
        return False, 'node: manufacturer_code'
    if not 0 <= node['radio_power'] <= 0xFF:
        return False, 'node: radio_power'
    # 验证endpoints
    endpoints = config['endpoints']
    for endpoint in endpoints:
        if not 0 <= endpoint['id'] <= 0xFF:
            return False, 'endpoints:{}:id'.format(endpoint['id'])
        if not 0 <= endpoint['profile_id'] <= 0xFFFF:
            return False, 'endpoints:{}:profile_id'.format(endpoint['id'])
        if not 0 <= endpoint['device_id'] <= 0xFFFF:
            return False, 'endpoints:{}:device_id'.format(endpoint['id'])
        if not 0 <= endpoint['device_version'] <= 0xFF:
            return False, 'endpoints:{}:device_version'.format(endpoint['id'])
        for cluster in endpoint['server_clusters']:
            result, error = cluster_validation(cluster)
            if not result:
                return False, 'endpoints:{}:server_'.format(endpoint['id'])+error
        for cluster in endpoint['client_clusters']:
            result, error = cluster_validation(cluster)
            if not result:
                return False, 'endpoints:{}:client_'.format(endpoint['id'])+error
    return True, None