import time

import rapidjson as json
from .WiserZigbeeGlobal import _init, get_value, set_value, Router, Response, get_ip_address, get_mac_address
from zigbeeLauncher.logging import mqttLogger as logger
mqtt_version = "v1.0"
payload_validate = json.Validator('{"required":["timestamp", "uuid", "data"]}')
client_ip = get_mac_address()
client_mac = get_mac_address()
router = Router()
response = Response()
_init()


from .WiserZigbeeLauncherMqtt import WiserMQTT


def init(role):
    if role == "simulator" or role == "launcher":
        from zigbeeLauncher.database.interface import DBDevice, DBSimulator
        DBDevice().delete()
        DBSimulator().delete()
        if not get_value("connected"):
            logger.info("Run %s MQTT client" % role)
            thread = WiserMQTT('broker.emqx.io', 1883, client_ip, role)
            thread.start()
            return thread
        else:
            return None
    else:
        logger.fatal('Only support "launcher" or "simulator" client type')
        return None
