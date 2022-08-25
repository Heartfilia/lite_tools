# -*- coding: utf-8 -*-
# @Author  : Lodge
"""
      ┏┛ ┻━━━━━┛ ┻┓
      ┃　　　　　　 ┃
      ┃　　　━　　　┃
      ┃　┳┛　  ┗┳　┃
      ┃　　　　　　 ┃
      ┃　　　┻　　　┃
      ┃　　　　　　 ┃
      ┗━┓　　　┏━━━┛
        ┃　　　┃   神兽保佑
        ┃　　　┃   代码无BUG！
        ┃　　　┗━━━━━━━━━┓
        ┃　　　　　　　    ┣┓
        ┃　　　　         ┏┛
        ┗━┓ ┓ ┏━━━┳ ┓ ┏━┛
          ┃ ┫ ┫   ┃ ┫ ┫
          ┗━┻━┛   ┗━┻━┛
这里是搞一个缓存中间件 通过装饰器的方案 让多线程或者多进程里面的消费者或者生产者走同一个管道

>> 第一版先只兼容同步的函数   **异步没有兼容** <<
"""
import time
import asyncio
from queue import Empty
from typing import Union
from functools import wraps
from multiprocessing import Queue
from threading import Lock, current_thread

from lite_tools.tools.utils.logs import logger
from lite_tools.exceptions.CacheExceptions import QueueEmptyNotion


class Singleton(type):
    """
    单例模式:需要单例的操作只需要创建对象的时候使用
    from lite_tools import Singleton

    class Xxx(metaclass=Singleton):
        pass

    # 上面的Xxx就是单例模式了
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


"""
下面是还没有搞完的缓存区
"""


class Buffer(metaclass=Singleton):
    queue_long: int = 10000   # 设置队列的长度 默认 10000   如果要改 --> Buffer.queue_long = 100
    __task_flag = True        # 队列什么时候结束由这里和队列长度一起说了算
    __queues: Union[Queue, asyncio.Queue] = None           # 队列需要放个名字上 用字典取值 因为我要保证同一个buffer
    __task_count = set()      # 线程情况统计
    _lock: Lock = Lock()

    @classmethod
    def seed(cls):
        with cls._lock:
            if not cls.__queues.empty():
                try:
                    return cls.__queues.get(timeout=3)
                except Empty:
                    raise QueueEmptyNotion
            else:
                raise QueueEmptyNotion


    @classmethod
    def task(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里是一个独立的线程运行
            cls.__task_flag = True
            for job in func(*args, **kwargs):
                cls.__queues.put(job)
            cls.__task_flag = False

        cls.__init__queue__()
        return wrapper

    @classmethod
    def worker(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with cls._lock:
                if current_thread().name not in cls.__task_count:
                    cls.__task_count.add(current_thread().name)
            while True:
                if not cls.__task_flag and cls.__queues.empty():
                    with cls._lock:
                        if current_thread().name in cls.__task_count:
                            cls.__task_count.remove(current_thread().name)
                        if not cls.__task_count:
                            logger.debug(f"队列-> 任务种子消耗完毕,worker结束.")
                    break
                if cls.__queues.empty():
                    time.sleep(1)
                    continue

                try:
                    func(*args, **kwargs)
                except QueueEmptyNotion:
                    pass

        cls.__init__queue__()
        return wrapper

    @classmethod
    def __init__queue__(cls):
        with cls._lock:
            if not cls.__queues:
                cls.__queues = Queue(cls.queue_long)
