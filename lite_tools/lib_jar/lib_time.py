# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:27
# @Author : Lodge
import re
import time
import functools
from typing import Union
from inspect import currentframe

from lite_tools.utils_jar.logs import my_logger, get_using_line_info, logger
from lite_tools.lib_jar.lib_matchcase import match_case
from lite_tools.utils_jar.u_re_time import DATETIME_PATTERN


"""
这里可以用 但是比较臃肿 
TODO(my_logger 在多线程中的路径有问题 -- 我也懒得修复 这个是个小问题)
"""

__ALL__ = ['get_date', 'get_time', 'time_count']


def get_date(timedelta: tuple = None):
    """
    这里是为了将get_time里面关于日期操作的独立出来 可以独立调用也可以由get_time调用
    # datetime模块太复杂了 还需要考虑一下怎么合并处理 先不给用这个模块
    """
    _ = timedelta
    pass


def get_time(goal: Union[str, int, float, None] = None, fmt: Union[bool, str] = False, unit: str = "s",
             double: bool = False, cursor: Union[str, int, float, None] = None):
    """
    返回时间的数值(整数) 或者 格式化好了的数据 优先级 goal > fmt > double = cursor
    params goal: 传入准确的时间戳 最好十位 额外可以设置的参数有 double fmt 如果需要把格式化时间转换为数字需要设置double=True, fmt设置为对应的格式
    params fmt : 返回格式化后的数据 True/False 默认%Y-%m-%d %H:%M:%S格式 传入其它格式按照其它格式转换
    params unit : 单位默认s/秒 还仅支持 ms/毫秒  这个数据默认取整
    params double: 返回小数的时间 还是整数 默认整数  如果搭配goal那么返回浮点数 因为是要把字符串转换为数字来着
    params cursor: 默认传入游标单位/天  可以是正可以是负 可以是整数可以是字符串 注意是有大小写区别的
                   更多的参数: Y:年 m:月 d:日 H:时 M:分 S:秒 （同时间那边的参数格式）如 cursor="-2Y"  如果写一堆 取最大的
                   不要写一堆时间符号说 一年三个月5天前这种:只推荐 单命令 如前面就只会提取最大的一年前进行处理
    params args  : 兼容不重要参数
    params kwargs: 兼容不重要参数
    """
    if isinstance(fmt, bool):
        fmt_str = _guess_fmt(goal)
        if not fmt_str:
            fmt_str = "%Y-%m-%d %H:%M:%S"
    else:
        fmt_str = fmt
    times = _get_unit_times(unit)

    if goal and double:
        return _fmt_to_timestamp(goal, fmt_str, times)
    elif goal and not double:
        return _timestamp_to_f_time(goal, fmt_str)
    else:
        if fmt and not cursor:
            return time.strftime(fmt_str)
        elif fmt and cursor:
            return _cursor_to_f_time(cursor, fmt_str)
        elif not fmt and cursor:
            return _cursor_to_timestamp(double, cursor, times)
        else:
            return _default_now_time(double, times)


def _get_unit_times(unit):
    """
    获取需要补充的倍数
    :param unit:
    :return:
    """
    if unit == "ms":
        times = 1000
    else:
        times = 1
    return times


def _default_now_time(double, times):
    """
    默认输出--当前时间，是否要浮点数
    """
    time_now = time.time()
    if double:
        return time_now * times
    else:
        return int(time_now * times)


def _cursor_to_timestamp(double, cursor, times):
    """
    通过游标时间输出时间戳
    """
    result = _get_time_block(cursor)
    if double:
        return result * times
    else:
        return int(result * times)


def _cursor_to_f_time(cursor, fmt_str):
    """
    通过游标时间输出格式化字符串
    """
    result = _get_time_block(cursor)
    if isinstance(result, int) or isinstance(result, float):
        return time.strftime(fmt_str, time.localtime(result))
    else:
        return result


def _timestamp_to_f_time(goal, fmt_str):
    """
    时间戳转换为格式化时间: 支持数字或者字符串时间戳 支持10或者13位数
    """
    if isinstance(goal, (int, float)):
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


def _fmt_to_timestamp(goal, fmt_str, times):
    """
    时间串转换为时间戳
    """
    try:
        sure_time = time.mktime(time.strptime(goal, fmt_str)) * times
        return sure_time
    except Exception as e:
        _, fl = get_using_line_info()
        line = str(currentframe().f_back.f_lineno)
        my_logger(fl, "get_time", line, f"请输入正确的[ fmt ]格式: {e}")
        return -1


def _guess_fmt(string):
    """
    当默认传入的fmt为True或者False的时候，这里预测fmt的格式
    TODO(会自动匹配时间)
    """
    _ = string
    from dateutil.parser import parse
    from dateparser import parse
    return ""


@match_case
def different_mode(_, *args):
    return 86400


@different_mode.register("Y")
def handle_year(_, *args):
    """
    一年按照 365 天算
    """
    cursor = args[0]
    return int(cursor) * 86400 * 365


@different_mode.register("m")
def handle_month(_, *args):
    """
    一月按照 30 天算
    """
    cursor = args[0]
    return int(cursor) * 86400 * 30


@different_mode.register("d")
def handle_day(_, *args):
    cursor = args[0]
    return int(cursor) * 86400


@different_mode.register("H")
def handle_hour(_, *args):
    cursor = args[0]
    return int(cursor) * 3600


@different_mode.register("M")
def handle_minutes(_, *args):
    cursor = args[0]
    return int(cursor) * 60


