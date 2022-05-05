import asyncio
import time
from threading import Thread

from zigbeeLauncher.mqtt import get_value

commands = {}
loop = asyncio.new_event_loop()


class Command:
    global commands

    def __init__(self, dongle, request, response=None, timeout=None, done=None):
        self.dongle = dongle
        self.device = dongle.name
        self.request = request
        self.response = response
        self.timeout = timeout
        self.done = done
        self.seq = 0

    async def send_command(self, timestamp, uuid, payload, report):
        self.timestamp = timestamp
        self.uuid = uuid
        self.payload = payload
        self.report = report
        self.seq, data = self.request(payload)
        commands[(self.seq, self.device)] = self
        self.dongle.data_write(data)
        try:
            if self.timeout:
                await asyncio.wait_for(self.wait_response(), timeout=5.0)
            else:
                del commands[(self.seq, self.device)]
        except asyncio.TimeoutError:
            del commands[(self.seq, self.device)]
            self.timeout(self.device, timestamp, uuid)
            return
        if self.done:
            self.done()

    async def wait_response(self):
        while (self.seq, self.device) in commands.keys():
            await asyncio.sleep(0.001)

    def get_response(self, user_data):
        del commands[(self.seq, self.device)]
        if user_data and self.response:
            if self.timestamp and self.uuid:
                user_data["timestamp"] = self.timestamp
                user_data["uuid"] = self.uuid
            self.response(self.device, user_data)
        else:
            if self.report and get_value("dongle_update_callback"):
                get_value("dongle_update_callback")(self.dongle.name, self.payload)


def send_command(command, timestamp=None, uuid=None, payload=None, report=False):
    asyncio.run_coroutine_threadsafe(command.send_command(timestamp, uuid, payload, report), loop)


def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()


def commands_init():
    run_loop_thread = Thread(target=start_loop)
    run_loop_thread.start()
