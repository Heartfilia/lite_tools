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
import time
import asyncio
import threading
from typing import Union
from functools import wraps
from asyncio import iscoroutinefunction

from lite_tools.exceptions.TimeExceptions import HttpXTimeOutError


def x_timeout(seconds: Union[int, float], error_message: str = 'HttpX Timed Out'):
    """
    TODO(还没有搞定 测试单个进程没啥问题 但是没有用 因为程序都是多线程)
    """
    def decorated(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                th_func = MyThread(target=func, args=args)
                th_func.setDaemon(True)
                th_func.start()
                sleep_num = int(seconds // 0.5)
                for i in range(0, sleep_num):
                    info = th_func.get_result()
                    if info:
                        return info
                    else:
                        time.sleep(0.5)
            except Exception as err:
                _ = err
                raise HttpXTimeOutError(error_message)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except KeyboardInterrupt:
                exit(0)
            except Exception as err:
                _ = err
                raise HttpXTimeOutError(error_message)

        return async_wrapper if iscoroutinefunction(func) else wrapper

    return decorated


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        """
            因为threading类没有返回值,因此在此处重新定义MyThread类,使线程拥有返回值
        """
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        # 接受返回值
        self.result = self.func(*self.args)

    def get_result(self):
        # 线程不结束,返回值为None
        try:
            return self.result
        except Exception:
            return None
