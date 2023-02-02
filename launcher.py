import os
import subprocess
import sys
import time
import socket
import json

from zigbeeLauncher import create_app

if __name__ == "__main__":
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    # 判断服务是否已经启动

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ret = s.connect_ex(('localhost', 5000))
    if ret == 0:
        from zigbeeLauncher.logging import flaskLogger as logger
        logger.fatal("5000 in used")
        sys.exit(-1)

    if not os.path.exists('./database'):
        os.mkdir('./database')
    if not os.path.exists('./files'):
        os.mkdir('./files')

    if not os.path.exists('./firmwares'):
        os.mkdir('./firmwares')
    if not os.path.exists('./version/'):
        os.mkdir('./version')
    if not os.path.exists('./records/'):
        os.mkdir('./records')
    if not os.path.exists('./hub/'):
        os.mkdir('./hub')
    socketio, app = create_app()
    socketio.run(app, host='0.0.0.0', use_reloader=False, allow_unsafe_werkzeug=True)
