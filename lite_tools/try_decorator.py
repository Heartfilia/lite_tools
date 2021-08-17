import re
import traceback
from loguru import logger
from functools import wraps, partial


# 这个东西还需要调试一下 还不对外开放使用
def async_try_catch(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            results = traceback.format_exc().split('\n')
            line = fl = '/'
            for item in results[::-1]:
                if func.__name__ in item:
                    line = "".join(re.findall(r'line (\d+)', item))
                    fl = ''.join(re.findall(r'File "(.*)"', item))
                    break
            logger.error(f"[{func.__name__}] lineo.{line} -> {fl} - {results[-2]}: {results[-3].strip()}")
    return wrapper


def try_catch(func=None, *, log=True, catch=False):
    """
    捕获异常的 默认是会打印日志
    使用方式如下
    @try_catch
    def test(): ...

    @try_catch(log=False)
    def test(): ...

    @try_catch(catch=True)
    def test(): ...
    """
    if func is None:
        return partial(try_catch, log=log, catch=catch)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            if log is True:   
                results = traceback.format_exc().split('\n')
                line = fl = '/'
                for item in results[::-1]:
                    if func.__name__ in item:
                        line = "".join(re.findall(r'line (\d+)', item))
                        fl = ''.join(re.findall(r'File "(.*)"', item))
                        break
                if catch is True:
                    logger.opt(exception=True, colors=True, capture=True).error("Error Informations: ↓↓↓")
                else:
                    logger.error(f"[{func.__name__}] lineo.{line} -> {fl} - {results[-2]}: {results[-3].strip()}")
    return wrapper
