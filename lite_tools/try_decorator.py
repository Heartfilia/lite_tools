import re
import asyncio
import warnings
import traceback
from functools import wraps, partial
from asyncio import iscoroutinefunction

from loguru import logger


warnings.filterwarnings('ignore', category=RuntimeWarning)


def try_catch(func=None, *, log=True, catch=False):
    if func is None:
        return partial(try_catch, log=log, catch=catch)

    def __judge__iscoroutine(function):
        try:
            return iscoroutinefunction(function)
        except Exception:
            return False

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

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            if log is True:   
                line, fl, exception_type, exception_detail = __handle_exception()
                if catch is True:
                    logger.opt(exception=True, colors=True, capture=True).error("More Informations: ↓↓↓")
                else:
                    logger.error(f"[{func.__name__}] lineo.{line} -> {fl} - {exception_type}: {exception_detail}")
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            if log is True:   
                line, fl, exception_type, exception_detail = __handle_exception()
                if catch is True:
                    logger.opt(exception=True, colors=True, capture=True).error("More Informations: ↓↓↓")
                else:
                    logger.error(f"[{func.__name__}] lineo.{line} -> {fl} - {exception_type}: {exception_detail}")
    
    if __judge__iscoroutine(func):
        return async_wrapper
    else:
        return wrapper
