import time

from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee, DBAuto
from zigbeeLauncher.util import Router, get_ip_address, get_mac_address, get_version
mqtt_version = 'v1.0'
router = Router()

def init():
    client_ip = get_ip_address()
    client_mac = get_mac_address()
    version = get_version()
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
    import zigbeeLauncher.mqtt.Simulator_API
    import zigbeeLauncher.mqtt.Launcher_API
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator(client_ip, client_mac, user_label, version)
    simulator.start()


