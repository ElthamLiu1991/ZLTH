import json
import logging
import logging.config
import os
import sys


with open('./logConfig.json', 'r') as f:
    print("read logConfig.py")
    dict_conf = json.load(f)
logging.config.dictConfig(dict_conf)

launcherLogger = logging.getLogger('Launcher')
simulatorLogger = logging.getLogger('Simulator')
dongleLogger = logging.getLogger('Dongle')
databaseLogger = logging.getLogger('Database')
flaskLogger = logging.getLogger("Flask")
mqttLogger = logging.getLogger("MQTT")
utilLogger = logging.getLogger('Util')
autoLogger = logging.getLogger('Auto')
serialLogger = logging.getLogger('SerialProtocol')
errorLogger = logging.getLogger('Error')
