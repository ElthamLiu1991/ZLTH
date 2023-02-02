import datetime
import importlib
import rapidjson as json
import os
import threading
import time
from enum import Enum

from rapidjson import JSONDecodeError

from zigbeeLauncher.database.interface import DBAuto
from zigbeeLauncher.logging import autoLogger as logger

from flask_socketio import emit, join_room, close_room

from zigbeeLauncher import socketio, base_dir


class State:
    READY = 'READY'
    START = 'START'
    PREPARING = 'PREPARING'
    WORKING = 'WORKING'
    FINISH = 'FINISH'


class Status:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class Result:
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    STOP = 'STOP'


class Error(Enum):
    NO_ERROR = 0
    NOT_FOUND = 1
    INVALID_CONFIG = 2
    NOT_RUNNING = 3
    RUNNING = 4


class ScriptName:
    CAPACITY = 'capacity'
    CAPACITY_LOCAL = 'capacity_local'
    STABILITY = 'stability'
    COMPOSE = 'compose'

# @socketio.event
# def connect():
#     script = AutoTesting().get_script()
#     emit('my_script', {'data': script})
#     if script:
#         with open(os.path.join(base_dir, 'scripts/{}.json'.format(script)), encoding='utf-8') as f:
#             config = f.read()
#             emit('my_config', {'data': config})
#
#         emit('my_state', {'data': 'ready'})


@socketio.on('join')
def join(message):
    record = message['record']
    logger.info(f'join room:{record}')
    join_room(record)

    records = DBAuto(record=record).retrieve()
    if records:
        state = records[0]['state']
        result = records[0]['result']
        config = records[0]['config']

        test = AutoTesting().get_record(record)
        try:
            emit('my_config', {'data': json.dumps(json.loads(config), indent=4)}, room=record)
        except JSONDecodeError as e:
            emit('my_config', {'data': config}, room=record)
        if not test:
            logger.info(f"{record} is history record")
            if state != State.FINISH:
                emit('my_state', {'state': State.FINISH, 'result': Result.STOP}, room=record)
            else:
                emit('my_state', {'state': state, 'result': result}, room=record)

            try:
                with open(os.path.join(base_dir, 'records/' + record)) as f:
                    emit('my_record', {'data': f.read()}, room=record)
            except FileNotFoundError as e:
                logger.warning(f"{record} has not log")
                emit('my_record', {'data': "no log"}, room=record)
        else:
            emit('my_state', {'state': state, 'result': result}, room=record)
            if state != State.READY:
                with open(os.path.join(base_dir, 'records/' + record)) as f:
                    emit('my_record', {'data': f.read()}, room=record)
    else:
        # not in database
        emit('my_state', {'state': State.FINISH, 'result': Result.STOP}, room=record)


@socketio.on('close')
def close(message):
    close_room(message['record'])


@socketio.event
def update_request(message):
    logger.info(f"update config {message['data']} for script:{message['record']}")
    config = json.loads(message['data'])
    record = message['record']

    AutoTesting().update_config(record, config)


@socketio.event
def start_request(message):
    record = message['record']
    logger.info(f"start script:{record}")
    # emit('my_state', {'data': 'running'}, room=record)
    AutoTesting().start(record)


@socketio.event
def stop_request(message):
    record = message['record']
    logger.info(f"stop script:{record}")
    # emit('my_state', {'data': 'stopping'}, room=record)
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
        data = f'{timestamp}:{state}:{status}:{message}\n'
        print("log record:", record)
        logger.info(data)
        if state == State.FINISH:
            data = message
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
    _script_instances = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def set_script(self, script):
        return self.run(script)

    def run(self, script):
        testing = importlib.import_module('zigbeeLauncher.auto_scripts.' + script)
        test = testing.Testing(self.on_status)
        record = test.get_record()
        config = test.get_config()
        if not test.is_ready():
            logger.error(f'{record} config invalid: {config}')
            auto_record(record, State.READY, Status.ERROR, test.get_error())
        # add to database
        DBAuto(record=record).add({
            'script': script,
            'state': State.READY,
            'result': Result.SUCCESS,
            'record': record,
            'config': config if isinstance(config, str) else json.dumps(config, indent=4)
        })
        self._script_instances[record] = test
        return record

    def update_config(self, record, config):
        test = self.get_record(record)
        if test:
            if test.is_running():
                logger.error(f'{record} is running, please wait it finish')
                auto_record(record, State.READY, Status.ERROR, f'{record} is running, please wait it finish')
                return Error.RUNNING
            else:
                test.set_config(config)
                if not test.is_ready():
                    logger.error(f'invalid config')
                    auto_record(record, State.READY, Status.ERROR, test.get_error())
                    return Error.INVALID_CONFIG
                else:
                    with open(os.path.join(base_dir, 'scripts/' + test.get_script() + '.json'), 'w',
                              encoding='utf-8') as f:
                        f.write(json.dumps(config, indent=4))
                    auto_record(record, State.READY, Status.INFO, f"update config: {config}")
                    DBAuto(record=record).update({'config': json.dumps(config, indent=4)})
                    return Error.NO_ERROR
        else:
            logger.error(f'{record} not found')
            return Error.NOT_FOUND

    def start(self, record):
        # if already has script running, don't start
        test = self.get_record(record)
        if test:
            if test.is_running():
                logger.error(f'{record} is running, please wait it finish')
                auto_record(record, State.START, Status.ERROR, f'{record} is running, please wait it finish')
                return Error.RUNNING
            elif not test.is_ready():
                logger.error(f'{record} is not ready, please update config')
                auto_record(record, State.START, Status.ERROR, test.get_error())
                return Error.INVALID_CONFIG
            else:
                for k, v in self._script_instances.items():
                    if v.is_running():
                        logger.error(f"{k} is running, please wait it finish")
                        auto_record(record, State.START, Status.ERROR, f'{k} is running, please wait it finish')
                        return Error.RUNNING
                test.start()
                return Error.NO_ERROR
        else:
            logger.error(f'{record} not found')
            return Error.NOT_FOUND

    def stop(self, record):
        test = self.get_record(record)
        if test:
            if not test.is_running():
                logger.error(f'{record} is not running')
                auto_record(record, State.READY, Status.ERROR,f'{record} is not running')
                return Error.NOT_RUNNING
            else:
                test.stop()
                auto_record(record, State.FINISH, Status.INFO, "user stopped")
                self.on_status(record, State.FINISH, Result.STOP)
                return Error.NO_ERROR
        else:
            logger.error(f'{record} not found')
            return Error.NOT_FOUND

    def on_status(self, record, state, result=Result.SUCCESS):
        # if script is compose, bypass other script FINISH state update
        if ScriptName.COMPOSE in record and state == State.FINISH and result == Result.SUCCESS:
            if record in self._script_instances and self._script_instances[record].get_state() != State.FINISH:
                return
        DBAuto(record=record).update({
            'state': state,
            'result': result
        })

        if state == State.FINISH:
            # script finish
            if record in self._script_instances:
                del self._script_instances[record]
            socketio.emit('my_state', {'state': state, 'result': result}, room=record)
        else:
            socketio.emit('my_state', {'state': state, 'result': result}, room=record)

    def get_record(self, record):
        if record in self._script_instances:
            return self._script_instances[record]
        return None
