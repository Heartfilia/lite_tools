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
import re
import sys
import traceback

from loguru import logger


def my_logger(file_root, log_function, log_line, message, log_level="error"):
    """
    因为是我自己用 我只用 warning 和 error 和 debug
    :param file_root:     日志报错路径
    :param log_function:  函数名称
    :param log_line:      报错行数
    :param message:       需要输出的信息
    :param log_level:     日志等级
    """
    fmt_str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>" + str(file_root) +"</cyan>:<cyan>[" + str(log_function) +"]</cyan>:<cyan>" + str(log_line) + "</cyan> - <level>{message}</level>"
    logger.remove()
    ctx = logger.add(
        sys.stderr,
        level="INFO",
        colorize=True,
        format=fmt_str
    )
    if log_level.lower() == 'error':
        logger.error(message)
    elif log_level.lower() == "debug":
        logger.debug(message)
    else:
        logger.warning(message)
    # 复原系统自带的状态
    try:
        logger.remove(ctx)
    except Exception:
        pass
    finally:
        logger.add(sys.stderr)   # stderr 直接输出  stdout遇到换行才输出 有个缓冲区


def handle_exception(traceback_format_info: str, function_name: str):
    """
    这里传入 traceback.format_exc() 就好了
    :param traceback_format_info : traceback.format_exc()
    :param function_name: 当前传入函数.__name__
    :return --> 报错行，报错文件路径，报错类型，报错详细介绍
    """
    results = traceback_format_info.split('\n')
    line = fl = ''
    for item in results[::-1]:
        if function_name in item:
            line = "".join(re.findall(r'line (\d+)', item))
            fl = ''.join(re.findall(r'File "(.*)",', item))
            break
    exception_type = results[-2]
    exception_detail = results[-3].strip()
    return line, fl, exception_type, exception_detail


def get_using_line_info(limit: int = 7):
    """
    这里只是读取栈信息
    """
    try:
        tb_data = traceback.format_stack(limit=limit)
        strings = "".join(tb_data).split('\n')[0]
        line = "".join(re.findall(r'line (\d+)', strings))
        fl = ''.join(re.findall(r'File "(.*)"', strings))
        return line, fl
    except Exception as err:
        _ = err
        return "", ""
