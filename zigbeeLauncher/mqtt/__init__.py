import threading
import time
from typing import cast

from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo, IPVersion

from zigbeeLauncher.logging import mqttLogger as logger
import rapidjson as json
from .WiserZigbeeGlobal import _init, get_value, set_value, Router, Response, get_ip_address, get_mac_address

mqtt_version = "v1.0"
payload_validate = json.Validator('{"required":["timestamp", "uuid", "data"]}')
client_mac = get_mac_address()
router = Router()
response = Response()
_init()
global client_ip
client_ip = ""
while True:
    client_ip = get_ip_address()
    if client_ip:
        break
    logger.warning("get ip address failed, waiting")
    time.sleep(1)

from zigbeeLauncher.database.interface import DBDevice, DBSimulator
# 将所有数据设置为offline
DBSimulator().update({"connected": False})
DBDevice().update({"connected": False})
# 删除本地数据
DBDevice(ip=client_mac).delete()
# DBSimulator(mac=client_mac).delete()

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
                continue
            """
            logger.info("Run %s MQTT client: launcher")
            thread = WiserMQTT(addr, cast(int, info.port), get_mac_address(), 'launcher')
            thread.start()
            """
            logger.info("Run MQTT client: simulator")
            if addr == client_ip:
                logger.info("connect to 127.0.0.1 broker")
                thread = WiserMQTT('127.0.0.1', cast(int, info.port), client_ip, 'simulator')
            else:
                thread = WiserMQTT(addr, cast(int, info.port), client_ip, 'simulator')
            thread.start()

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s update, service info:%s", name, info)
        for addr in info.parsed_scoped_addresses():
            brokers = get_value('brokers')
            if brokers and addr in brokers:
                continue
            """
            logger.info("Run %s MQTT client: launcher")
            thread = WiserMQTT(addr, cast(int, info.port), get_mac_address(), 'launcher')
            thread.start()
            """
            logger.info("Run %s MQTT client: simulator")
            thread = WiserMQTT(addr, cast(int, info.port), client_ip, 'simulator')
            thread.start()


ServiceBrowser(Zeroconf(), "_launcher._tcp.local.", MyListener())


def init():
    logger.info("register launcher service")
    info = ServiceInfo(
        "_launcher._tcp.local.",
        str(get_mac_address()) + "._launcher._tcp.local.",
        addresses=[client_ip],
        port=1883,
        properties={'timestamp': round(int(time.time() * 1000 * 1000))},
        server=str(get_mac_address()) + '.local.',
    )
    zeroconf = Zeroconf(ip_version=IPVersion.All)
    zeroconf.register_service(info)
