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
# import time
# import asyncio
# import threading
# from typing import Union
# from functools import wraps
# from asyncio import iscoroutinefunction
#
# from func_timeout import func_set_timeout, FunctionTimedOut
#
# from lite_tools.exceptions.TimeExceptions import HttpXTimeOutError


# def x_timeout(seconds: Union[int, float], error_message: str = 'Timed Out'):
#     """
#     TODO(还没有搞定 测试单个进程没啥问题 但是没有用 因为程序都是多线程)
#     """
#     raise HttpXTimeOutError("现在没有搞好")
#     def decorated(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 return func_set_timeout(seconds)
#             except FunctionTimedOut:
#                 raise HttpXTimeOutError(error_message)
#
#         @wraps(func)
#         async def async_wrapper(*args, **kwargs):
#             try:
#                 return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
#             except KeyboardInterrupt:
#                 exit(0)
#             except Exception as err:
#                 _ = err
#                 raise HttpXTimeOutError(error_message)
#
#         return async_wrapper if iscoroutinefunction(func) else wrapper
#
#     return decorated
