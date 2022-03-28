import logging
import logging.config
import os
import sys

import rapidjson
from .logConfig import config_dict
#with open(os.path.split(os.path.realpath(__file__))[0]+'/logConfig.py', 'r') as f:
#    print("read logConfig.py")
#    dict_conf = rapidjson.load(f)
logging.config.dictConfig(config_dict)

launcherLogger = logging.getLogger('Launcher')
simulatorLogger = logging.getLogger('Simulator')
dongleLogger = logging.getLogger('Dongle')
databaseLogger = logging.getLogger('Database')
flaskLogger = logging.getLogger("Flask")
mqttLogger = logging.getLogger("Mqtt")
