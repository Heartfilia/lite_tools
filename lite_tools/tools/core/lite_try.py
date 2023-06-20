import time
import asyncio
import traceback
from typing import Callable, TypeVar, List, Union, Sequence
from functools import wraps, partial
from asyncio import iscoroutinefunction

from lite_tools.logs import my_logger as try_log
from lite_tools.logs import logger, handle_exception

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


def get_params_args(params):
    if isinstance(params[0], int):  # (1, 2)  这种格式的
        for item in params:
            if not isinstance(item, int):
                return []
        return params
    if isinstance(params[0], list):  # ([1, 23], ["e"])  # 这格式的
        for item in params[0]:
            if not isinstance(item, int):
                return []
        return params[0]
    return []


def get_params_kwargs(params):
    if isinstance(params[0], str):  # ("data", "args")  这种格式的
        for item in params:
            if not isinstance(item, str):
                return []
        return params
    if isinstance(params[1], list):  # ([1, 23], ["e"])  # 这格式的
        for item in params[1]:
            if not isinstance(item, str):
                return []
        return params[1]
    return []


def try_catch(
        func=None, *,
        retry: int = 1,
        except_retry: Union[List[Exception], Exception, type] = BaseRetryException,
        ignore_retry: Union[List[Exception], Exception, type] = BaseRetryException,
        default: T = None, log: Union[bool, str] = True, catch: bool = False, timeout: Union[int, float] = None,
        err_callback: Callable = None, err_args: Sequence = None, err_params: T = None):
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
    :param err_params  : 这个和 err_args 二选一参数两者不同的区别在于 args是自己方法的自己的参数, params是装饰函数的参数
        优先级是 err_args > err_params 也就是如果写了args参数那么将不会提取err_params的参数
                       > 如何取值:
    """
    if func is None:
        return partial(
            try_catch, retry=retry, except_retry=except_retry, default=default, log=log, catch=catch, timeout=timeout,
            err_callback=err_callback, err_args=err_args, err_params=err_params
        )

    not_retry_exception = combine_retry(except_retry)
    continue_exception = combine_retry(ignore_retry)
    
    def __log_true(last: bool = False, *args, **kwargs):
        """
        :param last: 如果是最后一次重试才会打印日志
        """
        line, fl, exception_type, exception_detail = handle_exception(traceback.format_exc(), func.__name__)
        if err_callback is not None and last is True:
            try:
                if isinstance(err_args, (tuple, list, set, dict)):
                    err_callback(*err_args)
                else:
                    if err_params is None:
                        err_callback()
                    else:
                        # 到这里了 err_params 是一定有内容的
                        function_args = args[0]
                        function_kwargs = args[1]
                        send_args = ()
                        if function_args:
                            send_args = get_params_args(err_params)  # [1, 3]  返回这种格式的
                        send_kwargs = ()
                        if function_kwargs:
                            send_kwargs = get_params_kwargs(err_params)

                        cache_args = []
                        for a in send_args:
                            if a >= len(args[0]):
                                continue
                            cache_args.append(args[0][a])

                        cache_kwargs = {}
                        for k in send_kwargs:
                            cache_kwargs[k] = args[1].get(k)

                        try:
                            err_callback(*cache_args, **cache_kwargs)
                        except Exception as err:
                            if log is True:
                                logger.error(f"""[{err.__traceback__.tb_lineno}] 参数有问题,这里建议的参数设置方案如下:
        def 被装饰函数(a, b, c=None, d=None): |   def 回调函数(x, c=666):
            pass                            |        pass
        首先被装饰函数 a, b 是位置传参 那么我们建议是:  
            @try_catch(..., err_params=([1], ["c"])) 这里意思就是 
                位置参数取 b -赋值给回调函数-> x
                命名传递的参数 那么回调函数也得同名并且 参数位置第二个列表里面写的键是沟通两个函数的所以命名得一样
        如果只需要取值位置参数 或者 命名传递,只需要传需要传的就行了 如:
            @try_catch(..., err_params=(0, 1))  | @try_catch(..., err_params=("c",))
        如果被装饰是命名传参,那么这个回调函数的参数也得设置为命名 如上c,d  调用被装饰函数的时候如果用位置传参那么命名将取不到值 如 被装饰函数(a, b, c) 没有用 被装饰函数(a, b, c=c)
        如果被装饰函数全部传入的是位置传参,那么位置对应好即可  如 被装饰函数(a, b, c)  不要用c=c  这样子 回调函数哪里参数可以直接写 err_params=(0, 1, 2)
    原理是根据你调用函数是怎么传参的 传入的参数示例: (('aaa', 'bbbb', 'ccccc'), {{'d': 888, 'e': 666}})  位置传参映射第一部分 命名传参映射第二部分
""")
            except Exception as err:
                if log is True:
                    logger.error(f"[{err.__traceback__.tb_lineno}] 传入的回调函数不存在或者报错: {err}")

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
                    __log_true(True if retry-1 == ind else False, args, kwargs)
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
                    __log_true(True if retry-1 == ind else False, args, kwargs)
                if timeout is not None and isinstance(timeout, (int, float)):
                    await asyncio.sleep(timeout)
                continue

        return default
    
    return async_wrapper if iscoroutinefunction(func) else wrapper
