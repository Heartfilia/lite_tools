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
from typing import Dict, Any, NoReturn
from functools import wraps, partial
from queue import Queue, Empty
from asyncio import iscoroutinefunction
from threading import RLock, current_thread

from lite_tools.logs import logger
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
    _lock: RLock = RLock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

"""
TODO:下面缓存区还需要加一个超时异常结束程序的操作.
"""


class Buffer(metaclass=Singleton):
    max_cache: int = 1000                # 最大的缓存队列大小 有些时候可以设置小一点 这样子不会一次性拿掉太多任务
    __task_flag: Dict[str, bool] = {}     # 队列什么时候结束由这里和队列长度一起说了算
    __queues: Dict[str, Queue] = {}       # 创建任务的时候初始化这个 取任务要是没有直接会报错..
    __task_count: Dict[str, set] = {}     # 线程情况统计
    __task_time: Dict[str, float] = {}    # 统计任务耗时
    __async_out: bool = True              # 异步日志
    _get_count: Dict[str, int] = {}       # 从seed中拿的种子数量
    _lock: RLock = RLock()
    _task_done: bool = False              # 任务是否终止

    @classmethod
    def reset(cls, name: str = "default"):
        """
        重置统计数据的
        """
        cls.__init__queue__(name, rs=True)

    @classmethod
    def size(cls, name: str = "default") -> int:
        return cls.__queues[name].qsize()

    @classmethod
    def count(cls, name: str = "default") -> int:
        """
        每次调用seed后会+1 这里返回次数
        """
        return cls._get_count[name]

    @classmethod
    def sow(cls, job, name: str = "default") -> NoReturn:
        """
        这里是种种子 相当于 queue.put(xxx)
        """
        cls.__queues[name].put(job)

    @classmethod
    def seed(cls, name: str = "default") -> Any:
        """
        这里是拿种子 相当于 queue.get()
        """
        if not cls.__queues[name].empty():
            try:
                return cls.__queues[name].get(timeout=3)
            except Empty:
                raise QueueEmptyNotion
            finally:
                with cls._lock:
                    cls._get_count[name] += 1
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

            cls.__task_time[name] = time.time()
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
                        with cls._lock:
                            if not cls.__task_count[name] and not cls._task_done:
                                cost_time = round(time.time() - cls.__task_time[name], 3)
                                logger.debug(
                                    f"[{name}] 队列任务种子消耗完毕,worker结束.总耗时:{cost_time}s; "
                                    f"总调用任务种子:{cls.count(name)}条; 效率:{round(cls.count(name)/cost_time, 3)} seed/s"
                                )
                                cls._task_done = True
                    break
                if cls.__queues[name].empty():
                    time.sleep(.5)
                    continue

                try:
                    func(*args, **kwargs)
                except QueueEmptyNotion:
                    pass

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with cls._lock:
                cls.__task_count[name].add("AsyncTask")
            while True:
                if not cls.__task_flag.get(name, False) and cls.__queues[name].empty():
                    with cls._lock:
                        if cls.__async_out and not cls._task_done:
                            logger.debug(
                                f"[{name}] 队列任务种子消耗完毕,worker结束.耗时:{time.time() - cls.__task_time[name]:.3f} s"
                            )
                            cls._task_done = True

                        if cls.__task_count[name]:
                            cls.__task_count[name].pop()
                            cls.__async_out = False
                    break
                if cls.__queues[name].empty():
                    await asyncio.sleep(.5)
                    continue

                try:
                    await func(*args, **kwargs)
                except QueueEmptyNotion:
                    pass

        return async_wrapper if iscoroutinefunction(func) else wrapper

    @classmethod
    def __init__queue__(cls, name, rs: bool = False):
        """
        下面尽可能的划细一点 提升效率 不用每次都要进来加锁判断一下
        """
        if name not in cls.__queues:
            with cls._lock:
                if name not in cls.__queues:
                    cls.__queues[name] = Queue(cls.max_cache)

        if name not in cls.__task_count or rs is True:
            with cls._lock:
                if name not in cls.__task_count or rs is True:
                    cls.__task_count[name] = set()

        if name not in cls.__task_flag:
            with cls._lock:
                if name not in cls.__task_flag:
                    cls.__task_flag[name] = True

        if name not in cls.__task_time or rs is True:
            with cls._lock:
                if name not in cls.__task_time or rs is True:
                    cls.__task_time[name] = time.time()

        if name not in cls._get_count or rs is True:
            with cls._lock:
                if name not in cls._get_count or rs is True:
                    cls._get_count[name] = 0
