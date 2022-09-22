import traceback
from typing import Union, Callable, TypeVar
from functools import wraps, partial
from asyncio import iscoroutinefunction

from lite_tools.tools.utils.logs import my_logger, logger, handle_exception


__ALL__ = ["try_catch"]


T = TypeVar('T')


def try_catch(func=None, *,
              default: T = None, log: Union[bool, str] = True, catch: bool = False,
              err_callback: Callable = None, err_args: tuple = None):
    """
    异常捕获装饰器
    -->不加参数 就是把异常捕获了 返回None
    -->加了参数==参数如下:
    :param func        :
    :param default     : 默认的返回值
    :param log         : 是否打印报错信息,默认是打印的(如果传入指定的内容 那么就会报错指定内容)
    :param catch       : 按栈方式捕获异常
    :param err_callback: 当出现错误的时候调用的回调函数,只需要传入方法名即可
    :param err_args    : 如果有参数请用元组方式传进来 这里需要结合你自己的err_callback 参考见demo
    """
    if func is None:
        return partial(try_catch, default=default, log=log, catch=catch, err_callback=err_callback, err_args=err_args)
    
    def __log_true():
        line, fl, exception_type, exception_detail = handle_exception(traceback.format_exc(), func.__name__)
        if err_callback is not None:
            try:
                if isinstance(err_args, tuple):
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
            my_logger(fl, func.__name__, line, f"{exception_type} --> {exception_detail}")

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print()
            exit(0)
        except Exception as err:
            _ = err
            if log:
                __log_true()
            return default
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyboardInterrupt:
            print()
            exit(0)
        except Exception as err:
            _ = err
            if log:
                __log_true()
            return default
    
    return async_wrapper if iscoroutinefunction(func) else wrapper