@different_mode.register("S")
def handle_second(_, *args):
    cursor = args[0]
    return int(cursor)


def _get_offset(cursor: Union[str, int, float]) -> Union[int, float]:
    """
    通过传入的游标标志位 来判断时间
    从年月日到时分秒 优先级从上到下 也就是 如果一句话中出现多种状态 那么只取最大
    """
    offset = 0
    if isinstance(cursor, (int, float)):
        # 如果直接传数字 就按照天处理
        offset = cursor * 86400
    elif isinstance(cursor, str):
        level_year = re.search(r"(-?\d+\.?\d*)(Y)", cursor)
        level_month = re.search(r"(-?\d+\.?\d*)(m)", cursor)
        level_day = re.search(r"(-?\d+\.?\d*)(d)", cursor)
        level_hour = re.search(r"(-?\d+\.?\d*)(H)", cursor)
        level_minute = re.search(r"(-?\d+\.?\d*)(M)", cursor)
        level_second = re.search(r"(-?\d+\.?\d*)(S)", cursor)
        item = level_year or level_month or level_day or level_hour or level_minute or level_second
        if item:
            offset = different_mode(item.group(2), item.group(1))
    return offset


def _get_time_block(cursor):
    """
    处理游标时间：默认的不带任何标记的数据传入进来是 天
    更多的参数: Y:年 m:月 d:日 H:时 M:分 S:秒
    """
    offset = _get_offset(cursor)
    return time.time() + offset


class TimeMaker(object):
    def __init__(self):
        """
        TODO 将会在这里处理时间的模式 第一版先提供给`get_time`使用 后续做成通用模块  当前主要是转换成时间戳
        """
        self.base_time = ""
        self.base_template = "1970-01-01 00:00:00"
        self.little_day_info = [("一", 1), ("二", 2), ("三", 3), ("四", 4), ("五", 5),
                                ("六", 6), ("七", 7), ("八", 8), ("九", 9), ("十", 10)]
        # 下面这个主要是记录月份的特殊情况 只弄了 中英法德俄 语言
        self.month_info = {
            "01": ("Jan", "January", "一月", "janvier", "Januar", "январь"),
            "02": ("Feb", "February", "二月", "février", "Februar", "февраль"),
            "03": ("Mar", "March", "三月", "mars", "Marsch", "Март"),
            "04": ("Apr", "April", "四月", "avril", "April", "апреля"),
            "05": ("May", "May", "五月", "Mai", "Dürfen", "май"),
            "06": ("Jun", "June", "六月", "juin", "Juni", "июнь"),
            "07": ("Jul", "July", "七月", "juillet", "Juli", "июль"),
            "08": ("Aug", "August", "八月", "août", "August", "август"),
            "09": ("Sep", "September", "九月", "septembre", "September", "сентябрь"),
            "10": ("Oct", "October", "十月", "octobre", "Oktober", "Октябрь"),
            "11": ("Nov", "November", "十一月", "novembre", "November", "ноябрь"),
            "12": ("Dec", "December", "十二月", "décembre", "Dezember", "Декабрь"),
        }

    def make(self, fmt_time: str = None) -> Union[int, float]:
        """
        传入需要转换的时间格式
        :param fmt_time:
        :return:
        """
        if fmt_time is None or not fmt_time or not isinstance(fmt_time, str):
            logger.warning("因为没有传入规定格式化时间,现在返回的结果是 --> 0")
            return 0
        self.base_time = fmt_time

        cursor_time = self._handle_chinese_cursor_time()
        if cursor_time is False:
            info = self._handle_chinese_format_time()
            return info

    def _handle_chinese_format_time(self):
        for pattern, result_rules in DATETIME_PATTERN.items():
            aim_at = re.search(pattern, self.base_time)
            if aim_at:
                rule_len = len(result_rules)
                print(rule_len)
                print(aim_at)
                result = aim_at.group(1)
                return result
        return False

    def _handle_chinese_cursor_time(self):
        # 处理中文的位移量的时间形式 不搞英文的 因为英文的太难写了
        if "前" in self.base_time:
            if "秒" in self.base_time:
                wait = re.search(r"(\d+)\s*秒", self.base_time)
                cursor = 1
            elif "分" in self.base_time:
                wait = re.search(r"(\d+)\s*分", self.base_time)
                cursor = 60
            elif "时" in self.base_time:
                wait = re.search(r"(\d+)\s*个?小时", self.base_time)
                cursor = 3600
            elif "周" in self.base_time or "星期" in self.base_time:
                wait = re.search(r"(\d+)\s*周", self.base_time) or re.search(r"(\d+)\s*个?星期", self.base_time)
                cursor = 3600 * 7
            elif "天" in self.base_time:
                # 处理十天内的中文字符问题

                wait = re.search(r"(\d+)\s*天", self.base_time)
                cursor = 86400
            elif "月" in self.base_time:
                wait = re.search(r"(\d+)\s*个?月", self.base_time)
                cursor = 86400 * 30
            elif "年" in self.base_time:
                wait = re.search(r"(\d+)\s*年", self.base_time)
                cursor = 86400 * 365
            else:
                return False

            if wait:
                return time.time() - int(wait.group(1)) * cursor

        return False


def time_count(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        t1 = time.time()
        bk = fn(*args, **kwargs)
        logger.debug(f'[{fn.__name__}] Time consuming: {time.time()-t1:.3f}')
        return bk
    return inner


if __name__ == "__main__":
    t = time.time()
    a = TimeMaker()
    print(a.make("2012.2.15 3时20分"))
    print(time.time() - t)
