import time

from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee, DBAuto
from zigbeeLauncher.util import get_ip_address, get_mac_address, get_version, Global
from zigbeeLauncher.simulator.simulator import Simulator
from zigbeeLauncher.logging import simulatorLogger as logger

def init(port):
    client_ip = get_ip_address()
    client_mac = get_mac_address()
    version = get_version()
    logger.info(f"simulator: ip:{client_ip}, mac:{client_mac}, verison:{version}")
    try:
        user_label = DBSimulator(mac=client_mac).retrieve()[0]['label']
    except Exception as e:
        user_label = ""
    # 删除所有数据
    DBSimulator().delete()
    DBDevice().delete()
    DBZigbee().delete()
    # DBAuto().delete()
    # get current version
    simulator = Simulator(client_ip, client_mac, user_label, version, port)

