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
"""
import json
import random
import threading
import time as _time
from collections import Counter
from collections.abc import Mapping as MappingABC

from datetime import datetime, timedelta
from typing import Union, Sequence, List, Optional, TypeVar, Callable, Mapping, Set

try:
    from redis.typing import (
        EncodableT,
        ExpiryT,
        AbsExpiryT,
        FieldT,
        PatternT,
        AnyKeyT,
        ZScoreBoundT
    )
except ImportError:
    EncodedT = Union[bytes, memoryview]
    DecodedT = Union[str, int, float]
    EncodableT = Union[EncodedT, DecodedT]
    _StringLikeT = Union[bytes, str, memoryview]
    KeyT = _StringLikeT  # Main redis key space
    PatternT = _StringLikeT
    FieldT = EncodableT
    AbsExpiryT = Union[int, datetime]
    ExpiryT = Union[int, timedelta]
    AnyKeyT = TypeVar("AnyKeyT", bytes, str, memoryview)
    ZScoreBoundT = Union[float, str]


try:
    from typing import Literal
except ImportError:
    try:
        from typing_extensions import Literal
    except ImportError:
        from lite_tools.utils.pip_ import install
        install('typing_extensions')
        from typing_extensions import Literal

import redis as _redis
from redis.backoff import NoBackoff
from redis.retry import Retry
from redis.connection import parse_url, SSLConnection

from lite_tools.logs import logger
from lite_tools.tools.core.lib_hashlib import get_md5
from lite_tools.exceptions.CacheExceptions import FileNotFount


lock = threading.Lock()
T = TypeVar('T', bound='Redis')


class LiteProxy:
    def __init__(self, redis_client: _redis.Redis, redis_name: Union[str, Sequence], retry: int = 5,
                 mode: Literal['set', 'list'] = 'set'):
        """
        基于redis设计的代理池 --> 默认模式是 set 类型: 方便随机弹出  也可以list,滚动提取
        :param redis_client: 构造好的 redis 链接对象
        :param redis_name  : 代理放的位置(名字) 也可以放多个名字用 list  tuple  set 都可以 会随机取这里的值
        :param retry       : 重试获取代理的次数-->如果获取到代理为空的重试次数 如果最后也拿不到 返回 None  <-- 不会报错注意捕获
        :param mode        : 代理默认存储是set模式,也可以使用list模式
        """
        self.redis = redis_client
        self.redis_name = redis_name
        self.retry = retry
        self.mode = mode

    def get(self, t: Literal['default', 'httpx', 'string'] = 'default') -> Union[dict, str, None]:
        """
        默认调用就返回一个ip
        :param t: 返回代理的格式 我这里默认三种
            default --> {"http": "xxx", "https": "xxx"}
            httpx   --> {"http://": "xxx", "https://": "xxx", "all://": "xxx"}
            string  --> "http://xxxx"
        """
        for _ in range(self.retry):
            try:
                if isinstance(self.redis_name, str):
                    redis_name = self.redis_name
                else:
                    redis_name = random.choice(self.redis_name)
                proxy = self.get_item_from_redis(redis_name)
                if not proxy:
                    _time.sleep(0.3)
                    continue
                return self._trans_type(t, proxy)
            except Exception as err:
                logger.warning(f"代理提取异常 --> {err}")
                _time.sleep(1)
        return None

    def get_item_from_redis(self, redis_name: str):
        if self.mode == 'list':
            return self.redis.rpoplpush(redis_name, redis_name)
        else:
            return self.redis.srandmember(redis_name)

    @staticmethod
    def _trans_type(mode: str, proxy: str = None) -> Union[dict, str, None]:
        if proxy is None:
            return None
        if isinstance(proxy, bytes):
            proxy = proxy.decode("utf-8")
        if not isinstance(proxy, str) or not proxy.strip():
            raise ValueError("代理必须是非空字符串")
        if "://" not in proxy:
            proxy = f"http://{proxy}"

        if mode == "httpx":
            return {
                "http://": proxy,
                "https://": proxy,
                "all://": proxy
            }
        elif mode == "string":
            return proxy
        else:
            return {
                "http": proxy,
                "https": proxy
            }


# rd = LiteRedis("/root/config.yaml")
# rd = LiteRedis("/root/config.json")
class LiteRedis:
    """
    配置文件创建redis对象
    """
    def __init__(
            self,
            path: str = None,
            db: int = 0,
            *,
            host: str = "127.0.0.1",
            port: int = 6379,
            password: str = None,
            username: str = None,
            decode_responses: bool = True,
            keep_waiting: bool = True,
            timeout: int = 10,
            **kwargs):
        """
        keep_waiting: 是否对只读操作的临时连接错误进行有限重试；写操作不会自动重放
        timeout     : 重试间隔，默认10s。kwargs 可设 retry_attempts=3、retry_deadline=30

        如果需要机器人报警，
        """
        self._counter = Counter()
        if not isinstance(keep_waiting, bool):
            raise ValueError("keep_waiting 必须是 bool")
        self.host = host
        self.port = port
        self.password = password
        self.decode = decode_responses
        self.username = username
        self.db = db
        self.kwargs = kwargs
        self.keep_waiting = keep_waiting
        self.timeout = timeout

        if path:
            if path.startswith(("redis://", "rediss://")):
                self.read_url(path)
            elif path.endswith(".yaml") or path.endswith(".yml"):
                self.read_yaml(path)
            elif path.endswith(".json"):
                self.read_json(path)
            else:
                raise ValueError("path只支持 json/yaml 文件或 redis://、rediss:// URL")
        # Apply the same validation to direct parameters and file/URL configs.
        self.set_param({"host": self.host, "port": self.port, "db": self.db,
                        "password": self.password, "username": self.username,
                        "decode": self.decode})
        self._retry_attempts = self.kwargs.pop("retry_attempts", 3)
        self._retry_deadline = self.kwargs.pop("retry_deadline", 30)
        if isinstance(self._retry_attempts, bool) or not isinstance(self._retry_attempts, int) or self._retry_attempts < 1:
            raise ValueError("retry_attempts 必须是正整数")
        for name, value in (("timeout", timeout), ("retry_deadline", self._retry_deadline)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < float("inf"):
                raise ValueError("{} 必须是有限非负数".format(name))
        self._redis = self._connect_redis(self.host, self.db, self.password, self.port)

    @classmethod
    def help(cls):
        """
        这里主要是提示 json文件或者 yaml文件怎么写的
        """
        logger.info("""下面是展示文件的字段怎么写的 后面我写了具体值的就是默认参数 写了~的就是没有设置默认参数 可以只写最基础的字段
        如: myConf.json
        {"host": "xxx", "password": "yyy"}
