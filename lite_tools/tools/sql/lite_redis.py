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
import re
import json
import random
import threading
import time as _time
from collections import Counter

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

import yaml
import redis as _redis

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
        if not proxy.startswith('http'):
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
        keep_waiting: 如果出现了异常 是否一直重试等待redis服务器修复正常
        timeout     : 如果重试的话 休眠多久重试 默认10s

        如果需要机器人报警，
        """
        self._counter = Counter()
        self.host = host
        self.port = port
        self.password = password
        self.decode = decode_responses
        self.username = username
        self.db = db
        self.kwargs = kwargs

        if path:
            if path.endswith(".yaml") or path.endswith(".yml"):
                self.read_yaml(path)
            elif path.endswith(".json"):
                self.read_json(path)
            elif path.startswith("redis://"):
                # _redis.from_url(path, decode_responses=True) # 我这里不这么运行 因为我要自己封装
                self.read_url(path)
            else:
                logger.warning("path只支持 json/yaml 格式文件")
                exit(0)
        self._redis = self._connect_redis(self.host, self.db, self.password, self.port)
        self.keep_waiting = keep_waiting
        self.timeout = timeout

    @classmethod
    def help(cls):
        """
        这里主要是提示 json文件或者 yaml文件怎么写的
        """
        logger.info("""下面是展示文件的字段怎么写的 后面我写了具体值的就是默认参数 写了~的就是没有设置默认参数 可以只写最基础的字段
        如: myConf.json
        {"host": "xxx", "password": "yyy"}
不传入path参数的话:默认就是走localhost:6379    也可以直接这里面传入参数,但这个就很麻烦  我没有兼容**url格式**的redis链接 没必要
        
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
        try:
            redis = _redis.Redis(
                host=_host, db=_db, password=_password, port=_port, username=self.username,
                decode_responses=self.decode, socket_timeout=5, socket_connect_timeout=5, **self.kwargs)
            return redis
        except Exception as err:
            logger.error(err)

    def _self_incr_error(self, field: str) -> None:
        with lock:
            self._counter[field] += 1

    def _redis_option(self, option, name: str, *args, **kwargs):
        error_time_start = _time.time()
        while True:
            try:
                result = option(name, *args, **kwargs)
                if self._counter["retry"] > 0:  # 如果正常的话 需要恢复为0
                    if self._counter["retry"] > 10:  # 如果重试次数非常多的那种需要报恢复正常的日志
                        error_time_end = _time.time()
                        logger.success(f"{self.host}:{self.port} 的redis恢复正常,"
                                       f"恢复耗时: {error_time_end - error_time_start:.3f}秒")
                    self._counter["retry"] = 0
                if self._counter["redis"] > 0:  # 如果正常的话 需要恢复为0
                    self._counter["redis"] = 0
                return result
            except KeyboardInterrupt:
                break
            except _redis.exceptions.ConnectionError:
                if self._counter["retry"] % 30 == 0:  # 大概这里会 300 秒报错提示一次
                    logger.warning(f"redis链接失败\n\t"
                                   f"错误:redis链接异常...\n\t"
                                   f"主机:{self.host}\n\t"
                                   f"操作:{option.__name__}\n\t"
                                   f"访问库:{name}\n\t"
                                   f"重试:等待10秒重试")
                self._connect_redis(self.host, self.db, self.password, self.port)
                self._self_incr_error("retry")
                logger.warning(f"【{option.__name__}】redis链接异常:正在重新链接 -> 重试次数:{self._counter['retry']}")
            except Exception as err:
                self._self_incr_error("redis")  # 只有链接异常才会进行重连操作
                if self._counter['redis'] % 60 == 0:  # 大概每600秒就会提示报错一次 如果没解决的话
                    logger.error(f"redis 操作失败\n\t"
                                 f"错误:{err}\n\t"
                                 f"主机:{self.host}\n\t"
                                 f"操作:{option.__name__}\n\t"
                                 f"访问库:{name}\n\t"
                                 f"重试:等待{self.timeout + 20}秒重试")
                    _time.sleep(self.timeout + 20)  # 这里的报错需要额外多休息会 因为这里的报错不是链接异常
            if self.keep_waiting:
                _time.sleep(self.timeout)
            else:
                break

    @property
    def redis(self) -> _redis.Redis:
        return self._redis

    client = redis

    def set_param(self, config: dict, from_url: bool = False):
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)
        self.password = config.get("password")
        self.username = config.get("username")
        if not from_url:
            self.decode = config.get("decode", True)
            self.kwargs = config.get("kwargs", {})

    def read_yaml(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                config = yaml.load(fp.read(), Loader=yaml.Loader)
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
        username = re.search(r"//([^.]+):", path)
        password = re.search(r"redis://.*?:(\S+)@", path)
        host = re.search(r"@(\S+):", path) or re.search(r"//(\S+):\d+", path)
        port = re.search(r":(\d{2,5})/?", path)
        db = re.search(r":\d+/(\d+)", path)
        conf = {
            "host": host.group(1) if host else "127.0.0.1",
            "port": int(port.group(1)) if port else 6379,
            "db": int(db.group(1)) if db else 0,
            "password": password.group(1) if password else None,
            "username": username.group(1) if username else None
        }
        self.set_param(conf, from_url=True)

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
        return self._redis_option(self.redis.scan_iter, match, count, _type, **kwargs)

    def sscan_iter(self, name: str, match: Union[PatternT, None] = None, count: Union[int, None] = None):
        return self._redis_option(self.redis.sscan_iter, name, match, count)

    def hscan_iter(self, name: str, match: Union[PatternT, None] = None, count: Union[int, None] = None):
        return self._redis_option(self.redis.hscan_iter, name, match, count)

    def zscan_iter(self, name: str, match: Union[PatternT, None] = None, count: Union[int, None] = None,
                   score_cast_func: Union[type, Callable] = float):
        return self._redis_option(self.redis.zscan_iter, name, match, count, score_cast_func)

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
        return self._redis_option(self.redis.zrank, name, value, withscore)

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
        return self._redis_option(self.redis.hset, name, key, value, mapping, items)

    def hsetnx(self, name: str, key: str, value: str) -> bool:
        return self._redis_option(self.redis.hsetnx, name, key, value)

    def __getattr__(self: T, name: str):
        def default_method(*args, **kwargs) -> T:
            """
            没有封装的方法将会走这里
            """
            option = getattr(self.redis, name)
            return self._redis_option(option, *args, **kwargs)

        return default_method


class SimpleHash(object):
    def __init__(self, cap, seed):
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
        self.server = redis
        self.key = key
        self.block_num = block_num
        self.bit_size = bit_size if bit_size < 4294967296 else 4294967296   # 限制最大只能512M
        self.seeds = [5, 7, 11, 13, 31, 37, 61] if not seeds else seeds
        self.hash_func = [SimpleHash(self.bit_size, seed) for seed in self.seeds]  # 创建不同素材的hash函数

    def _get_name(self, string):
        """对结果进行分区 这样有便于 分区管理 去重"""
        string = get_md5(string)
        name = f"{self.key}:{int(string[:2], 16) % self.block_num}"
        return string, name

    def remove(self):
        """移除布隆过滤器"""
        self.server.delete(self.key)

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
        ret = True
        for func in self.hash_func:
            loc = func.hash(string)
            ret ^= self.server.getbit(name, loc)
        # 上面判断了是否包含
        return True if not ret else False
