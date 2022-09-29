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

import redis

from lite_tools.tools.utils.logs import logger
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
            if path.endswith(".yaml"):
                pass
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
        return self.rd

    def read_yaml(self, path: str):
        pass

    def read_json(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                config = json.load(fp)
        except (FileNotFoundError, FileExistsError):
            raise FileNotFount(path)
        else:
            self.host = config.get("host", "localhost")
            self.port = config.get("port", 6379)
            self.password = config.get("password")
            self.decode = config.get("decode", True)
            self.kwargs = config.get("kwargs", {})

