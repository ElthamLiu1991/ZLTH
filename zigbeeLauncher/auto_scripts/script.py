import abc
import asyncio
import time
from functools import wraps

import httpx
import rapidjson as json

from zigbeeLauncher.auto_scripts import auto_record
from zigbeeLauncher.dongle import Tasks
from zigbeeLauncher.logging import autoLogger as logger


class Basic_script():
    def __init__(self):
        self.running = False
        self.record = None
        self.config = None
        self.script = None
        self.state = None
        self.result = None
        self.setting = None
        self.ready = False
        self.error = None

    def is_running(self):
        return self.running

    def get_state(self):
        return self.state

    def get_config(self):
        return self.config

    def get_record(self):
        return self.record

    def get_script(self):
        return self.script

    @abc.abstractmethod
    def set_config(self, config):
        """
        update config json
        :param config:
        :return:
        """
        pass


class Script(Basic_script):
    def __init__(self, script, path, status_callback):
        Basic_script.__init__(self)
        self.script = script
        self.update_callback = status_callback
        with open(path, encoding='utf-8') as f:
            self.record = self.script + '-' + time.strftime("%Y-%m-%d_%H-%M-%S") + '.log'
            try:
                self.config = f.read()
                self.config = json.loads(self.config)
            except json.JSONDecodeError as e:
                logger.exception(f'invalid JSON format, {self.config}')
                self.error = f'config is not valid JSON format'
            else:
                self.load_config()

    @abc.abstractmethod
    def update_result(self, result, descriptor):
        """
        store failed record
        :param result: result
        :param descriptor: record
        :return:
        """
        pass

    @abc.abstractmethod
    def load_config(self):
        """
        load script config
        :return:
        """
        pass

    @abc.abstractmethod
    def start(self):
        """
        start script
        :return:
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        stop current script
        :return:
        """
        pass

    @abc.abstractmethod
    def preparing(self):
        """
        prepare job before start script
        :return:
        """
        pass

    @abc.abstractmethod
    def working(self):
        """
        working job
        :return:
        """
        pass

    def set_config(self, config):
        self.config = config
        self.load_config()

    def update(self, state, result):
        self.state = state
        self.result = result
        if self.update_callback:
            self.update_callback(self.record, self.state, result)


    def log(self, status, message):
        auto_record(self.record, self.state, status, message)
        pass

    def is_ready(self):
        return self.ready

    def get_error(self):
        return self.error

    def set_record(self, record):
        self.record = record

    def get_state(self):
        return self.state


class Http:
    def __init__(self, url=None, method=None, path=None, params=None, headers=None, body=None):
        self.url = url
        self.method = method
        self.path = path
        self.params = params
        self.headers = headers
        self.body = body
        self.response = None

    async def send(self):
        async with httpx.AsyncClient() as client:
            logger.info(f"request:{self.url}{self.path}")
            if self.method == 'GET':
                r = await client.get(self.url + self.path,
                                     params=self.params,
                                     headers=self.headers,
                                     )
            elif self.method == 'POST':
                r = await client.post(self.url + self.path,
                                      params=self.params,
                                      headers=self.headers,
                                      data=json.dumps(self.body))
            elif self.method == 'PUT':
                r = await client.put(self.url + self.path,
                                     params=self.params,
                                     headers=self.headers,
                                     data=json.dumps(self.body))
            elif self.method == 'DELETE':
                r = await client.delete(self.url + self.path,
                                        params=self.params,
                                        headers=self.headers)
            if r.status_code != 200:
                logger.info(f"HTTP response failed: {r.json()}")
                raise Exception(f"{r.status_code}: {r.json()}")
            else:
                logger.info(f"HTTP response success: {r.json()}")
                self.response = r.json()


def wait_and_retry(timeout=5, retry=3):

    async def _wait():
        await asyncio.sleep(timeout)

    def wait_handle(func):
        @wraps(func)
        def retry_handle(*args, **kwargs):
            # do something
            for i in range(0, retry):
                if not func(*args, **kwargs):
                    task = Tasks()
                    task.add(_wait()).result()
                    # asyncio.run(_wait())
                else:
                    return True
            return False
        return retry_handle
    return wait_handle
