import datetime
import importlib
import json
import os
import threading
import time
from zigbeeLauncher.logging import autoLogger as logger

from flask_socketio import emit

from zigbeeLauncher import socketio, base_dir

START = 'start'
PREPARING = 'preparing'
WORKING = 'running'
DONE = 'done'
FINISH = 'finish'

INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'

FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
STOP = 'STOP'


@socketio.event
def connect():
    script = AutoTesting().get_script()
    emit('my_script', {'data': script})
    if script:
        with open(os.path.join(base_dir, 'scripts/{}.json'.format(script)), encoding='utf-8') as f:
            config = f.read()
            emit('my_config', {'data': config})

        emit('my_status', {'data': 'ready'})


@socketio.event
def update_request(message):
    print("update config", message['data'])
    config = json.loads(message['data'])
    script = AutoTesting().get_script()
    with open(os.path.join(base_dir, 'scripts/{}.json'.format(script)), 'w+', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


@socketio.event
def start_request():
    print("start script")
    emit('my_status', {'data': 'running'})
    AutoTesting().run()


@socketio.event
def stop_request():
    print("stop script")
    emit('my_status', {'data': 'stopping'})
    AutoTesting().stop()


def auto_record(state, status, message):
    """
    保存脚本运行记录到文本
    :param state: 'start', 'preparing', 'working', 'done', 'failed'
    :param status: 'info', 'error', 'warning'
    :param message:
    :return:
    """
    testing = AutoTesting()
    if testing.is_running():
        timestamp = '{}.{}'.format(time.strftime("%Y-%m-%d_%H-%M-%S"),
                                   str(datetime.datetime.now().microsecond * 1000)[:4])
        with open(os.path.join(base_dir, 'scripts/' + testing.record()), 'a+') as f:
            data = '{}:{}:{}:{}\n'.format(
                timestamp,
                state,
                status,
                message)
            logger.info(data)
            f.write(data)
            socketio.emit('my_response',
                          {
                              'timestamp': timestamp,
                              'state': state,
                              'status': status,
                              'data': message
                          })


class AutoTesting:
    _instance = None
    _running = False
    _record = None
    _script = None
    _result = SUCCESS
    _testing = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def run(self):
        print(f"running:{self._running}")
        if not self._running:
            self._running = True
            self._record = 'capacity-' + time.strftime("%Y-%m-%d_%H-%M-%S") + '.log'
            testing = importlib.import_module('zigbeeLauncher.auto_scripts.' + self._script)
            self._testing = testing.Testing(self.on_status)

            if self._testing.preparing():
                self._testing.start()

    def stop(self):
        if self._testing:
            self._testing.stop()

    def on_status(self, state, status):
        if status == SUCCESS and (state == PREPARING or state == WORKING):
            self._running = True
            socketio.emit('my_status', {'data': state})
        else:
            self._running = False
            self._record = None
            self._testing = None
            self._testing = None
            socketio.emit('my_status', {'data': status})
            socketio.emit('finish', {'data': status})

    def is_ready(self):
        if self._running:
            return False
        else:
            return True

    def is_running(self):
        if self._running:
            return True
        else:
            return False

    def record(self):
        return self._record

    def name(self):
        return self._script

    def set_script(self, script):
        self._script = script

    def get_script(self):
        return self._script
