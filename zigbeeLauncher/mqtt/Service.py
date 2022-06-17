from typing import cast
from zigbeeLauncher.database.interface import DBSimulator
from zigbeeLauncher.logging import mqttLogger as logger
from zigbeeLauncher.mqtt.Instance import brokers, WiserMQTT
from zigbeeLauncher.util import get_ip_address, get_value


class ServicesListener:
    def remove_service(self, zeroconf, type, name):
        logger.info("Service %s removed", name)
        if name in brokers:
            del brokers[name]

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s added, service info: %s", name, info)
        for addr in info.parsed_scoped_addresses():
            if brokers and addr in brokers:
                logger.warning('already connected to broker:%s', addr)
                continue
            ip = get_value('client_ip')
            if addr == ip:
                continue
            logger.info("Run MQTT client: edge")
            thread = WiserMQTT(addr, cast(int, info.port), 'edge')
            thread.start()

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.info("Service %s update, service info:%s", name, info)
        for addr in info.parsed_scoped_addresses():
            if brokers and addr in brokers:
                logger.info('already connected to broker:%s', addr)
                DBSimulator(ip=addr).update({'connected': 1})
                continue
            logger.info("Run MQTT client: edge")
            thread = WiserMQTT(addr, cast(int, info.port), 'edge')
            thread.start()