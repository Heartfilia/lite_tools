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
from typing import Union, Literal, Sequence

from lite_tools.tools.utils.logs import logger

try:
    import yaml
    import redis
except ImportError:
    logger.error("这里需要[pyyaml][redis]这两个包: 也可以尝试安装--> pip install lite-tools[plus]")
    exit(0)

from lite_tools.exceptions.CacheExceptions import FileNotFount


class LiteProxy:
    def __init__(self, redis_client: redis.Redis, redis_name: Union[str, Sequence], retry: int = 5):
        """
        基于redis设计的代理池 --> 模式是 set 类型: 方便随机弹出
        :param redis_client: 构造好的 redis 链接对象
        :param redis_name  : 代理放的位置(名字) 也可以放多个名字用 list  tuple  set 都可以 会随机取这里的值
        :param retry       : 重试获取代理的次数-->如果获取到代理为空的重试次数 如果最后也拿不到 返回 None  <-- 不会报错注意捕获
        """
        self.redis = redis_client
        self.redis_name = redis_name
        self.retry = retry

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
                proxy = self.redis.srandmember(redis_name)
                if not proxy:
                    time.sleep(0.3)
                    continue
                return self._trans_type(t, proxy)
            except Exception as err:
                logger.warning(f"代理提取异常 --> {err}")
                time.sleep(1)
        return None

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


# 下面功能虽然没啥用 是因为只是一个雏形 以后会加入读取配置文件 这样每次只需要去读指定位置的配置文件就好了如
# rd = LiteRedis("/root/config.yaml")
# rd = LiteRedis("/root/config.json")
class LiteRedis:
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

    @staticmethod
    def help():
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
        """)

    @property
    def client(self):
        if not self.rd:
            self.rd = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                decode_responses=self.decode,
                db=self.db,
                **self.kwargs
            )
            logger.success("redis-链接成功")
        return self.rd

    def set_param(self, config: dict):
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6379)
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
