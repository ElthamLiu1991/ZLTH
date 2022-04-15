from hashlib import md5

import rapidjson
import rapidjson as json

import zigbeeLauncher.logging
from ..database import db
from ..database.device import Device
from . import router, mqtt_version, client_ip, payload_validate
from .WiserZigbeeGlobal import get_value, set_value, pack_payload
from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee, DBZigbeeEndpoint, \
    DBZigbeeEndpointCluster, DBZigbeeEndpointClusterAttribute
from zigbeeLauncher.logging import launcherLogger as logger


def insert_device(device):
    try:
        mac = device['mac']
        DBDevice(mac=mac).add(device)
        if 'zigbee' in device:
            device['zigbee']['mac'] = mac
            DBZigbee(mac=mac).add(device["zigbee"])
            # 删除endpoint数据
            DBZigbeeEndpoint(mac=mac).delete()
            # 删除endpointCluster数据
            DBZigbeeEndpointCluster(mac=mac).delete()
            # 删除endpointClusterAttribute数据
            DBZigbeeEndpointClusterAttribute(mac=mac).delete()
            endpoints = device['zigbee']['endpoints']
            for endpoint in endpoints:
                endpoint_id = endpoint['endpoint']
                endpoint['mac'] = mac
                DBZigbeeEndpoint(mac=mac, endpoint=endpoint_id).add(endpoint)
                for cluster in endpoint['server_clusters']:
                    cluster['mac'] = mac
                    cluster['endpoint'] = endpoint_id
                    cluster['server'] = True
                    DBZigbeeEndpointCluster(
                        mac=mac,
                        endpoint=endpoint_id,
                        cluster=cluster['cluster'],
                        server=True).add(cluster)
                    for attribute in cluster['attributes']:
                        attribute['mac'] = mac
                        attribute['endpoint'] = endpoint_id
                        attribute['server'] = True
                        attribute['cluster'] = cluster['cluster']
                        DBZigbeeEndpointClusterAttribute(
                            mac=mac,
                            endpoint=endpoint_id,
                            cluster=cluster['cluster'],
                            server=True,
                            attribute=attribute['attribute']).add(attribute)
                for cluster in endpoint['client_clusters']:
                    cluster['mac'] = mac
                    cluster['endpoint'] = endpoint_id
                    cluster['server'] = False
                    DBZigbeeEndpointCluster(
                        mac=mac,
                        endpoint=endpoint_id,
                        cluster=cluster['cluster'],
                        server=False).add(cluster)
                    for attribute in cluster['attributes']:
                        attribute['mac'] = mac
                        attribute['endpoint'] = endpoint_id
                        attribute['server'] = False
                        attribute['cluster'] = cluster['cluster']
                        DBZigbeeEndpointClusterAttribute(
                            mac=mac,
                            endpoint=endpoint_id,
                            cluster=cluster['cluster'],
                            server=False,
                            attribute=attribute['attribute']).add(attribute)
    except Exception as e:
        logger.exception("insert device failed: %s", e)


@router.route('/simulator/info')
def simulator_info(client, ip, payload):
    try:
        payload_validate(payload)
        # 加入数据库
        data = json.loads(payload)
        data_obj = data["data"]
        if 'devices' in data_obj:
            devices = data_obj["devices"]
            for device in devices:
                device['ip'] = ip
                insert_device(device)
        DBSimulator(mac=data_obj["mac"]).add(data_obj)
        # 删除所有相关的devices
        #if ip != client_ip:
            #DBDevice(ip=data_obj['mac']).delete()
            # 重新插入新设备

            # 获取devices
            # request_simulator_info(client, ip)
    except Exception as e:
        logger.exception("payload validation failed: %s", e)
    finally:
        pass


@router.route('/simulator/devices/+/info')
def simulator_device_info(client, ip, payload, device):
    try:
        payload_validate(payload)
        # 加入数据库
        data = json.loads(payload)
        data_obj = data["data"]
        insert_device(data_obj)
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
        DBSimulator(mac=ip).update(data["data"])
    except Exception as e:
        logger.error('Falied to update simulator:%s', e)


@router.route('/simulator/devices/+/update')
def simulator_device_update(client, ip, payload, device):
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
        if 'attribute' in data['data']:
            # attribute table
            if DBZigbeeEndpointClusterAttribute(mac=device).retrieve():
                DBZigbeeEndpointClusterAttribute(mac=device,
                                                 endpoint=data['data']['attribute']['endpoint'],
                                                 cluster=data['data']['attribute']['cluster'],
                                                 server=data['data']['attribute']['server'],
                                                 attribute=data['data']['attribute']['attribute']
                                                 ).update(data['data']['attribute'])

            del data['data']['attribute']
        if DBDevice(mac=device).retrieve():
            if data['data']:
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
    logger.info("Publish: topic:%s", topic)
    client.publish(topic, payload=None, qos=2)


def request_simulator_info(client, ip):
    topic = mqtt_version + "/" + ip + "/simulator"
    logger.info("Publish: topic:%s", topic)
    client.publish(topic, payload=None, qos=2)


def request_dongle_info(client, ip, dongle):
    topic = mqtt_version + "/" + ip + "/simulator/devices/" + dongle
    logger.info("Publish: topic:%s", topic)
    client.publish(topic, payload=None, qos=2)


def simulator_command(simulator, body):
    brokers = get_value('brokers')
    if brokers:
        for value in brokers.values():
            data = pack_payload(body)
            topic = mqtt_version + "/" + simulator + "/simulator/command"
            logger.info("Publish: topic:%s", topic)
            value.publish(topic, data)
            break
    else:
        logger.warn("Launcher MQTT client not ready")


def dongle_command(simulator, name, body):
    print("this is dongle command", simulator, name, body)
    brokers = get_value('brokers')
    if brokers:
        for value in brokers.values():
            data = pack_payload(body)
            topic = mqtt_version + "/" + simulator + "/simulator/devices/" + name + "/command"
            logger.info("Publish: topic:%s", topic)
            value.publish(topic, data)
            break
    else:
        logger.warn("Launcher MQTT client not ready")