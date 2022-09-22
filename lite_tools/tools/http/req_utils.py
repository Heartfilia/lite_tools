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
import httpx
import requests

from typing import Literal, Union, TypeVar, Mapping

T = TypeVar('T')


class LiteResponse:
    status_code: int = 200
    response: ...
    decode: str = 'requests'
    headers: requests.Response.headers
    history: requests.Response.history


class LiteRequest(object):
    def __init__(self, retry: int = 5):
        self.retry = retry

    def send(self,
             url,
             method: Literal['get', 'post'] = 'get',  # request, head, patch, put, delete, options这些不搞
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

    async def async_send(self,
                         url,
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
