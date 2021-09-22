# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:27
# @Author : Lodge
import time
import functools
from loguru import logger

"""
这里可以用 但是比较臃肿 
后续将重构
"""


def get_time(goal=None, fmt=False, double=False, cursor=None, fmt_str="%Y-%m-%d %H:%M:%S"):
    """
    返回时间的数值(整数) 或者 格式化好了的数据 优先级 goal > fmt > double = cursor
    params goal: 传入准确的时间戳 最好十位 额外可以设置的参数有 double fmt_str 如果需要把格式化时间转换为数字需要设置double=True, fmt_str设置为对应的格式
    params fmt : 返回格式化后的数据  True/False
    params double: 返回小数的时间 还是整数 默认整数  如果搭配goal那么返回浮点数 因为是要把字符串转换为数字来着
    params cursor: 传入游标单位/天  可以是正可以是负 可以是整数可以是字符串
    params fmt_str: 默认%Y-%m-%d %H:%M:%S格式 可以自定义输出样式 如果搭配goal+double=True+fmt_str 则表示处理对应格式的字符串对象
    """
    if goal and double:
        try:
            sure_time = time.mktime(time.strptime(goal, fmt_str))
            return sure_time
        except Exception as e:
            logger.error(f"请输入正确的[ fmt_str ]格式，错误为:{e}")
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
                logger.error("请输入正确的内容:传入的是非数字类型的则会默认当前时间的格式化样式")
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
        logger.debug(f'>>> [{fn.__name__}] -- cost time:{time.time()-t1:.5f}')
        return bk
    return inner
