import base64
import json
import os
import time
import uuid

import rapidjson

from . import router, mqtt_version, client_ip, client_mac, user_label
from .WiserZigbeeDongleHandler import dongle_command_handle
from .WiserZigbeeGlobal import pack_payload, get_value, except_handle, get_ip_address
from .WiserZigbeeDongle import upload_port_info, pack_port_info
from zigbeeLauncher.logging import simulatorLogger as logger
from .WiserZigbeeLauncher import insert_device, simulator_device_info, simulator_device_update
from ..database.interface import DBDevice, DBSimulator, DBZigbee, DBZigbeeEndpointCluster, DBZigbeeEndpoint, \
    DBZigbeeEndpointClusterAttribute


def simulator_error_callback(msg):
    data = pack_payload(msg)
    topic = mqtt_version + "/simulator/error"
    logger.info("Publish: topic:%s", topic)
    brokers = get_value('brokers')
    if brokers and '127.0.0.1' in brokers:
        brokers['127.0.0.1'].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")

def dongle_info_callback(name, msg):
    msg["ip"] = client_ip
    data = pack_payload(msg)
    topic = mqtt_version + "/simulator/devices/" + name + "/info"
    logger.info("Publish: topic:%s", topic)
    brokers = get_value('brokers')
    if brokers and '127.0.0.1' in brokers:
        brokers['127.0.0.1'].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        simulator_device_info(None, None, data, None)


def dongle_update_callback(name, msg):
    data = pack_payload(msg)
    topic = mqtt_version + "/simulator/devices/" + name + "/update"
    logger.info("Publish: topic:%s", topic)
    brokers = get_value('brokers')
    if brokers and '127.0.0.1' in brokers:
        brokers['127.0.0.1'].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")
        # insert to database
        simulator_device_update(None, None, data, name)


def dongle_error_callback(name, msg):
    data = pack_payload(msg)
    topic = mqtt_version + "/simulator/devices/" + name + "/error"
    logger.info("Publish: topic:%s", topic)
    brokers = get_value('brokers')
    if brokers and '127.0.0.1' in brokers:
        brokers['127.0.0.1'].publish(topic, data, qos=2)
    else:
        logger.error("MQTT client is not ready")


@router.route('/synchronized')
def synchronized(client, ip, payload):
    """
    发送simulator/info以及simulator/devices/*/info进行同步
    :return:
    """
    try:
        data = pack_payload(pack_simulator_info())
        topic = mqtt_version + "/" + ip + "/simulator/info"
        logger.info("public:%s", topic)
        client.publish(topic, data, qos=2)
        """
        logger.info("Packing all dongles info from database")
        # upload_port_info()
        dongles = DBDevice().retrieve()
        for dongle in dongles:
            if dongle["ip"] == client_ip:
                dongle_info_callback(dongle["mac"], dongle)
        """
    except Exception as e:
        logger.exception("Error:%s", e)
    finally:
        pass


@router.route('/simulator')
def simulator(client, ip, payload):
    """
    获取Simulator以及Dongle设备详细信息，每个Dongle的信息单独发送
    :param client:
    :param payload:
    :return:
    """
    try:
        """
        data = pack_payload(pack_simulator_info())
        topic = mqtt_version + "/" + client_ip + "/simulator/info"
        client.publish(topic, data)
        logger.info("Packing all dongles info...")
        upload_port_info()
        """
        logger.info("Packing all dongles info from port list")
        upload_port_info()
        """
        dongles = DBDevice(ip=ip).retrieve()
        for dongle in dongles:
            if dongle["ip"] == client_ip:
                dongle_info_callback(dongle["mac"], dongle)
        """

    except Exception as e:
        logger.exception("Error:%s", e)
    finally:
        pass


@router.route('/simulator/devices/+')
def simulator_device(client, ip, payload, device):
    """
    获取dongle设备详细信息
    :param client:
    :param payload:
    :param device:
    :return:
    """
    try:
        logger.info("Packing dongle '%s' info...", device)
        upload_port_info(device)
    except Exception as e:
        logger.exception("Error:%s", e)
    finally:
        pass


@router.route('/simulator/command')
@except_handle(simulator_error_callback)
def simulator_command(client, ip, payload):
    data = json.loads(payload)
    rsp = {
        'code': 0,
        'message': '',
        'timestamp': data['timestamp'],
        'uuid': data['uuid']
    }
    data_obj = data["data"]
    for key in data_obj.keys():
        command = key
        command_payload = data_obj[key]
        if command == "firmware" and command_payload:
            if "data" in command_payload:
                if "filename" in command_payload:
                    filename = command_payload["filename"]
                else:
                    filename = uuid.uuid1()
                # save data to file
                with open('./firmwares/' + filename, 'wb') as f:
                    f.write(base64.b64decode(command_payload["data"]))
            else:
                filename = command_payload["filename"]
            for device in command_payload["devices"]:
                dongle_command_handle(device=device, timestamp=data["timestamp"], uuid=data["uuid"], data={
                    "firmware": {
                        "filename": filename
                    }
                })
        elif command == 'label':
            label = command_payload['data']
            DBSimulator(ip=ip).update({'label': data['data']['label']['data']})
            # update
            data = pack_payload({'label': label})
            topic = mqtt_version + "/simulator/update"
            logger.info("Publish: topic:%s", topic)
            brokers = get_value('brokers')
            if brokers and '127.0.0.1' in brokers:
                brokers['127.0.0.1'].publish(topic, data, qos=2)
        elif command == 'config':
            devices = command_payload['devices']
            for device in devices:
                dongle_command_handle(device=device, timestamp=data["timestamp"], uuid=data["uuid"], data=data_obj)
        else:
            logger.warn("unsupported command:%s", command)
            raise Exception("unsupported command: " + command)
    simulator_error_callback(rsp)


@router.route('/simulator/devices/+/command')
@except_handle(dongle_error_callback)
def simulator_device_command(client, ip, payload, device):
    data = json.loads(payload)
    dongle_command_handle(device=device, timestamp=data["timestamp"], uuid=data["uuid"], data=data["data"])


def pack_simulator_info():
    version = '1.0'
    with open('./version/version.txt', 'r') as f:
        version = f.read()
    data = {
        "ip": get_ip_address(),
        "mac": client_mac,
        "name": "simulator-" + client_ip,
        "connected": 1,
        "label": user_label,
        "version": version
    }
    # 打包dongles信息
    #lock.acquire()
    try:
        devices = DBDevice(ip=get_ip_address()).retrieve()
        for device in devices:
            zigbee = DBZigbee(mac=device['mac']).retrieve()[0]
            device['zigbee'] = zigbee
        data['devices'] = devices
    except Exception as e:
        logger.exception("pack dongle info failed")
        data['devices'] = []
    finally:
        #lock.release()
        pass
    return data