不传入path参数的话默认连接 localhost:6379，也支持 redis:// 和 rediss:// URL。
        
JSON示例: 文件名.json
{"host": "127.0.0.1", "port": 6379, "password": ~, "decode": True, "kwargs": {其它配置用字典传这里}}

YAML示例: 文件名.yaml/文件名.yml
host: "127.0.0.1"  # YAML文件字符串有没有双引号都可以
port: 6379
password: ~
decode: True
kwargs: 
  xxx: ~
  yyy: ~
  zzz: ~  
  
创建DEMO:
  app = LiteRedis('test.json').client   后面的client没有括号哦~    
        """)

    def _connect_redis(self, _host: str, _db: int, _password: str, _port: int) -> Optional[_redis.Redis]:
        """
        这里创建链接是不会报错的 地址不对都不会报错 这里的报错只是参数异常报错
        """
        options = dict(socket_timeout=5, socket_connect_timeout=5)
        options.update(self.kwargs)
        # redis-py 6+ retries writes by default. Disable transport replay here;
        # the wrapper retries only explicitly known read-only operations.
        options.pop("retry_on_timeout", None)
        options.update(retry=Retry(NoBackoff(), 0), retry_on_error=[])
        return _redis.Redis(host=_host, db=_db, password=_password, port=_port,
                            username=self.username, decode_responses=self.decode, **options)

    def _self_incr_error(self, field: str) -> None:
        with lock:
            self._counter[field] += 1

    _READ_ONLY = frozenset((
        "get", "mget", "exists", "ttl", "pttl", "type", "strlen", "getbit", "getrange", "substr",
        "lindex", "llen", "lrange", "scard", "sismember", "smismember", "smembers", "srandmember",
        "hget", "hmget", "hgetall", "hexists", "hkeys", "hlen", "hvals", "hstrlen",
        "zcard", "zcount", "zrange", "zrank", "zscore", "zmscore", "zrandmember",
        "scan", "sscan", "hscan", "zscan", "keys", "ping", "echo", "dbsize",
    ))

    def _redis_option(self, option, *args, **kwargs):
        started = _time.monotonic()
        method = getattr(option, "__name__", "")
        attempts = self._retry_attempts if self.keep_waiting and method in self._READ_ONLY else 1
        for attempt in range(attempts):
            try:
                result = option(*args, **kwargs)
                with lock:
                    self._counter["retry"] = 0
                    self._counter["redis"] = 0
                return result
            except (_redis.exceptions.AuthenticationError, _redis.exceptions.AuthorizationError):
                raise
            except (_redis.exceptions.ConnectionError, _redis.exceptions.TimeoutError):
                self._self_incr_error("retry")
                if attempt + 1 >= attempts or _time.monotonic() - started + self.timeout >= self._retry_deadline:
                    raise
                _time.sleep(self.timeout)

    @property
    def redis(self) -> _redis.Redis:
        return self._redis

    client = redis

    def set_param(self, config: dict, from_url: bool = False):
        if not isinstance(config, MappingABC):
            raise ValueError("Redis 配置必须是字典")
        options = config.get("kwargs", {})
        if not isinstance(options, MappingABC):
            raise ValueError("Redis kwargs 必须是字典")
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)
        if not isinstance(self.host, str) or not self.host:
            raise ValueError("Redis host 必须是非空字符串")
        for name, value, upper in (("port", self.port, 65535), ("db", self.db, None)):
            if isinstance(value, bool) or not isinstance(value, int) or value < (1 if name == "port" else 0) or (upper and value > upper):
                raise ValueError("Redis {} 不合法".format(name))
        self.password = config.get("password")
        self.username = config.get("username")
        if not from_url:
            self.decode = config.get("decode_responses", config.get("decode", True))
            if not isinstance(self.decode, bool):
                raise ValueError("Redis decode 必须是 bool")
            self.kwargs = dict(self.kwargs, **options)

    def read_yaml(self, path: str):
        try:
            import yaml
        except ImportError as err:
            raise ImportError("读取 YAML 需要安装 PyYAML；JSON/URL/直接传参不需要") from err
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                config = yaml.safe_load(fp)
        except (FileNotFoundError, FileExistsError):
            raise FileNotFount(path)
        else:
            self.set_param(config)

    def read_json(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                config = json.load(fp)
        except (FileNotFoundError, FileExistsError):
            raise FileNotFount(path)
        else:
            self.set_param(config)

    def read_url(self, path: str):
        if not path.startswith(("redis://", "rediss://")):
            raise ValueError("仅支持 redis://、rediss://")
        parsed = parse_url(path)
        connection_class = parsed.pop("connection_class", None)
        if connection_class is SSLConnection:
            parsed["ssl"] = True
        conf = {key: parsed.pop(key) for key in ("host", "port", "db", "username", "password") if key in parsed}
        decode = parsed.pop("decode_responses", self.decode)
        if isinstance(decode, str):
            if decode.lower() not in ("true", "false", "1", "0", "yes", "no"):
                raise ValueError("decode_responses 必须是布尔值")
            decode = decode.lower() in ("true", "1", "yes")
        self.set_param(conf, from_url=True)
        self.decode = decode
        self.kwargs.update(parsed)

    def delete(self, name: str) -> int:
        return self._redis_option(self.redis.delete, name)

    def exists(self, name: str) -> bool:
        return self._redis_option(self.redis.exists, name)

    def expire(
            self,
            name: str,
            time: ExpiryT,
            nx: bool = False,
            xx: bool = False,
            gt: bool = False,
            lt: bool = False,
    ) -> bool:
        """
        Set an expire flag on key ``name`` for ``time`` seconds with given
        ``option``. ``time`` can be represented by an integer or a Python timedelta
        object.

        Valid options are:
            NX -> Set expiry only when the key has no expiry
            XX -> Set expiry only when the key has an existing expiry
            GT -> Set expiry only when the new expiry is greater than current one
            LT -> Set expiry only when the new expiry is less than current one

        For more information see https://redis.io/commands/expire
        """
        return self._redis_option(self.redis.expire, name, time, nx, xx, gt, lt)

    def get(self, name: str) -> Optional[str]:
        return self._redis_option(self.redis.get, name)

    def getbit(self, name: str, offset: int) -> int:
        return self._redis_option(self.redis.getbit, name, offset)

    def incrby(self, name: str, amount: int = 1) -> int:
        return self._redis_option(self.redis.incrby, name, amount)

    incr = incrby

    def decrby(self, name: str, amount: int = 1) -> int:
        return self._redis_option(self.redis.decrby, name, amount)

    decr = decrby

    def incrbyfloat(self, name: str, amount: float = 1.0) -> float:
        return self._redis_option(self.redis.incrbyfloat, name, amount)

    def keys(self, pattern: str = "*") -> List:
        return self._redis_option(self.redis.keys, pattern)

    def move(self, name: str, db: int) -> bool:
        return self._redis_option(self.redis.move, name, db)

    def rename(self, src: str, dst: str) -> bool:
        return self._redis_option(self.redis.rename, src, dst)

    def set(
            self,
            name: str,
            value: EncodableT,
            ex: Union[ExpiryT, None] = None,
            px: Union[ExpiryT, None] = None,
            nx: bool = False,
            xx: bool = False,
            keepttl: bool = False,
            get: bool = False,
            exat: Union[AbsExpiryT, None] = None,
            pxat: Union[AbsExpiryT, None] = None
    ) -> bool:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return self._redis_option(self.redis.set, name, value, ex, px, nx, xx, keepttl, get, exat, pxat)

    def setbit(self, name: str, offset: int, value: int) -> int:
        return self._redis_option(self.redis.setbit, name, offset, value)

    def setex(self, name: str, time: ExpiryT, value: EncodableT):
        return self._redis_option(self.redis.setex, name, time, value)

    def setnx(self, name: str, value: EncodableT):
        return self._redis_option(self.redis.setnx, name, value)

    def setrange(self, name: str, offset: int, value: EncodableT):
        return self._redis_option(self.redis.setrange, name, offset, value)

    def strlen(self, name: str) -> int:
        return self._redis_option(self.redis.strlen, name)

    def substr(self, name: str, start: int, end: int = -1) -> str:
        return self._redis_option(self.redis.substr, name, start, end)

    def ttl(self, name: str) -> int:
        return self._redis_option(self.redis.ttl, name)

    def type(self, name: str) -> str:
        return self._redis_option(self.redis.type, name)

    # --------------------------上面是key的操作 下面是list的操作---------------------------

    def lindex(self, name: str, index: int) -> Optional[str]:
        return self._redis_option(self.redis.lindex, name, index)

    def linsert(self, name: str, where: str, refvalue: str, value: str) -> int:
        """
        Insert ``value`` in list ``name`` either immediately before or after
        [``where``] ``refvalue``

        Returns the new length of the list on success or -1 if ``refvalue``
        is not in the list.

        For more information see https://redis.io/commands/linsert
        """
        return self._redis_option(self.redis.linsert, name, where, refvalue, value)

    def llen(self, name: str) -> int:
        return self._redis_option(self.redis.llen, name)

    def lpop(self, name: str, count: Optional[int] = None) -> Union[str, List, None]:
        return self._redis_option(self.redis.lpop, name, count)

    def lpush(self, name: str, *values: FieldT) -> int:
        return self._redis_option(self.redis.lpush, name, *values)

    def lpushx(self, name: str, *values: FieldT) -> int:
        return self._redis_option(self.redis.lpushx, name, *values)

    def lrange(self, name: str, start: int, end: int) -> list:
        return self._redis_option(self.redis.lrange, name, start, end)

    def lrem(self, name: str, count: int, value: str) -> int:
        return self._redis_option(self.redis.lrem, name, count, value)

    def lset(self, name: str, index: int, value: str) -> str:
        """
        Set element at ``index`` of list ``name`` to ``value``

        For more information see https://redis.io/commands/lset
        """
        return self._redis_option(self.redis.lset, name, index, value)

    def ltrim(self, name: str, start: int, end: int) -> str:
        """
        Trim the list ``name``, removing all values not within the slice
        between ``start`` and ``end``

        ``start`` and ``end`` can be negative numbers just like
        Python slicing notation

        For more information see https://redis.io/commands/ltrim
        """
        return self._redis_option(self.redis.ltrim, name, start, end)

    def rpop(self, name: str, count: Optional[int] = None) -> Union[str, List, None]:
        return self._redis_option(self.redis.rpop, name, count)

    def rpoplpush(self, src: str, dst: str) -> Optional[str]:
        return self._redis_option(self.redis.rpoplpush, src, dst)

    def rpush(self, name: str, *values: FieldT) -> int:
        return self._redis_option(self.redis.rpush, name, *values)

    def rpushx(self, name: str, value: str) -> int:
        return self._redis_option(self.redis.rpushx, name, value)

    def sort(
            self,
            name: str,
            start: Optional[int] = None,
            num: Optional[int] = None,
            by: Optional[str] = None,
            get: Optional[List[str]] = None,
            desc: bool = False,
            alpha: bool = False,
            store: Optional[str] = None,
            groups: Optional[bool] = False) -> Union[List, int]:
        """
        Sort and return the list, set or sorted set at ``name``.

        ``start`` and ``num`` allow for paging through the sorted data

        ``by`` allows using an external key to weight and sort the items.
            Use an "*" to indicate where in the key the item value is located

        ``get`` allows for returning items from external keys rather than the
            sorted data itself.  Use an "*" to indicate where in the key
            the item value is located

        ``desc`` allows for reversing the sort

        ``alpha`` allows for sorting lexicographically rather than numerically

        ``store`` allows for storing the result of the sort into
            the key ``store``

        ``groups`` if set to True and if ``get`` contains at least two
            elements, sort will return a list of tuples, each containing the
            values fetched from the arguments to ``get``.

        For more information see https://redis.io/commands/sort
        """
        return self._redis_option(self.redis.sort, name, start, num, by, get, desc, alpha, store, groups)

    # ----------------上面是list 下面是set hash--------------------------
    def scan_iter(self, match: Union[PatternT, None] = None, count: Union[int, None] = None,
                  _type: Union[str, None] = None, **kwargs):
        cursor = 0
        while True:
            cursor, items = self._redis_option(self.redis.scan, cursor=cursor, match=match, count=count, _type=_type, **kwargs)
            yield from items
            if int(cursor) == 0:
                break

    def sscan_iter(self, name: str, match: Union[PatternT, None] = None, count: Union[int, None] = None):
        cursor = 0
        while True:
            cursor, items = self._redis_option(self.redis.sscan, name, cursor=cursor, match=match, count=count)
            yield from items
            if int(cursor) == 0:
                break

    def hscan_iter(self, name: str, match: Union[PatternT, None] = None, count: Union[int, None] = None):
        cursor = 0
        while True:
            cursor, items = self._redis_option(self.redis.hscan, name, cursor=cursor, match=match, count=count)
            yield from items.items()
            if int(cursor) == 0:
                break

    def zscan_iter(self, name: str, match: Union[PatternT, None] = None, count: Union[int, None] = None,
                   score_cast_func: Union[type, Callable] = float):
        cursor = 0
        while True:
            cursor, items = self._redis_option(self.redis.zscan, name, cursor=cursor, match=match, count=count,
                                              score_cast_func=score_cast_func)
            yield from items
            if int(cursor) == 0:
                break

    def sadd(self, name: str, *values: FieldT) -> None:
        if len(values) == 1 and isinstance(values[0], (dict, list)):
            return self._redis_option(self.redis.sadd, name, json.dumps(values[0], ensure_ascii=False))
        return self._redis_option(self.redis.sadd, name, *values)

    def scard(self, name: str) -> int:
        return self._redis_option(self.redis.scard, name)

    def sismember(self, name: str, value: str) -> int:
        return self._redis_option(self.redis.sismember, name, value)

    def smembers(self, name: str) -> Set:
        return self._redis_option(self.redis.smembers, name)

    def smismember(self, name: str, values: List, *args: List) -> List[Union[Literal[0], Literal[1]]]:
        return self._redis_option(self.redis.smismember, name, values, *args)

    def smove(self, src: str, dst: str, value: str) -> bool:
        """
        Move ``value`` from set ``src`` to set ``dst`` atomically

        For more information see https://redis.io/commands/smove
        """
        return self._redis_option(self.redis.smove, src, dst, value)

    def spop(self, name: str, count: Optional[int] = None) -> Union[str, List, None]:
        return self._redis_option(self.redis.spop, name, count)

    def srandmember(self, name: str, number: Optional[int] = None) -> Union[str, List, None]:
        return self._redis_option(self.redis.srandmember, name, number)

    def srem(self, name: str, *values: FieldT) -> int:
        """
        Remove ``values`` from set ``name``

        For more information see https://redis.io/commands/srem
        """
        return self._redis_option(self.redis.srem, name, *values)

    # ----------------- 这里为固定集合的操作 -----------------------

    def zadd(
            self,
            name: str,
            mapping: Mapping[AnyKeyT, EncodableT],
            nx: bool = False,
            xx: bool = False,
            ch: bool = False,
            incr: bool = False,
            gt: bool = False,
            lt: bool = False,
    ):
        """
        Set any number of element-name, score pairs to the key ``name``. Pairs
        are specified as a dict of element-names keys to score values.

        ``nx`` forces ZADD to only create new elements and not to update
        scores for elements that already exist.

        ``xx`` forces ZADD to only update scores of elements that already
        exist. New elements will not be added.

        ``ch`` modifies the return value to be the numbers of elements changed.
        Changed elements include new elements that were added and elements
        whose scores changed.

        ``incr`` modifies ZADD to behave like ZINCRBY. In this mode only a
        single element/score pair can be specified and the score is the amount
        the existing score will be incremented by. When using this mode the
        return value of ZADD will be the new score of the element.

        ``LT`` Only update existing elements if the new score is less than
        the current score. This flag doesn't prevent adding new elements.

        ``GT`` Only update existing elements if the new score is greater than
        the current score. This flag doesn't prevent adding new elements.

        The return value of ZADD varies based on the mode specified. With no
        options, ZADD returns the number of new elements added to the sorted
        set.

        ``NX``, ``LT``, and ``GT`` are mutually exclusive options.

        See: https://redis.io/commands/ZADD
        """
        return self._redis_option(self.redis.zadd, name, mapping, nx, xx, ch, incr, gt, lt)

    def zcard(self, name: str) -> int:
        return self._redis_option(self.redis.zcard, name)

    def zcount(self, name: str, min: ZScoreBoundT, max: ZScoreBoundT) -> int:
        return self._redis_option(self.redis.zcount, name, min, max)

    def zincrby(self, name: str, amount: float, value: EncodableT) -> int:
        return self._redis_option(self.redis.zincrby, name, amount, value)

    def zpopmax(self, name: str, count: Union[int, None] = None):
        return self._redis_option(self.redis.zpopmax, name, count)

    def zpopmin(self, name: str, count: Union[int, None] = None):
        return self._redis_option(self.redis.zpopmin, name, count)

    def zrandmember(self, name: str, count: int = None, withscores: bool = False):
        return self._redis_option(self.redis.zrandmember, name, count, withscores)

    def zrange(
            self,
            name: str,
            start: int,
            end: int,
            desc: bool = False,
            withscores: bool = False,
            score_cast_func: Union[type, Callable] = float,
            byscore: bool = False,
            bylex: bool = False,
            offset: int = None,
            num: int = None,
    ):
        return self._redis_option(self.redis.zrange, name, start, end, desc, withscores, score_cast_func,
                                  byscore, bylex, offset, num)

    def zrank(
            self,
            name: str,
            value: EncodableT,
            withscore: bool = False,
    ):
        if withscore:
            return self._redis_option(self.redis.zrank, name, value, withscore=True)
        return self._redis_option(self.redis.zrank, name, value)

    def zrem(self, name: str, *values: FieldT):
        return self._redis_option(self.redis.zrem, name, *values)

    def zscore(self, name: str, value: EncodableT):
        return self._redis_option(self.redis.zscore, name, value)

    # --------------------- hash 的部分操作 -------------------------------

    def hdel(self, name: str, *keys: List) -> int:
        return self._redis_option(self.redis.hdel, name, *keys)

    def hexists(self, name: str, key: str) -> bool:
        return self._redis_option(self.redis.hexists, name, key)

    def hget(self, name: str, key: str) -> Optional[str]:
        return self._redis_option(self.redis.hget, name, key)

    def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        return self._redis_option(self.redis.hincrby, name, key, amount)

    def hincrbyfloat(self, name: str, key: str, amount: float = 1.0) -> float:
        return self._redis_option(self.redis.hincrbyfloat, name, key, amount)

    def hkeys(self, name: str) -> List:
        return self._redis_option(self.redis.hkeys, name)

    def hlen(self, name: str) -> int:
        return self._redis_option(self.redis.hlen, name)

    def hset(self, name: str, key: str = None, value: FieldT = None,
             mapping: Optional[dict] = None, items: Optional[list] = None, ) -> int:
        """
        value 为 dict 和 list的时候做了兼容 会自动转换为 json字符串存储
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        options = dict(key=key, value=value, mapping=mapping)
        if items is not None:
            options["items"] = items
        return self._redis_option(self.redis.hset, name, **options)

    def hsetnx(self, name: str, key: str, value: str) -> bool:
        return self._redis_option(self.redis.hsetnx, name, key, value)

    def __getattr__(self: T, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        option = getattr(self.redis, name)
        if not callable(option):
            return option
        def default_method(*args, **kwargs) -> T:
            """
            没有封装的方法将会走这里
            """
            return self._redis_option(option, *args, **kwargs)

        return default_method


class SimpleHash(object):
    def __init__(self, cap, seed):
        if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1 or cap > (1 << 32) or cap & (cap - 1):
            raise ValueError("cap 必须是 1 到 2**32 范围内的 2 的幂")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed <= 0:
            raise ValueError("seed 必须是正整数")
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter:
    def __init__(self, redis: Union[_redis.StrictRedis, _redis.Redis], key: str,
                 block_num: int = 1, bit_size: int = 1 << 31, seeds: List[int] = None):
        """
        :param redis     : redis链接对象
        :param key       : 需要创建的redis的key的基础名字
        :param seeds     : 随机种子
        :param bit_size  : 容量控制 我这里默认256M redis最大为 512M
        :param block_num : 分区数量 设置为其它则会创建好几个 redis分区管理
        """
        if isinstance(block_num, bool) or not isinstance(block_num, int) or not 1 <= block_num <= 256:
            raise ValueError("block_num 必须是 1 到 256 的整数")
        if not isinstance(key, str) or not key:
            raise ValueError("key 必须是非空字符串")
        if seeds is not None:
            if (not isinstance(seeds, list) or not seeds or
                    any(isinstance(seed, bool) or not isinstance(seed, int) or seed <= 0 for seed in seeds) or
                    len(set(seeds)) != len(seeds)):
                raise ValueError("seeds 必须是非空且不重复的正整数列表")
        self.server = redis
        self.key = key
        self.block_num = block_num
        self.bit_size = bit_size
        self.seeds = [5, 7, 11, 13, 31, 37, 61] if seeds is None else list(seeds)
        self.hash_func = [SimpleHash(self.bit_size, seed) for seed in self.seeds]  # 创建不同素材的hash函数

    def _get_name(self, string):
        """对结果进行分区 这样有便于 分区管理 去重"""
        string = get_md5(string)
        name = f"{self.key}:{int(string[:2], 16) % self.block_num}"
        return string, name

    def remove(self):
        """移除布隆过滤器"""
        # Delete exact partition names, never a glob that could match unrelated
        # application keys. Individual deletes also work on Redis Cluster.
        for partition in range(self.block_num):
            self.server.delete("{}:{}".format(self.key, partition))

    def insert(self, string: str) -> None:
        """插入"""
        string, name = self._get_name(string)
        for func in self.hash_func:
            loc = func.hash(string)
            self.server.setbit(name, loc, 1)

    def exists(self, string: str) -> bool:
        """判断"""
        if not string:
            # 空直接判断为存在 这样子就没有必要跑了
            return True
        string, name = self._get_name(string)
        for func in self.hash_func:
            loc = func.hash(string)
            if not self.server.getbit(name, loc):
                return False
        return True
