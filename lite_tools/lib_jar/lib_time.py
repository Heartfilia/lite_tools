# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:27
# @Author : Lodge
import time
import functools
from typing import Union
from inspect import currentframe

from lite_tools.utils_jar.logs import my_logger, get_using_line_info


"""
这里可以用 但是比较臃肿 
后续将重构
"""

__ALL__ = ['get_date', 'get_time']


def get_date(timedelta: tuple = None):
    """
    这里是为了将get_time里面关于日期操作的独立出来 可以独立调用也可以由get_time调用
    # datetime模块太复杂了 还需要考虑一下怎么合并处理 先不给用这个模块
    """
    pass


def get_time(goal=None, fmt: Union[bool, str] = False, double=False, cursor=None, *args, **kwargs):
    """
    TODO(my_logger 的路径有问题)
    返回时间的数值(整数) 或者 格式化好了的数据 优先级 goal > fmt > double = cursor
    params goal: 传入准确的时间戳 最好十位 额外可以设置的参数有 double fmt 如果需要把格式化时间转换为数字需要设置double=True, fmt设置为对应的格式
    params fmt : 返回格式化后的数据 True/False 默认%Y-%m-%d %H:%M:%S格式 传入其它格式按照其它格式转换 TODO(会自动匹配时间)
    params double: 返回小数的时间 还是整数 默认整数  如果搭配goal那么返回浮点数 因为是要把字符串转换为数字来着
    params cursor: 传入游标单位/天  可以是正可以是负 可以是整数可以是字符串 TODO(后续会增加更细的游标设置)
    """
    if isinstance(fmt, bool):
        fmt_str = "%Y-%m-%d %H:%M:%S"
    else:
        fmt_str = fmt

    if goal and double:
        try:
            sure_time = time.mktime(time.strptime(goal, fmt_str))
            return sure_time
        except Exception as e:
            _, fl = get_using_line_info()
            line = str(currentframe().f_back.f_lineno)
            my_logger(fl, "get_time", line, f"请输入正确的[ fmt ]格式: {e}")
            return -1
    elif goal and not double:
        if isinstance(goal, int):
            str_time = str(goal)
            limit_len_time = str_time[:10]
            int_time = int(f"{limit_len_time:<010}")
        else:
            if goal.isdigit():
                limit_len_time = goal[:10]
                int_time = int(f"{limit_len_time:<010}")
            else:
                _, fl = get_using_line_info()
                line = str(currentframe().f_back.f_lineno)
                my_logger(fl, "get_time", line, f"请输入正确的[ goal ]:传入的是非数字类型的则会默认当前时间的格式化样式")
                int_time = int(time.time())
        return time.strftime(fmt_str, time.localtime(int_time))
    else:
        if fmt and not cursor:
            return time.strftime(fmt_str)
        elif fmt and cursor:
            result = _get_time_block(cursor)
            if isinstance(result, int) or isinstance(result, float):
                return time.strftime(fmt_str, time.localtime(result))
            else:
                return result
        elif not fmt and cursor:
            result = _get_time_block(cursor)
            if double:
                return result
            else:
                return int(result)
        time_now = time.time()
        if double:
            return time_now
        else:
            return int(time_now)


def _get_time_block(cursor):
    if isinstance(cursor, int) or isinstance(cursor, float):
        tm_before = time.time() + cursor * 86400
    elif isinstance(cursor, str):
        if "-" in cursor:
            cursor_now = cursor.replace('-', '')
            if cursor_now.isdigit():
                tm_before = time.time() - int(cursor_now) * 86400
            else:
                return "请输入正确的时间"
        elif cursor.isdigit():
            tm_before = time.time() + int(cursor) * 86400
        else:
            return "请输入正确的时间"
    else:
        return "请输入正确的时间"
    return tm_before


def timec(fn):  # time count
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        t1 = time.time()
        bk = fn(*args, **kwargs)
        _, fl = get_using_line_info(limit=8)
        line = str(currentframe().f_back.f_lineno)
        my_logger(fl, fn.__name__, line, f' Time consuming: {time.time()-t1:.5f}', log_level='debug')
        return bk
    return inner
