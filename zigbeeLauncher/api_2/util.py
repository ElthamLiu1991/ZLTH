import json
import time
import uuid
from functools import wraps

import requests

from zigbeeLauncher.data_model import Message
from zigbeeLauncher.exceptions import Timeout
from zigbeeLauncher.logging import flaskLogger as logger
from zigbeeLauncher.api_2.response import Response
from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee
from zigbeeLauncher.wait_response import wait_response
from zigbeeLauncher.simulator import get_mac_address
from zigbeeLauncher.simulator.handler import handle_device_command, handler_command
from zigbeeLauncher.util import get_ip_address, Global
from zigbeeLauncher.zigbee import type_exist, format_validation, value_validation


def send_command(ip=None, mac=None, command=None, timeout=10):
    timestamp = int(round(time.time() * 1000))
    uid = str(uuid.uuid1())
    # 加入request等待队列
    task = wait_response(timestamp, uid, timeout)
    message = Message(uuid=uid, timestamp=timestamp, data=command, code=0, message="")
    # if ip == get_ip_address():
    if False:
        logger.info(f'local command:{command}')
        if mac:
            # device command
            handle_device_command(message, ip, mac)
            pass
        else:
            # simulator command
            handler_command(message, ip)
    else:
        logger.info(f'remote command:{command}')
        simulator = Global.get(Global.SIMULATOR)
        if mac:
            simulator.client.send_device_command(ip, mac, message)
        else:
            # simulator command
            simulator.client.send_simulator_command(ip, message)
    timeout, data = task.result()
    if timeout:
        raise Timeout()
    return data


def handle_devices(devices):
    devices_dict = {}
    for mac in devices:
        device = DBDevice(mac=mac).retrieve()
        if not device:
            return Response(mac, code=10000).pack()
        else:
            device = device[0]
            if not device["connected"]:
                return Response(mac, code=10001).pack()
            elif device['state'] == 3:
                return Response(mac, code=10003).pack()
            else:
                ip = device['ip']
                if ip not in devices_dict:
                    devices_dict[ip] = []
                devices_dict[ip].append(mac)
    for ip in devices_dict:
        simulator = DBSimulator(ip=ip).retrieve()
        if not simulator:
            return Response(ip, code=20000).pack()
        else:
            simulator = simulator[0]
            if not simulator['connected']:
                return Response(mac, code=20001).pack()
    return devices_dict, 200


def check_zigbee_exist(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        mac = kwargs['mac']
        zigbee = DBZigbee(mac=mac).retrieve()
        if not zigbee:
            return Response(mac, code=10000).pack()
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
            return Response(mac, code=10000).pack()
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
            return Response(mac, code=10000).pack()
        else:
            device = device[0]
            connected = device['connected']
            if not connected:
                return Response(mac, code=10001).pack()
            else:
                # state = device['state']
                # if state == 2:
                #     return Response(mac, code=10002).pack()
                # elif state == 3:
                #     return Response(mac, code=10003).pack()
                # elif state == 9:
                #     return Response(mac, code=10009).pack()
                # else:
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

