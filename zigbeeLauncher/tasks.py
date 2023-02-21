import asyncio
import threading


class Tasks(threading.Thread):
    _instance = None
    _flag = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance=super().__new__(cls)
        return cls._instance

    def __init__(self):
        threading.Thread.__init__(self)
        if not self._flag:
            self._flag = True
            print("task loop init")
            self.loop = asyncio.new_event_loop()  # 获取一个事件循环
            self.start()

    def run(self) -> None:
        print("run task loop")
        _run = True
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def add(self, task):
        return asyncio.run_coroutine_threadsafe(
            task, self.loop
        )