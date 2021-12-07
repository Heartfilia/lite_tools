import re
import traceback
from functools import wraps, partial
from asyncio import iscoroutinefunction
from loguru import logger


__ALL__ = ["try_catch"]


def try_catch(func=None, *, default=None, log=True, catch=False, err_callback=None, err_args: tuple = None):
    """
    异常捕获装饰器
    -->不加参数 就是把异常捕获了 返回None
    -->加了参数==参数如下:
    :param func        :
    :param default     : 默认的返回值
    :param log         : 是否打印报错信息,默认是打印的
    :param catch       : 按栈方式捕获异常
    :param err_callback: 当出现错误的时候调用的回调函数,只需要传入方法名即可
    :param err_args    : 如果有参数请用元组方式传进来 这里需要结合你自己的err_callback 参考见demo
    """
    if func is None:
        return partial(try_catch, default=default, log=log, catch=catch, err_callback=err_callback)

    def __handle_exception():
        results = traceback.format_exc().split('\n')
        line = fl = '/'
        for item in results[::-1]:
            if func.__name__ in item:
                line = "".join(re.findall(r'line (\d+)', item))
                fl = ''.join(re.findall(r'File "(.*)"', item))
                break
        exception_type = results[-2]
        exception_detail = results[-3].strip()
        return line, fl, exception_type, exception_detail
    
    def __log_true():
        line, fl, exception_type, exception_detail = __handle_exception()
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
        else:
            logger.error(f"[{func.__name__}] lineNo.{line} -> {fl} - {exception_type}: {exception_detail}")

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            exit(0)
        except Exception:
            if log is True: __log_true()
            return default
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyboardInterrupt:
            exit(0)
        except Exception:
            if log is True: __log_true()  
            return default
    
    return async_wrapper if iscoroutinefunction(func) else wrapper
