from typing import cast
from zigbeeLauncher.logging import mqttLogger as logger
from zigbeeLauncher.mqtt.Connection import ZLTHMQTT
from zigbeeLauncher.util import get_ip_address


class ServicesListener:
    def remove_service(self, zeroconf, type, name):
        logger.info("Service %s removed", name)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s added, service info: %s", name, info)
        for addr in info.parsed_scoped_addresses():
            ip = get_ip_address()
            if addr == ip:
                continue
            logger.info("Run MQTT client: edge")
            thread = ZLTHMQTT(addr, cast(int, info.port), 'edge')
            thread.start()

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s update, service info:%s", name, info)
        for addr in info.parsed_scoped_addresses():
            logger.info("Run MQTT client: edge")
            thread = ZLTHMQTT(addr, cast(int, info.port), 'edge')
            thread.start()