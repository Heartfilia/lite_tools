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
import json
import asyncio
import inspect
import threading
import hashlib
import math
import uuid
import weakref
from datetime import date, datetime, time as datetime_time, timedelta
from decimal import Decimal
from queue import Queue, Empty
from functools import wraps, partial
from asyncio import iscoroutinefunction
from typing import Dict, Any, NoReturn, Callable
from threading import RLock, Lock, current_thread

import redis

from lite_tools.logs import logger
from lite_tools.tools.core.ip_info import get_lan
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
    "producer_count": 0,  # type: int     # 当前生产者数量
}


class CountConfig:
    def __init__(self):
        self.log_jar = {}
        self.lock = RLock()

    def init(self, name):
        """初始化模板数据字段"""
        with self.lock:
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
            self.log_jar[name]["producer_count"] = 1 if flag else 0

    def get_flag(self, name: str) -> bool:
        return self.log_jar[name].get("producer_count", 0) > 0

    def start_producer(self, name: str):
        self.init(name)
        with self.lock:
            self.log_jar[name]["producer_count"] += 1
            self.log_jar[name]["flag"] = True

    def finish_producer(self, name: str):
        self.init(name)
        with self.lock:
            left = max(0, self.log_jar[name].get("producer_count", 0) - 1)
            self.log_jar[name]["producer_count"] = left
            self.log_jar[name]["flag"] = left > 0

    def get_producer_count(self, name: str) -> int:
        self.init(name)
        return self.log_jar[name].get("producer_count", 0)


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
        cls.__init__queue__(name)
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
        cls.__init__queue__(name)
        if not cls.__queues[name].full():
            cls.__queues[name].put(job)
        else:
            logger.warning(f"因为队列已经满了，避免程序阻塞，这个任务采用了丢弃方案: {job}")

    @classmethod
    def seed(cls, name: str = "default") -> Any:
        """
        这里是拿种子 相当于 queue.get()
        """
        cls.__init__queue__(name)
        try:
            result = cls.__queues[name].get(timeout=3)
        except Empty:
            raise QueueEmptyNotion
        cls.count_config.set_count(name, 1)
        return result

    @classmethod
    def task(cls, func=None, *, name: str = "default"):
        if func is None:
            return partial(cls.task, name=name)
        cls.__init__queue__(name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里是一个独立的线程运行
            cls.__prepare_task_run(name)
            cls.count_config.start_producer(name)
            try:
                for job in func(*args, **kwargs):
                    cls.sow(job, name=name)
            finally:
                cls.count_config.finish_producer(name)  # 标记这个任务线程已经退出

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
            empty_rounds = 0
            while True:
                if not cls.count_config.get_flag(name) and cls.__queues[name].empty():
                    if cls.count_config.exists_task(name, current_thread().name):
                        cls.count_config.remove_task(name, current_thread().name)
                        continue
                    break
                if cls.__queues[name].empty():
                    time.sleep(.1)
                    continue

                try:
                    func(*args, **kwargs)
                    empty_rounds = 0
                except QueueEmptyNotion:   # 如果队列持续为空 # 避免卡死
                    if not cls.count_config.get_flag(name):
                        empty_rounds += 1
                        time.sleep(.1)
                        if empty_rounds >= 5:
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

        if rs is True:
            with cls._lock:
                cls.__queues[name] = Queue(cls.max_cache)
        if name not in cls.count_config.log_jar or rs is True:
            cls.count_config.set_count(name, 0)
            cls.count_config.set_task_time(name)
            cls.count_config.set_task_name(name)
            cls.count_config.set_max_out(name, 0)
            cls.count_config.set_task_done(name, False)
            cls.count_config.set_flag(name, False)

    @classmethod
    def __prepare_task_run(cls, name: str):
        """
        新一轮生产开始前，只有在当前队列已经空闲时才重置统计信息。
        这样不会打断多个生产者共同写入同一队列的场景。
        """
        cls.__init__queue__(name)
        if cls.count_config.get_producer_count(name) == 0 and cls.__queues[name].empty():
            cls.count_config.set_count(name, 0)
            cls.count_config.set_task_time(name)
            cls.count_config.set_task_done(name, False)
            cls.count_config.set_max_out(name, 0)


class LiteCacher:
    def __init__(
            self,
            sync_redis: redis.Redis = None, async_redis: redis.asyncio.Redis = None,
            save_ip: bool = False, **kwargs
    ):
        """
        sync_redis 和 async_redis 二选一
        如果传入了redis 就用redis 否则用内存
        :param sync_redis    同步的redis对象
        :param async_redis   异步的redis对象
        :param save_ip       是否需要记录当前内网ip
        """
        self._ip = get_lan() if save_ip else ""   # 存一下内网地址
        if sync_redis is not None and async_redis is not None:
            raise ValueError("sync_redis 和 async_redis 只能传入一个")
        self._mid_hash = {}
        self._memory_lock = threading.RLock()
        self._receiver_tokens = {}
        self._receiver_lock = threading.Lock()
        if sync_redis is not None:
            self._mid = sync_redis    # 同步redis
            self._mode = 1
        elif async_redis is not None:   # 同步方法使用独立的内存缓存
            self._mid = async_redis   # 异步redis
            self._mode = 2
        else:
            self._mid_hash = dict()            # 内存
            self._mode = 0
            self._mid = sync_redis

        if self._mode == 2:
            self._lock = asyncio.Lock()
        else:
            self._lock = threading.Lock()

        self.kwargs = kwargs    # encoding

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
        now = time.monotonic()
        stored = None
        if task_item['type'] == 1 and task_item['value'] is not None:
            try:
                stored = copy.deepcopy(task_item['value'])
            except Exception:
                return  # An uncopyable result must not break the wrapped call.
        with self._memory_lock:
            if task_item['type'] == 1:
                if task_item['value'] is None:
                    return
                # Bound memory and prune entries even if they are never read.
                maximum = self.kwargs.get("max_entries", 1024)
                if len(self._mid_hash) >= maximum:
                    for key, (_, expires) in list(self._mid_hash.items()):
                        if expires <= now:
                            self._mid_hash.pop(key, None)
                    if cache_key not in self._mid_hash and len(self._mid_hash) >= maximum:
                        self._mid_hash.pop(next(iter(self._mid_hash)))
                self._mid_hash[cache_key] = (stored, now + task_item['ttl'])
            else:
                entry = self._mid_hash.get(cache_key)
                if entry is not None:
                    result, expires = entry
                    if now < expires:
                        try:
                            return copy.deepcopy(result)
                        except Exception:
                            self._mid_hash.pop(cache_key, None)
                            return None
                    self._mid_hash.pop(cache_key, None)

    def _mode_1(self, task_item: dict) -> Any:
        """
        type self.mid = redis.Redis
        """
        cache_key = task_item['key']
        if task_item['type'] == 1:  # 1-存
            if task_item['value'] is None:
                return
            with self._lock:
                try:
                    save_item = {
                        "time": time.time(),
                        "ip": self._ip,
                        "function": task_item['function'],
                        "value": task_item['value']
                    }
                    self._mid.set(
                        cache_key,
                        json.dumps(save_item, ensure_ascii=False, separators=(",", ":")),
                        ex=task_item["ttl"]
                    )
                except Exception as err:
                    if self.kwargs.get("log", False):
                        logger.error(f"【{err.__traceback__.tb_lineno}】redis- {err}")
        else:
            try:
                cache_item = self._mid.get(cache_key)
                if cache_item:
                    if isinstance(cache_item, bytes):
                        cache_item = cache_item.decode(encoding=self.kwargs.get("encoding", "utf-8"))
                    return json.loads(cache_item)['value']
            except (redis.exceptions.RedisError, ValueError, TypeError, KeyError, UnicodeError):
                return None  # Cache miss on an unavailable/corrupt cache.

    async def _mode_2(self, task_item: dict) -> Any:
        """
        type self.mid = redis.asyncio.Redis
        """
        cache_key = task_item['key']
        if task_item['type'] == 1:  # 1-存
            # 这里有一次碰到了出来的结果是异步函数，现在没有碰到，不知道为啥
            await_value = await task_item['value'] if inspect.isawaitable(task_item['value']) else task_item['value']
            if await_value is None:
                return
            async with self._lock:
                try:
                    save_item = {
                        "time": time.time(),
                        "ip": self._ip,
                        "function": task_item['function'],
                        "value": await_value
                    }
                    await self._mid.set(
                        cache_key,
                        json.dumps(save_item, ensure_ascii=False, separators=(",", ":")),
                        ex=task_item["ttl"]
                    )
                except Exception as err:
                    if self.kwargs.get("log", False):
                        logger.error(f"【{err.__traceback__.tb_lineno}】async_redis- {err}")
        else:
            try:
                cache_item = await self._mid.get(cache_key)
                if cache_item:
                    if isinstance(cache_item, bytes):
                        cache_item = cache_item.decode(encoding=self.kwargs.get("encoding", "utf-8"))
                    return json.loads(cache_item)['value']
            except (redis.exceptions.RedisError, ValueError, TypeError, KeyError, UnicodeError):
                return None

    @classmethod
    def _key_value(cls, value):
        """Typed, unambiguous canonical form; never serialize executable code."""
        if value is None:
            return ["none"]
        if type(value) in (bool, int, str):
            return [type(value).__name__, value]
        if type(value) is float:
            if not math.isfinite(value):
                raise TypeError("非有限浮点数不参与缓存")
            return ["float", value.hex()]
        if type(value) is bytes:
            return ["bytes", value.hex()]
        if isinstance(value, (datetime, date, datetime_time)):
            return [type(value).__name__, value.isoformat()]
        if isinstance(value, timedelta):
            return ["timedelta", value.days, value.seconds, value.microseconds]
        if isinstance(value, (Decimal, uuid.UUID)):
            return [type(value).__name__, str(value)]
        if type(value) in (list, tuple):
            return [type(value).__name__, [cls._key_value(item) for item in value]]
        if type(value) in (set, frozenset):
            return [type(value).__name__, sorted((cls._key_value(item) for item in value), key=cls._key_json)]
        if type(value) is dict:
            items = [[cls._key_value(key), cls._key_value(item)] for key, item in value.items()]
            return ["dict", sorted(items, key=lambda pair: cls._key_json(pair[0]))]
        raise TypeError("无法安全生成缓存键的类型: {}".format(type(value).__name__))

    @staticmethod
    def _key_json(value):
        return json.dumps(value, ensure_ascii=True, separators=(",", ":"), allow_nan=False)

    def _receiver_token(self, receiver):
        identity = id(receiver)
        with self._receiver_lock:
            entry = self._receiver_tokens.get(identity)
            if entry is None or entry[0]() is not receiver:
                def discard(reference):
                    with self._receiver_lock:
                        current = self._receiver_tokens.get(identity)
                        if current is not None and current[0] is reference:
                            self._receiver_tokens.pop(identity, None)
                reference = weakref.ref(receiver, discard)
                entry = (reference, uuid.uuid4().hex)
                self._receiver_tokens[identity] = entry
            return entry[1]

    def cal_redis_key_name(
            self, redis_head: str, signature: inspect.Signature = None, main_key: list = None, *args, **kwargs):
        """
        获取名称
        """
        arguments = None
        receiver_token = None
        if signature is not None:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            arguments = dict(bound.arguments)
            names = list(signature.parameters)
            if names and names[0] in ("self", "cls") and names[0] in arguments:
                receiver_token = self._receiver_token(arguments.pop(names[0]))
        if main_key:
            if not isinstance(main_key, list) or not all(isinstance(key, str) for key in main_key):
                raise ValueError("main_key 必须是参数名列表")
            available = dict(kwargs) if arguments is None else dict(arguments)
            if signature is not None:
                for name, parameter in signature.parameters.items():
                    if parameter.kind is inspect.Parameter.VAR_KEYWORD:
                        for key, value in arguments.get(name, {}).items():
                            available.setdefault(key, value)
            missing = set(main_key) - set(available)
            if missing:
                raise ValueError("main_key 指定的参数不存在: {}".format(sorted(missing)))
            payload = {key: available[key] for key in main_key}
        else:
            payload = arguments if arguments is not None else (args, kwargs)
        encoded = self._key_json(["v2", receiver_token, self._key_value(payload)])
        return "{}:v2:{}".format(redis_head, hashlib.sha256(encoded.encode("utf-8")).hexdigest())

    def cached(self, redis_head: str, ttl: int = 60, main_key: list = None):
        """
        redis_head: 存到redis的名称前缀 xxx:
        ttl       : 过期时间
        main_key  : 如果设置了这个 那么key的拼接规则就会变成 从kw里面取值 然后组合判断 如 ["a", "b"] 那么需要提取到 这个方法 a的值和b的值来计算key
        """
        if isinstance(ttl, bool) or not isinstance(ttl, int) or ttl <= 0:
            raise ValueError("ttl 必须是正整数秒")
        if main_key is not None and (not isinstance(main_key, list) or not all(isinstance(key, str) for key in main_key)):
            raise ValueError("main_key 必须是参数名列表")
        maximum = self.kwargs.get("max_entries", 1024)
        if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum < 1:
            raise ValueError("max_entries 必须是正整数")
        def decorator(func: Callable):
            signature = inspect.signature(func)
            # Avoid sharing results between different functions with one prefix.
            namespace = "{}:{}:{}".format(redis_head, func.__module__, func.__qualname__)
            if func.__closure__:
                # Two closures may have the same qualified name but capture
                # different users/configuration. Never share their cache.
                namespace += ":" + uuid.uuid4().hex
            def make_key(args, kwargs):
                return self.cal_redis_key_name(namespace, signature, main_key, *args, **kwargs)
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                try:
                    redis_key = make_key(args, kwargs)
                except (TypeError, RecursionError):
                    return await func(*args, **kwargs)  # Unsupported values: bypass, never collide.
                task_item_0 = {"type": 0, "key": redis_key, "ttl": ttl, "function": func.__name__}
                if self._mode == 2:
                    cache_result = await self._mode_2(task_item_0)
                else:
                    cache_result = await asyncio.get_running_loop().run_in_executor(None, self._mode_1, task_item_0) if self._mode == 1 else self._mode_0(task_item_0)
                if cache_result is None:
                    result = await func(*args, **kwargs)
                    if result is not None:
                        task_item_1 = dict(task_item_0, **{"type": 1, "value": result})
                        if self._mode == 2:
                            await self._mode_2(task_item_1)
                        else:
                            if self._mode == 1:
                                await asyncio.get_running_loop().run_in_executor(None, self._mode_1, task_item_1)
                            else:
                                self._mode_0(task_item_1)

                    return result
                else:
                    return cache_result

            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    redis_key = make_key(args, kwargs)
                except (TypeError, RecursionError):
                    return func(*args, **kwargs)
                task_item_0 = {"type": 0, "key": redis_key, "ttl": ttl, "function": func.__name__}
                if self._mode == 1:
                    cache_result = self._mode_1(task_item_0)
                else:
                    cache_result = self._mode_0(task_item_0)
                if cache_result is None:
                    result = func(*args, **kwargs)
                    if result is not None:
                        task_item_1 = dict(task_item_0, **{"type": 1, "value": result})
                        if self._mode == 1:
                            self._mode_1(task_item_1)
                        else:
                            self._mode_0(task_item_1)
                    return result
                else:
                    return cache_result

            return async_wrapper if iscoroutinefunction(func) else wrapper
        return decorator
