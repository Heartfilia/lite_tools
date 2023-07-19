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
import time
import random
from typing import Union, Sequence, List
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import yaml
import redis as _redis

from lite_tools.logs import logger
from lite_tools.tools.core.lib_hashlib import get_md5
from lite_tools.exceptions.CacheExceptions import FileNotFount


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
                    time.sleep(0.3)
                    continue
                return self._trans_type(t, proxy)
            except Exception as err:
                logger.warning(f"代理提取异常 --> {err}")
                time.sleep(1)
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
            host: str = "localhost",
            port: int = 6379,
            password: str = None,
            decode_responses: bool = True,
            **kwargs):
        if path:
            if path.endswith(".yaml") or path.endswith(".yml"):
                self.read_yaml(path)
            elif path.endswith(".json"):
                self.read_json(path)
            else:
                logger.warning("path只支持 json/yaml 格式文件")
                exit(0)
        else:
            self.host = host
            self.port = port
            self.password = password
            self.decode = decode_responses
            self.kwargs = kwargs
            self.db = db
        self.rd = None

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
{"host": "localhost", "port": 6379, "password": ~, "decode": True, "kwargs": {其它配置用字典传这里}}

YAML示例: 文件名.yaml/文件名.yml
host: "localhost"  # YAML文件字符串有没有双引号都可以
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

    @property
    def client(self) -> _redis.Redis:
        if not self.rd:
            self.rd = _redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                decode_responses=self.decode,
                db=self.db,
                **self.kwargs
            )
            logger.success("redis-链接成功 这里是一个`property` 如果说Redis Not Callable, 请不要加后面的括号哦~")
        return self.rd

    def set_param(self, config: dict):
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)
        self.password = config.get("password")
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
        :param redis: redis链接对象
        :param key  : 需要创建的key
        :param seeds  : 随机种子
        :param bit_size  : 容量控制 我这里默认256M redis最大为 512M
        :param block_num: one blockNum for about 90,000,000; if you have more strings for filtering, increase it.
        """
        self.server = redis
        self.key = key
        self.block_num = block_num
        self.bit_size = bit_size if bit_size < 4294967296 else 4294967296   # 限制最大只能512M
        self.seeds = [5, 7, 11, 13, 31, 37, 61] if not seeds else seeds
        self.hash_func = [SimpleHash(self.bit_size, seed) for seed in self.seeds]  # 创建不同素材的hash函数

    def remove(self):
        """移除布隆过滤器"""
        self.server.delete(self.key)

    def insert(self, string: str) -> None:
        """插入"""
        string = get_md5(string)
        name = f"{self.key}{int(string[:2], 16) % self.block_num}"
        for func in self.hash_func:
            loc = func.hash(string)
            self.server.setbit(name, loc, 1)

    def exists(self, string: str) -> bool:
        """判断"""
        if not string:
            # 空直接判断为存在 这样子就没有必要跑了
            return True
        string = get_md5(string)
        ret = True
        name = f"{self.key}{int(string[:2], 16) % self.block_num}"
        for func in self.hash_func:
            loc = func.hash(string)
            ret ^= self.server.getbit(name, loc)
        # 上面判断了是否包含
        return True if not ret else False
