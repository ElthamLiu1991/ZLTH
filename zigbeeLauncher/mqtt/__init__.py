import sys
import threading
import time
from typing import cast

from ..database.interface import DBDevice, DBSimulator, DBZigbee, DBZigbeeEndpoint, DBZigbeeEndpointCluster, \
    DBZigbeeEndpointClusterAttribute
from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo, IPVersion

from zigbeeLauncher.logging import mqttLogger as logger
import rapidjson as json
from .WiserZigbeeGlobal import _init, get_value, set_value, Router, Response, get_ip_address, get_mac_address

mqtt_version = "v1.0"
payload_validate = json.Validator('{"required":["timestamp", "uuid", "data"]}')
client_mac = get_mac_address()
try:
    user_label = DBSimulator(mac=client_mac).retrieve()[0]['label']
except Exception as e:
    user_label = ""
# 删除所有数据
DBSimulator().delete()
DBDevice().delete()
DBZigbee().delete()
DBZigbeeEndpoint().delete()
DBZigbeeEndpointCluster().delete()
DBZigbeeEndpointClusterAttribute().delete()
router = Router()
response = Response()
_init()
while True:
    client_ip = get_ip_address()
    if client_ip:
        break
    logger.warning("get ip address failed, waiting")
    time.sleep(1)
from threading import RLock
lock = RLock()
from .WiserZigbeeLauncherMqtt import WiserMQTT


class MyListener:

    def remove_service(self, zeroconf, type, name):
        logger.info("Service %s removed", name)
        brokers = get_value("brokers")
        if name in brokers:
            del brokers[name]
            set_value("brokers", brokers)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s added, service info: %s", name, info)
        for addr in info.parsed_scoped_addresses():
            brokers = get_value('brokers')
            if brokers and addr in brokers:
                logger.info('already connected to broker:%s', addr)
                continue
            """
            logger.info("Run %s MQTT client: launcher")
            thread = WiserMQTT(addr, cast(int, info.port), get_mac_address(), 'launcher')
            thread.start()
            """
            logger.info("Run MQTT client: edge")
            thread = WiserMQTT(addr, cast(int, info.port), get_ip_address(), 'edge')
            thread.start()

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s update, service info:%s", name, info)
        for addr in info.parsed_scoped_addresses():
            brokers = get_value('brokers')
            if brokers and addr in brokers:
                logger.info('already connected to broker:%s', addr)
                # get /simulator/info
                topic = mqtt_version + "/" + client_ip + "/synchronized"
                logger.info("Publish: topic:%s", topic)
                brokers[addr].publish(topic, payload=None, qos=2)
                continue
            """
            logger.info("Run %s MQTT client: launcher")
            thread = WiserMQTT(addr, cast(int, info.port), get_mac_address(), 'launcher')
            thread.start()
            """
            logger.info("Run MQTT client: edge")
            thread = WiserMQTT(addr, cast(int, info.port), get_ip_address(), 'edge')
            thread.start()


def init():
    # start simulator client
    logger.info("Run MQTT client: simulator")
    thread = WiserMQTT('127.0.0.1', 1883, '127.0.0.1', 'simulator')
    thread.start()
    ServiceBrowser(Zeroconf(), "_launcher._tcp.local.", MyListener())
    if sys.platform.startswith('darwin'):
        thread = WiserMQTT('127.0.0.1', 1883, get_ip_address(), 'simulator')
        thread.start()
    logger.info("register launcher service")
    info = ServiceInfo(
        "_launcher._tcp.local.",
        str(get_mac_address()) + "._launcher._tcp.local.",
        addresses=[get_ip_address()],
        port=1883,
        properties={'timestamp': round(int(time.time() * 1000 * 1000))},
        server=str(get_mac_address()) + '.local.',
    )
    zeroconf = Zeroconf(ip_version=IPVersion.All)
    zeroconf.register_service(info)

