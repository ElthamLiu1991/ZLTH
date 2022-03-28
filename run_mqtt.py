import os
import time

from zigbeeLauncher import mqtt
import sys
from zigbeeLauncher.mqtt.WiserZigbeeGlobal import get_value

if __name__ == "__main__":
    # create folder firmwares and logs
    if not os.path.exists('./firmwares'):
        os.mkdir('./firmwares')
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    if len(sys.argv) == 2:
        print(sys.argv[1])
        mqtt.init(sys.argv[1])
    else:
        mqtt.init("simulator")
