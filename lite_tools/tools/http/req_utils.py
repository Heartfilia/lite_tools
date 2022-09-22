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
from typing import Literal, Union, TypeVar, Mapping

import httpx
import requests

from lite_tools.tools.time.lite_time import get_time


T = TypeVar('T')


class LiteHistory:
    status_code: int = 200
    url: str
    cookie: dict
    headers: dict

    def __str__(self):
        return f"<Response [{self.status_code}]>"

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]


class LiteResponse:
    status_code: int = 200
    url: str
    request_time: float      # ms 单位
    body: ...
    decode: str   # 这里还不确定怎么弄
    request_mode: str = 'requests'
    cookies: Union[requests.Response.cookies, httpx.Response.cookies]
    headers: Mapping[str, T]
    history: LiteHistory

    def __new__(cls):
        cls.request_time = get_time(instance=float)

    def __str__(self):
        return f"<Response [{self.status_code}]>"

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]


class LiteRequest(object):
    def __init__(self, retry: int = 5):
        self.retry = retry

    def send(self, url,
             *,
             method: Literal['get', 'post', 'head', 'put', 'delete'] = 'get',  # request, patch, options这些不搞
             h2: bool = False,
             encoding: str = None,
             proxies: Union[dict, str] = None,
             headers: Mapping[str, T] = None,
             cookies: Mapping[str, T] = None,
             params: Mapping[str, T] = None,
             json: Mapping[str, T] = None,
             data: Union[dict, str, tuple] = None,
             timeout: Union[int, float] = 3,
             verify: bool = None,
             **kwargs):   # 其它一些不咋用到的参数就给隐藏了
        """
        这里是一个简单的发包请求参数同requests,httpx 主要多了h2切换模式, ret返回类型 encoding 数据格式更改
        :param url:
        :param method: 默认get 小写即可
        :param h2: 是否切换h2模式请求
        :param encoding: 调整响应格式
        :param proxies: 代理
        :param headers: 请求头
        :param cookies: cookie
        :param params: 参数
        :param json: payload
        :param data: payload
        :param timeout: 超时
        :param verify: 认证
        """
        pass

    async def async_send(self, url,
                         *,
                         method: Literal['get', 'post'] = 'get',
                         h2: bool = False,
                         encoding: str = None,
                         proxies: Union[dict, str] = None,
                         headers: dict = None,
                         cookies: dict = None,
                         params: dict = None,
                         json: dict = None,
                         data: Union[dict, str, tuple] = None,
                         timeout: Union[int, float] = 3,
                         verify: bool = None,
                         **kwargs):
        # 异步的部分下次再弄
        pass

    def _cal_ret(self, resp, ret):
        pass

    async def _async_cal_ret(self, resp, ret):
        pass
