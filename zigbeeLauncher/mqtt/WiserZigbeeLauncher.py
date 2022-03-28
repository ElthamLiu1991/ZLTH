import rapidjson
import rapidjson as json

import zigbeeLauncher.logging
from ..database import db
from ..database.device import Device
from . import router, mqtt_version, client_ip, payload_validate
from .WiserZigbeeGlobal import get_value, set_value, pack_payload
from zigbeeLauncher.database.interface import DBDevice, DBSimulator
from zigbeeLauncher.logging import launcherLogger as logger


@router.route('/simulator/info')
def simulator_info(client, ip, payload):
    try:
        payload_validate(payload)
        # 加入数据库
        data = json.loads(payload)
        data_obj = data["data"]
        DBSimulator(mac=data_obj["mac"]).add(data_obj)
    except Exception as e:
        logger.error("payload validation failed: %s", e)
    finally:
        pass


@router.route('/simulator/devices/+/info')
def simulator_device_info(client, ip, payload, device):
    try:
        payload_validate(payload)
        # 加入数据库
        data = json.loads(payload)
        data_obj = data["data"]
        DBDevice(mac=data_obj["mac"]).add(data_obj)
    except Exception as e:
        logger.error("payload validation failed:%s", e)
    finally:
        pass


@router.route('/simulator/update')
def simulator_update(client, ip, payload):
    """
    更新对于simulator的所有设备状态
    :param client:
    :param ip:
    :param payload:
    :return:
    """
    try:
        payload_validate(payload)
        # update database
        data = json.loads(payload)
        DBDevice(ip=ip).update(data["data"])
    except Exception as e:
        logger.error('Falied to update simulator:%s', e)


@router.route('/simulator/devices/+/update')
def simulator_device_update(client, ip, payload, device):
    try:
        payload_validate(payload)
        # update database
        data = json.loads(payload)
        # 先判断dongle是否存在
        if DBDevice(mac=device).retrieve():
            DBDevice(mac=device).update(data["data"])
        else:
            # 不存在，获取dongle信息
            request_dongle_info(client, ip, device)
    except Exception as e:
        logger.error("update failed:%s", e)


@router.route('/simulator/error')
def simulator_device_error(client, ip, payload):
    pass


@router.route('/simulator/devices/+/error')
def simulator_device_error(client, ip, payload, device):
    pass


def request_synchronization(client):
    topic = mqtt_version + "/synchronization"
    client.publish(topic, payload=None, qos=2)


def request_simulator_info(client, ip):
    topic = mqtt_version + "/" + ip + "/simulator"
    client.publish(topic, payload=None, qos=2)


def request_dongle_info(client, ip, dongle):
    topic = mqtt_version + "/" + ip + "/simulator/devices/" + dongle
    client.publish(topic, payload=None, qos=2)


def simulator_command(simulator, body):
    client = get_value('launcher')
    if client:
        data = pack_payload(body)
        topic = mqtt_version + "/" + simulator + "/simulator/command"
        logger.info("Publish: topic:%s", topic)
        client.publish(topic, data)
    else:
        logger.warn("Launcher MQTT client not ready")


def dongle_command(simulator, name, body):
    print("this is dongle command", simulator, name, body)
    client = get_value('launcher')
    if client:
        data = pack_payload(body)
        topic = mqtt_version + "/" + simulator + "/simulator/devices/" + name + "/command"
        logger.info("Publish: topic:%s", topic)
        client.publish(topic, data)
    else:
        logger.warn("Launcher MQTT client not ready")