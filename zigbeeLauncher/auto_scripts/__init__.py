import datetime
import importlib
import json
import os
import threading
import time

from zigbeeLauncher.database.interface import DBAuto
from zigbeeLauncher.logging import autoLogger as logger

from flask_socketio import emit, join_room, close_room

from zigbeeLauncher import socketio, base_dir

READY = 'ready'
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


# @socketio.event
# def connect():
#     script = AutoTesting().get_script()
#     emit('my_script', {'data': script})
#     if script:
#         with open(os.path.join(base_dir, 'scripts/{}.json'.format(script)), encoding='utf-8') as f:
#             config = f.read()
#             emit('my_config', {'data': config})
#
#         emit('my_status', {'data': 'ready'})


@socketio.on('join')
def join(message):
    script = message['record']
    logger.debug(f'join room:{script}')
    join_room(script)
    if AutoTesting().ready(script):
        logger.debug(f"ready:{script}")
        emit('my_status', {'data': READY}, room=script)
        with open(os.path.join(base_dir, 'scripts/'+script.split('-')[0]+'.json'), encoding='utf-8') as f:
            emit('my_config', {'data':f.read()}, room=script)
    else:
        logger.debug("{} is history record".format(script))
        record = DBAuto(record=script).retrieve()
        if record:
            record = record[0]
            status = record['status']
            config = record['config']
            emit('my_status', {'data': status}, room=script)
            emit('my_config', {'data': config}, room=script)
            with open(os.path.join(base_dir, 'records/' + script)) as f:
                emit('my_record', {'data': f.read()}, room=script)
                return


@socketio.on('close')
def close(message):
    close_room(message['record'])


@socketio.event
def update_request(message):
    logger.debug("update config {} for script:{}".format(message['data'], message["record"]))
    config = json.loads(message['data'])
    script = message['record']

    AutoTesting().update_config(script, config)


@socketio.event
def start_request(message):
    record = message['record']
    logger.debug(f"start script:{record}")
    emit('my_status', {'data': 'running'}, room=record)
    AutoTesting().start(record)


@socketio.event
def stop_request(message):
    record = message['record']
    logger.debug(f"stop script:{record}")
    emit('my_status', {'data': 'stopping'}, room=record)
    AutoTesting().stop(record)


def auto_record(record, state, status, message):
    """
    保存脚本运行记录到文本
    :param record:
    :param state: 'start', 'preparing', 'working', 'done', 'failed'
    :param status: 'info', 'error', 'warning'
    :param message:
    :return:
    """
    # DBAuto(record=record).update({
    #     'state': state,
    #     'status': status
    # })
    timestamp = '{}.{}'.format(time.strftime("%Y-%m-%d_%H-%M-%S"),
                               str(datetime.datetime.now().microsecond * 1000)[:4])
    with open(os.path.join(base_dir, 'records/' + record), 'a+') as f:
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
                      }, room=record)


class AutoTesting:
    _instance = None
    _records = {}
    _script = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def set_script(self, script):
        self._script = script
        return self.run()

    def run(self):
        testing = importlib.import_module('zigbeeLauncher.auto_scripts.' + self._script)
        test = testing.Testing(self.on_status)
        record = test.get_record()
        if record:
            self._records[record] = test
            # add to database
            DBAuto(record=record).add({
                'script': test.get_script(),
                'state': START,
                'status': SUCCESS,
                'record': record,
                'config': json.dumps(test.get_config())
            })

        return record

    def ready(self, record):
        if record in self._records:
            return True
        else:
            return False

    def update_config(self, record, config):
        if record in self._records:
            auto_record(record, INFO, SUCCESS, "update config: {}".format(config))
            self._records[record].set_config(config)
            # update config
            DBAuto(record=record).update({'config': json.dumps(config)})
            return True
        else:
            return False

    def start(self, record):
        if record in self._records:
            self._records[record].start()
        else:
            logger.warning("%s is not in record", record)

    def stop(self, record):
        if record in self._records:
            self._records[record].stop()
            while self._records[record].running:
                pass
            self.on_status(record, WORKING, STOP)
            auto_record(record, INFO, STOP, "user stopped")
        else:
            logger.warning("%s is not running", record)

    def on_status(self, record, state, status):
        response = {'record': record}
        if status == SUCCESS and (state == PREPARING or state == WORKING):
            response['data'] = state
            DBAuto(record=record).update({
                'state': state
            })
        else:
            if record in self._records:
                del self._records[record]
            response['data'] = status
            socketio.emit('finish', {'data': status})
            DBAuto(record=record).update({
                'state': FINISH,
                'status': status
            })
        socketio.emit('my_status', response)
