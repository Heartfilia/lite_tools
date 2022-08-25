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
"""
import time
from threading import Lock, Thread, current_thread
from multiprocessing import Queue
from functools import wraps, partial

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
    __task_flag = {}          # 队列什么时候结束由这里和队列长度一起说了算
    __queues = {}             # 队列需要放个名字上 用字典取值 因为我要保证同一个buffer
    __task_count = set()      # 线程情况统计
    _lock: Lock = Lock()

    @classmethod
    def seed(cls, name: str = "default"):
        if cls.__queues.get(name) and not cls.__queues.get(name).empty():
            try:
                return cls.__queues.get(name).get()
            except QueueEmptyNotion:
                raise QueueEmptyNotion
        else:
            raise QueueEmptyNotion

    @classmethod
    def task(cls, func, name: str = "default"):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里是一个独立的线程运行
            cls.__task_flag[name] = True
            for job in func(*args, **kwargs):
                cls.__queues[name].put(job)
            cls.__task_flag[name] = False

        if func is None:
            return partial(cls.task, name=name)

        if name not in cls.__queues:
            cls.__queues[name] = Queue(cls.queue_long)

        return wrapper

    @classmethod
    def worker(cls, func, name: str = "default"):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with cls._lock:
                if current_thread().name not in cls.__task_count:
                    cls.__task_count.add(current_thread().name)
            while True:
                logger.debug(f"{current_thread().name} // {cls.__task_flag.get(name)} // {cls.__queues[name].empty()}")
                if not cls.__task_flag.get(name) and cls.__queues[name].empty():
                    with cls._lock:
                        if current_thread().name in cls.__task_count:
                            cls.__task_count.remove(current_thread().name)
                        if not cls.__task_count:
                            logger.debug(f"[{name}] 队列-> 任务种子消耗完毕,worker结束.")
                    logger.warning(
                        f"{current_thread().name} // {cls.__task_flag.get(name)} // {cls.__queues[name].empty()}")
                    break
                logger.info(f"{current_thread().name} // {cls.__task_flag.get(name)} // {cls.__queues[name].empty()}")
                if cls.__queues[name].empty():
                    time.sleep(1)
                    continue

                logger.success(f"{current_thread().name} // {cls.__task_flag.get(name)} // {cls.__queues[name].empty()}")
                try:
                    func(*args, **kwargs)
                except QueueEmptyNotion:
                    logger.error("这里错了吗")
                    pass

        if func is None:
            return partial(cls.task, name=name)
        if name not in cls.__queues:
            cls.__queues[name] = Queue(cls.queue_long)

        return wrapper


@Buffer.task
def test1():
    for t in range(12):
        yield t


@Buffer.worker
def test2():
    task = Buffer.seed()
    logger.info(task)


if __name__ == "__main__":
    Thread(target=test1).start()
    t_list = [Thread(target=test2) for _ in range(5)]
    for t in t_list:
        # t.setDaemon(True)
        t.start()
    # for t in t_list:
    #     t.join()
    print('xxxxxxxxxx')

