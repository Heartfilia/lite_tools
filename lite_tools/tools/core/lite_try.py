import time
import asyncio
import traceback
from typing import Callable, TypeVar, List, Union, Sequence
from functools import wraps, partial
from asyncio import iscoroutinefunction

from lite_tools.tools.utils.logs import my_logger as try_log
from lite_tools.tools.utils.logs import logger, handle_exception

__ALL__ = ["try_catch"]


T = TypeVar('T')


class BaseRetryException(Exception):
    def __init__(self):
        pass


def combine_retry(exc: Union[List[Exception], Exception, type]) -> T:
    if isinstance(exc, tuple):
        not_retry_exception = exc
    elif isinstance(exc, (list, set)):
        not_retry_exception = tuple(exc)
    elif issubclass(exc, Exception):
        not_retry_exception = exc
    else:
        not_retry_exception = BaseRetryException

    return not_retry_exception


def try_catch(
        func=None, *,
        retry: int = 1,
        except_retry: Union[List[Exception], Exception, type] = BaseRetryException,
        ignore_retry: Union[List[Exception], Exception, type] = BaseRetryException,
        default: T = None, log: Union[bool, str] = True, catch: bool = False, timeout: Union[int, float] = None,
        err_callback: Callable = None, err_args: Sequence = None):
    """
    异常捕获装饰器
    -->不加参数 就是把异常捕获了 返回None
    -->加了参数==参数如下:
    :param func        :
    :param retry       : 重试次数
    :param timeout     : 重试的时候加的休眠时间
    :param except_retry: 如果有这种异常那么就不重试 直接返回默认值 这里如果写Exception 那么就会忽略所有异常不进行重试直接返回默认值
    :param ignore_retry: 如果有这种异常 就继续重试
    :param default     : 默认的返回值
    :param log         : 是否打印报错信息,默认是打印的(如果传入指定的内容 那么就会报错指定内容)
    :param catch       : 按栈方式捕获异常
    :param err_callback: 当出现错误的时候调用的回调函数,只需要传入方法名即可
    :param err_args    : 如果有参数请用序列方式传入,要结合你自己的err_callback参数,无参数也可以 参考见demo
    """
    if func is None:
        return partial(
            try_catch, retry=retry, except_retry=except_retry, default=default, log=log, catch=catch, timeout=timeout,
            err_callback=err_callback, err_args=err_args
        )

    not_retry_exception = combine_retry(except_retry)
    continue_exception = combine_retry(ignore_retry)
    
    def __log_true(last: bool = False):
        """
        :param last: 如果是最后一次重试才会打印日志
        """
        line, fl, exception_type, exception_detail = handle_exception(traceback.format_exc(), func.__name__)
        if err_callback is not None and last is True:
            try:
                if isinstance(err_args, (tuple, list, set, dict)):
                    err_callback(*err_args)
                else:
                    err_callback()
            except Exception as err:
                if log is True:
                    logger.error(f"传入的回调函数不存在或者报错: {err}")

        if catch is True:
            logger.opt(exception=True, colors=True, capture=True).error("Information: ↓ ↓ ↓ ")
        elif log and isinstance(log, str):
            logger.error(log)
        else:
            try_log(fl, func.__name__, line, f"{exception_type} --> {exception_detail}")

    @wraps(func)
    def wrapper(*args, **kwargs):
        for ind in range(retry):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                print()
                exit(0)
            except not_retry_exception:
                break
            except continue_exception:
                continue
            except Exception as err:
                _ = err
                if log:
                    __log_true(True if retry-1 == ind else False)
                if timeout is not None and isinstance(timeout, (int, float)):
                    time.sleep(timeout)
                continue

        return default
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        for ind in range(retry):
            try:
                return await func(*args, **kwargs)
            except KeyboardInterrupt:
                print()
                exit(0)
            except not_retry_exception:
                break
            except continue_exception:
                continue
            except Exception as err:
                _ = err
                if log:
                    __log_true(True if retry-1 == ind else False)
                if timeout is not None and isinstance(timeout, (int, float)):
                    await asyncio.sleep(timeout)
                continue

        return default
    
    return async_wrapper if iscoroutinefunction(func) else wrapper
