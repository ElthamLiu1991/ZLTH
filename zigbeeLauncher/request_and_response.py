import asyncio
import time
from threading import Thread
from zigbeeLauncher.logging import flaskLogger as logger
message_queue = {}


async def _check_response(x, y, timeout):
    while True:
        if x in message_queue:
            result = message_queue[x]
            if result != {}:
                del message_queue[x]
                return result
        if time.time() - y/1000.0 > timeout:
            logger.warning("request timeout:%s", x)
            del message_queue[x]
            return {}
        await asyncio.sleep(0.01)


async def _insert_request(x, y, timeout):
    if x not in message_queue:
        message_queue[x] = {}
    result = await _check_response(x, y, timeout)
    # 返回result
    return result


def _start_loop(loop):
    #  运行事件循环， loop以参数的形式传递进来运行
    asyncio.set_event_loop(loop)
    loop.run_forever()


def init():
    global thread_loop
    thread_loop = asyncio.new_event_loop()  # 获取一个事件循环
    run_loop_thread = Thread(target=_start_loop, args=(thread_loop,))  # 将次事件循环运行在一个线程中，防止阻塞当前主线程
    run_loop_thread.start()  # 运行线程，同时协程事件循环也会运


def wait_response(timestamp, uid, timeout):
    return asyncio.run_coroutine_threadsafe(_insert_request(uid, timestamp, timeout), thread_loop)


def add_response(response):
    try:
        uuid = response['data']['uuid']
        data = response['data']
        if uuid in message_queue:
            message_queue[uuid] = data
    except Exception as e:
        logger.warning("response error:%s", response)