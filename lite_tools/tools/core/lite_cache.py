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
import copy
import time
from queue import Queue, Empty
from functools import wraps, partial
from asyncio import iscoroutinefunction
from typing import Dict, Any, NoReturn, Callable
from threading import RLock, Lock, current_thread

import redis
import aioredis

from lite_tools.tools.core.ip_info import get_lan
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
#TODO(下面缓存区还需要加一个超时异常结束程序的操作, 而且有点bug 不建议作为主要代码使用 后面有空修复)
"""


BASE_TEMPLATE = {
    "get_count": 0,       # type: int     # 从seed里面拿任务种子数量
    "task_time": 0.0,     # type: float   # 统计任务耗时
    "task_name": set(),   # type: set     # 线程情况统计
    "max_out": 0,         # type: int     # 每个程序的最大重试次数
    "task_done": False,   # type: bool    # 任务是否终止
    "flag": False,        # type: bool    # 队列什么时候结束
}


class CountConfig:
    def __init__(self):
        self.log_jar = {}
        self.lock = RLock()

    def init(self, name):
        """初始化模板数据字段"""
        if name not in self.log_jar:
            self.log_jar[name] = copy.deepcopy(BASE_TEMPLATE)

    def set_max_out(self, name: str, num: int = 0):
        self.init(name)
        with self.lock:
            if num == 0:
                self.log_jar[name]["max_out"] = 0
            else:
                self.log_jar[name]["max_out"] += num

    def get_max_out(self, name: str):
        return self.log_jar[name]["max_out"]

    def set_task_name(self, name: str, item: str = None):
        self.init(name)
        with self.lock:
            if not item:
                self.log_jar[name]["task_name"] = set()
            else:
                self.log_jar[name]["task_name"].add(item)

    def exists_task(self, name: str, item_name: str) -> bool:
        if item_name in self.log_jar[name]['task_name']:
            return True
        return False

    def has_task(self, name: str) -> bool:
        if self.log_jar[name].get('task_name'):
            return True
        return False

    def remove_task(self, name: str, item_name: str):
        with self.lock:
            if item_name in self.log_jar[name]['task_name']:
                self.log_jar[name]['task_name'].remove(item_name)

    def get_task_name(self, name: str):
        try:
            return self.log_jar[name]["task_name"].pop()
        except Exception as err:
            _ = err
            return None

    def set_task_time(self, name: str):
        self.init(name)
        with self.lock:
            self.log_jar[name]["task_time"] = time.time()

    def get_task_time(self, name: str):
        return self.log_jar[name].get("task_time", time.time())

    def set_count(self, name: str, num: int = 0):
        self.init(name)
        with self.lock:
            if num == 0:
                self.log_jar[name]["get_count"] = 0
            else:
                self.log_jar[name]["get_count"] += num

    def get_count(self, name: str):
        return self.log_jar[name].get("get_count", 0)

    def set_task_done(self, name: str, flag: bool = False):
        self.init(name)
        with self.lock:
            self.log_jar[name]["task_done"] = flag

    def get_task_done(self, name: str) -> bool:
        return self.log_jar[name].get("task_done", False)

    def set_flag(self, name: str, flag: bool = False):
        self.init(name)
        with self.lock:
            self.log_jar[name]["flag"] = flag

    def get_flag(self, name: str) -> bool:
        return self.log_jar[name]["flag"]


class Buffer(metaclass=Singleton):
    max_cache: int = 1000                # 最大的缓存队列大小 有些时候可以设置小一点 这样子不会一次性拿掉太多任务
    __queues: Dict[str, Queue] = {}       # 创建任务的时候初始化这个 取任务要是没有直接会报错..
    _lock: Lock = Lock()
    count_config = CountConfig()

    @classmethod
    def reset(cls, name: str = "default"):
        """
        重置统计数据的
        """
        cls.__init__queue__(name, rs=True)

    @classmethod
    def size(cls, name: str = "default") -> int:
        """
        队列里面剩余的量
        """
        return cls.__queues[name].qsize()

    @classmethod
    def count(cls, name: str = "default") -> int:
        """
        每次调用seed后会+1 这里返回次数
        """
        return cls.count_config.get_count(name)

    @classmethod
    def sow(cls, job, name: str = "default") -> NoReturn:
        """
        这里是种种子 相当于 queue.put(xxx) 避免阻塞 采取丢失失败任务的方案
        """
        if not cls.__queues[name].full():
            cls.__queues[name].put(job)
        else:
            logger.warning(f"因为队列已经满了，避免程序阻塞，这个任务采用了丢弃方案: {job}")

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
                cls.count_config.set_count(name, 1)
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
            cls.count_config.set_flag(name, True)
            cls.count_config.set_task_time(name)
            
            for job in func(*args, **kwargs):
                cls.__queues[name].put(job)

            cls.count_config.set_flag(name, False)  # 标记这个任务线程已经退出

        return wrapper

    @classmethod
    def _log_detail(cls, name: str):
        with cls._lock:
            if not cls.count_config.has_task(name) and not cls.count_config.get_task_done(name):
                cost_time = round(time.time() - cls.count_config.get_task_time(name), 3)
                logger.debug(
                    f"[{name}] 队列任务种子消耗完毕,worker结束.总耗时:{cost_time}s; "
                    f"总调用任务种子:"
                    f"{cls.count(name)}条; 效率:{round(cls.count(name) / (cost_time or 1), 3)} seed/s"
                )
                cls.count_config.set_task_done(name, True)

    @classmethod
    def worker(cls, func=None, *, name: str = "default"):
        if func is None:
            return partial(cls.worker, name=name)

        cls.__init__queue__(name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            cls.count_config.set_task_name(name, current_thread().name)
            while True:
                if not cls.count_config.get_flag(name) and cls.__queues[name].empty():
                    if cls.count_config.exists_task(name, current_thread().name):
                        cls.count_config.remove_task(name, current_thread().name)
                        continue
                    break
                if cls.__queues[name].empty():
                    time.sleep(.5)
                    if not cls.count_config.get_flag(name):
                        cls.count_config.set_max_out(name, 1)
                    if cls.count_config.get_max_out(name) >= 300:
                        break
                    continue

                try:
                    func(*args, **kwargs)
                    if cls.count_config.get_max_out(name) > 0:
                        cls.count_config.set_max_out(name, 0)
                except QueueEmptyNotion:   # 如果队列持续为空 # 避免卡死
                    if not cls.count_config.get_flag(name):
                        cls.count_config.set_max_out(name, 1)
                        time.sleep(1)
                    if cls.count_config.get_max_out(name) >= 300:
                        break
            cls._log_detail(name)

        return wrapper

    @classmethod
    def __init__queue__(cls, name, rs: bool = False):
        """
        下面尽可能 划细一点 提升效率 不用每次都要进来加锁判断一下
        """
        cls.count_config.init(name)
        if name not in cls.__queues:
            with cls._lock:
                if name not in cls.__queues:
                    cls.__queues[name] = Queue(cls.max_cache)

        if name not in cls.count_config.log_jar or rs is True:
            cls.count_config.set_count(name, 0)
            cls.count_config.set_task_time(name)
            cls.count_config.set_task_name(name)
            cls.count_config.set_max_out(name, 0)
            cls.count_config.set_task_done(name, False)
            cls.count_config.set_flag(name, True)


class LiteCacher:
    def __init__(
            self,
            sync_redis: redis.Redis = None, async_redis: aioredis.Redis = None,
            save_ip: bool = False,
    ):
        """
        sync_redis 和 async_redis 二选一
        如果传入了redis 就用redis 否则用内存
        """
        self._ip = get_lan() if save_ip else ""   # 存一下内网地址
        if sync_redis:
            self._mid = sync_redis    # 同步redis
            self._mode = 1
        elif async_redis:
            self._mid = async_redis   # 异步redis
            self._mode = 2
        else:
            self._mid = {}            # 内存
            self._mode = 0

    """
    task_item = {
        "type": 0-取 1-存
        "key": "存redis或者内存的时候的key",
        "value": 任意类型：如果是redis存储的话 整个数据存json 这样子取出来读取就好了 存的时候 如果是None 则忽略
        "ttl": "配置的有效期，也用作内存存取的时候的判断依据"
    }
    """

    def _mode_0(self, task_item: dict) -> Any:
        """
        内存 设置
        """
        cache_key = task_item['key']
        if task_item['type'] == 1:   # 1-存
            self._mid[cache_key] = (task_item["value"], time.perf_counter())
        else:   # 0-取
            if cache_key in self._mid:
                result, perf_counter = self._mid[cache_key]
                if time.perf_counter() - perf_counter < task_item['ttl']:
                    return result
                else:
                    del self._mid[cache_key]   # 移除过期的key

    def cached(self, redis_key: str, ttl: int = 60, func_name: bool = True, value_field: list = None):
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                pass

            def wrapper(*args, **kwargs) -> Any:
                pass

            return async_wrapper if iscoroutinefunction(func) else wrapper
