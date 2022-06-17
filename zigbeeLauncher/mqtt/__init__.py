import time

from zigbeeLauncher.database.interface import DBDevice, DBSimulator, DBZigbee
from zigbeeLauncher.util import _init, Router, get_ip_address, get_mac_address, get_version, set_value
_init()
router = Router()
set_value('mqtt_version',  "v1.0")


def init():
    client_ip = get_ip_address()
    set_value('client_ip', client_ip)
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
    # get current version
    from zigbeeLauncher.mqtt.Simulator import Simulator
    simulator = Simulator(client_ip, client_mac, user_label, version)
    simulator.start()
    set_value('simulator', simulator)
    import zigbeeLauncher.mqtt.Simulator_API
    import zigbeeLauncher.mqtt.Launcher_API
    from zigbeeLauncher.mqtt.Instance import brokers
    while simulator.ip not in brokers:
        time.sleep(0.5)
        # upload simulator info
    from zigbeeLauncher.mqtt.Callbacks import simulator_info_callback
    simulator_info_callback(simulator.get())
    # instance simulator

