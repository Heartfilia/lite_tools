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
from typing import Dict, Any
from queue import Empty
from functools import wraps, partial
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
    __task_flag: Dict[str, bool] = {}     # 队列什么时候结束由这里和队列长度一起说了算
    __queues: Dict[str, Queue] = {}       # 创建任务的时候初始化这个 取任务要是没有直接会报错..
    __task_count: Dict[str, set] = {}     # 线程情况统计
    _lock: Lock = Lock()

    @classmethod
    def seed(cls, name: str = "default") -> Any:
        if not cls.__queues[name].empty():
            try:
                return cls.__queues[name].get(timeout=3)
            except Empty:
                raise QueueEmptyNotion
        else:
            raise QueueEmptyNotion

    @classmethod
    def task(cls, func=None, *, name: str = "default"):
        if func is None:
            return partial(cls.task, name=name)
        cls.__init__queue__(name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里是一个独立的线程运行
            if name not in cls.__task_count:
                cls.__task_flag[name] = True
            for job in func(*args, **kwargs):
                cls.__queues[name].put(job)
            cls.__task_flag[name] = False

        return wrapper

    @classmethod
    def worker(cls, func=None, *, name: str = "default"):
        if func is None:
            return partial(cls.worker, name=name)

        cls.__init__queue__(name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            with cls._lock:
                if current_thread().name not in cls.__task_count[name]:
                    cls.__task_count[name].add(current_thread().name)
            while True:
                if not cls.__task_flag.get(name, False) and cls.__queues[name].empty():
                    with cls._lock:
                        if current_thread().name in cls.__task_count[name]:
                            cls.__task_count[name].remove(current_thread().name)
                        if not cls.__task_count[name]:
                            logger.debug(f"队列 {name} -> 任务种子消耗完毕,worker结束.")
                    break
                if cls.__queues[name].empty():
                    time.sleep(1)
                    continue

                try:
                    func(*args, **kwargs)
                except QueueEmptyNotion:
                    pass

        return wrapper

    @classmethod
    def __init__queue__(cls, name):
        cls._lock.acquire()
        if name not in cls.__queues:
            cls.__queues[name] = Queue(10000)
        if name not in cls.__task_count:
            cls.__task_count[name] = set()
        if name not in cls.__task_flag:
            cls.__task_flag[name] = True
        cls._lock.release()
