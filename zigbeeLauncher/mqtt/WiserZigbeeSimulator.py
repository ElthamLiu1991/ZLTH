import base64
import os
import time
import uuid

import rapidjson

from . import router, mqtt_version, client_ip, client_mac, payload_validate
from .WiserZigbeeGlobal import pack_payload, get_value, except_handle, get_ip_address
from .WiserZigbeeDongle import upload_port_info, dongle_command_handle
from zigbeeLauncher.logging import simulatorLogger as logger
from ..database.interface import DBDevice


def simulator_error_callback(device, msg):
    logger.exception("Simulator error")
    data = pack_payload(msg)
    topic = mqtt_version + "/" + client_ip + "/simulator/error"
    logger.info("Publish: topic:%s, payload:%s", topic, rapidjson.dumps(data, indent=2))
    get_value("simulator").publish(topic, data, qos=2)


def synchronization(client):
    """
    发送simulator/info以及simulator/devices/*/info进行同步
    :return:
    """
    try:
        data = pack_payload(pack_simulator_info())
        topic = mqtt_version + "/" + client_ip + "/simulator/info"
        client.publish(topic, data)
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
    payload_validate(payload)
    data = rapidjson.loads(payload)
    data_obj = data["data"]
    command = data_obj["command"]
    command_payload = data_obj["payload"]
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
                "command": "firmware",
                "payload": {
                    "filename": filename
                }
            })
    else:
        logger.warn("unsupported command:%s", command)
        raise Exception("unsupported command: " + command)


@router.route('/simulator/devices/+/command')
@except_handle(simulator_error_callback)
def simulator_device_command(client, ip, payload, device):
    payload_validate(payload)
    data = rapidjson.loads(payload)
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
        "label": "",
        "version": version
    }
    return data


def dongle_info_callback(name, msg):
    msg["ip"] = client_ip
    data = pack_payload(msg)
    topic = mqtt_version + "/" + client_ip + "/simulator/devices/" + name + "/info"
    logger.info("Publish: topic:%s, payload:%s", topic, rapidjson.dumps(data, indent=2))
    get_value("simulator").publish(topic, data, qos=2)


def dongle_update_callback(name, msg):
    data = pack_payload(msg)
    topic = mqtt_version + "/" + client_ip + "/simulator/devices/" + name + "/update"
    logger.info("Publish: topic:%s, payload:%s", topic, rapidjson.dumps(data, indent=2))
    get_value("simulator").publish(topic, data, qos=2)


def dongle_error_callback(name, msg):
    logger.exception("Dongle error")
    data = pack_payload(msg)
    topic = mqtt_version + "/" + client_ip + "/simulator/devices/" + name + "/error"
    logger.info("Publish: topic:%s, payload:%s", topic, rapidjson.dumps(data, indent=2))
    get_value("simulator").publish(topic, data, qos=2)
