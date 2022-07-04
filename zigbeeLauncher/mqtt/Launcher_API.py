import time
import uuid
import rapidjson as json


from . import router
from zigbeeLauncher.util import send_command, payload_validate
from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee
from zigbeeLauncher.logging import launcherLogger as logger
from zigbeeLauncher.request_and_response import add_response


def insert_device(device):
    try:

        mac = device['mac']
        DBDevice(mac=mac).add(device)
        if 'zigbee' in device:
            device['zigbee']['mac'] = mac
            DBZigbee(mac=mac).add(device["zigbee"])
    except Exception as e:
        logger.exception("insert device failed: %s", e)


@router.route('/simulator/info')
def simulator_info(ip, payload):
    try:
        #lock.acquire()
        payload_validate(payload)
        # 加入数据库
        data = json.loads(payload)
        data_obj = data["data"]
        DBSimulator(mac=data_obj["mac"]).add(data_obj)
        if 'devices' in data_obj:
            devices = data_obj["devices"]
            for device in devices:
                device['ip'] = data_obj['ip']
                insert_device(device)
        # 删除所有相关的devices
        #if ip != client_ip:
            #DBDevice(ip=data_obj['mac']).delete()
            # 重新插入新设备

            # 获取devices
            # request_simulator_info(client, ip)
    except Exception as e:
        logger.exception("payload validation failed: %s", e)
    finally:
        #lock.release()
        pass


@router.route('/simulator/devices/+/info')
def simulator_device_info(ip, payload, device):
    try:
        #lock.acquire()
        payload_validate(payload)
        # 加入数据库
        data = json.loads(payload)
        data_obj = data["data"]
        insert_device(data_obj)
        # print("insert device finish")
    except Exception as e:
        logger.error("payload validation failed:%s", e)
    finally:
        #lock.release()
        pass


@router.route('/simulator/update')
def simulator_update(ip, payload):
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
        if 'connected' in data['data']:
            DBDevice(ip=ip).update(data["data"])
        DBSimulator(ip=ip).update(data["data"])
    except Exception as e:
        logger.error('Falied to update simulator:%s', e)


@router.route('/simulator/devices/+/update')
def simulator_device_update(ip, payload, device):
    try:
        payload_validate(payload)
        # update database
        data = json.loads(payload)
        # 先判断dongle是否存在
        if 'process' in data['data']:
            del data['data']['process']
        if 'zigbee' in data['data']:
            # zigbee table
            if DBZigbee(mac=device).retrieve():
                DBZigbee(mac=device).update(data['data']['zigbee'])
            del data['data']['zigbee']
        if DBDevice(mac=device).retrieve():
            if data['data']:
                DBDevice(mac=device).update(data["data"])
        else:
            logger.warn("device %s not in database", device)
            # 不存在，获取dongle信息
            # request_dongle_info(client, ip, device)
    except Exception as e:
        logger.error("update failed:%s", e)


@router.route('/simulator/error')
def simulator_error(ip, payload):
    add_response(json.loads(payload))
    pass


@router.route('/simulator/devices/+/error')
def simulator_device_error(ip, payload, device):
    add_response(json.loads(payload))
    pass


def request_synchronized(client, body):
    from zigbeeLauncher.mqtt import mqtt_version
    topic = mqtt_version + "/simulator/synchronized"
    logger.info("Publish: topic:%s", topic)
    client.publish(topic, payload=body, qos=2)


def request_simulator_info(client, ip):
    from zigbeeLauncher.mqtt import mqtt_version
    topic = mqtt_version + "/" + ip + "/simulator"
    logger.info("Publish: topic:%s", topic)
    client.publish(topic, payload=None, qos=2)


def request_dongle_info(client, ip, dongle):
    from zigbeeLauncher.mqtt import mqtt_version
    topic = mqtt_version + "/" + ip + "/simulator/devices/" + dongle
    logger.info("Publish: topic:%s", topic)
    client.publish(topic, payload=None, qos=2)


def simulator_command_2(ip, body, timeout=10):
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        if ip == simulator.ip:
            topic = mqtt_version + "/simulator/command"
        else:
            topic = mqtt_version + "/" + ip + "/simulator/command"
        return send_command(simulator.client, topic, body, timeout)

    else:
        logger.error("Launcher %s MQTT client not ready", ip)
        return {'code': 90007,
                'message': 'simulator {} not connected'.format(ip),
                'timestamp': int(round(time.time() * 1000)),
                'uuid': str(uuid.uuid1())}


def dongle_command_2(ip, name, body, timeout=10):
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator()
    if simulator.client:
        from zigbeeLauncher.mqtt import mqtt_version
        if ip == simulator.ip:
            topic = mqtt_version + "/simulator/devices/" + name + "/command"
        else:
            topic = mqtt_version + "/" + ip + "/simulator/devices/" + name + "/command"
        return send_command(simulator.client, topic, body, timeout)

    else:
        logger.error("Launcher %s MQTT client not ready", ip)
        return {'code': 90007,
                'message': 'simulator {} not connected'.format(ip),
                'timestamp': int(round(time.time() * 1000)),
                'uuid': str(uuid.uuid1())}
