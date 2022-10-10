# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:27
# @Author : Lodge
import re
import time
import calendar
import functools
from typing import Union, Literal, Tuple
# from inspect import currentframe

from lite_tools.tools.utils.logs import logger
from lite_tools.tools.core.lite_match import match_case
from lite_tools.tools.utils.u_re_time import DATETIME_PATTERN
from lite_tools.exceptions.TimeExceptions import TimeFormatException, ErrorTimeRange

"""
这里可以用 但是比较臃肿 暂时不支持 年月日通过游标操作获得年月日 可以实现 但是不知道参数取名和其他的冲突问题
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


def get_time(goal: Union[str, int, float, None] = None, fmt: Union[bool, str] = False, unit: Literal["ms", "s"] = "s",
             instance: Union[None, type] = None, cursor: Union[str, int, float] = 0, **kwargs):
    """
    返回时间的数值(整数) 或者 格式化好了的数据 优先级 goal > fmt > double = cursor
    params goal: 传入准确的时间戳 最好十位 额外可以设置的参数有 double fmt 如果需要把格式化时间转换为数字需要设置double=True, fmt设置为对应的格式
    params fmt : 返回格式化后的数据 True/False 默认%Y-%m-%d %H:%M:%S格式 传入其它格式按照其它格式转换
    params unit : 单位默认s/秒 还仅支持 ms/毫秒  这个数据默认取整 --> 可以设置 unit="ms/int" 对double后的结果取整
    params instance: 写 int/float 即可按照int或者float返回数据
    params cursor: 默认传入游标单位/天  可以是正可以是负 可以是整数可以是字符串 注意是有大小写区别的
                   更多的参数: Y:年 m:月 d:日 H:时 M:分 S:秒 （同时间那边的参数格式）如 cursor="-2Y"  如果写一堆 取最大的
                   不要写一堆时间符号说 一年三个月5天前这种:只推荐 单命令 如前面就只会提取最大的一年前进行处理
    params args  : 兼容不重要参数
    params kwargs: 兼容不重要参数
    """
    if isinstance(fmt, bool) and isinstance(goal, str):
        fmt_str = _guess_fmt(goal)
        if not fmt_str:
            fmt_str = "%Y-%m-%d %H:%M:%S"
    elif not isinstance(goal, str) and fmt is True:
        fmt_str = "%Y-%m-%d %H:%M:%S"
    else:
        fmt_str = fmt
    times = _get_unit_times(unit)
    if kwargs.get('double') is True:
        instance = float

    if instance is not None and instance not in [int, float]:
        instance = int
    if not isinstance(goal, str) and fmt is False:
        return _cal_cursor_timestamp(goal, times, instance, cursor)
    elif goal and isinstance(goal, str) and not goal.replace(".", "").isdigit():  # 转换目标格式为 时间戳
        return _fmt_to_timestamp(goal, fmt_str, times, instance)
    elif goal and isinstance(goal, (float, int)) and cursor == 0:   # 转换时间戳为 目标时间格式
        return _timestamp_to_f_time(goal, fmt_str)
    else:    # 处理没有参数或者有游标参数的情况或者特定格式参数的情况
        if fmt and not cursor and instance is None:
            return time.strftime(fmt_str)
        elif fmt and cursor:
            return _cursor_to_f_time(cursor, fmt_str)
        elif not fmt and cursor:
            return _cursor_to_timestamp(instance, cursor, times)
        else:
            return _default_now_time(instance, times)


def _get_unit_times(unit):
    """
    获取需要补充的倍数
    :param unit:
    :return:
    """
    if "ms" in unit:
        times = 1000
    else:
        times = 1
    return times


def _cal_cursor_timestamp(goal, times, instance, cursor):
    if goal is None:
        base_time = _default_now_time(instance, times)
    else:
        str_goal = str(goal).split(".")[0]   # 取整
        this_times = 1 if len(str_goal) == 10 and times == 1 else 1000
        base_time = goal * this_times

    cursor_time = _get_offset(cursor) * times

    result_temp = base_time + cursor_time

    if times == 1000 and len(str(int(result_temp))) == 10:
        result_temp = result_temp * 1000

    if instance == int:
        return int(result_temp)
    else:
        return result_temp


def _default_now_time(instance, times):
    """
    默认输出--当前时间，是否要浮点数
    """
    time_now = time.time()
    if instance == float:
        return time_now * times
    else:
        return int(time_now * times)


def _cursor_to_timestamp(instance, cursor, times):
    """
    通过游标时间输出时间戳
    """
    result = _get_time_block(cursor)
    if instance == float:
        return result * times
    else:
        return int(result * times)


def _cursor_to_f_time(cursor, fmt_str):
    """
    通过游标时间输出格式化字符串
    """
    result = _get_time_block(cursor)
    if isinstance(result, (int, float)):
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
            raise TimeFormatException(f"请输入正确的[ goal ]:传入的是非数字类型的则会默认当前时间的格式化样式")
    return time.strftime(fmt_str, time.localtime(int_time))


def _fmt_to_timestamp(goal, fmt_str, times, instance):
    """
    时间串转换为时间戳
    """
    try:
        sure_time = time.mktime(time.strptime(goal, fmt_str)) * times
        if instance == float:
            return sure_time
        return int(sure_time)
    except Exception as e:
        raise TimeFormatException(f"由错误的[ fmt ]格式引发的异常: {e}")


def _guess_fmt(string: str):
    """
    当默认传入的fmt为True或者False的时候，这里预测fmt的格式
    (会自动匹配时间 目前只匹配基本的模板)
    """
    if not string:
        return ""

    if re.search(r"^\d{4}$", string): return "%Y"
    elif re.search(r"^\d{4}-\d{2}$", string): return "%Y-%m"
    elif re.search(r"^\d{4}年\d{2}月$", string): return "%Y年%m月"
    elif re.search(r"^\d{4}-\d{2}-\d{2}$", string): return "%Y-%m-%d"
    elif re.search(r"^\d{4}/\d{2}/\d{2}$", string): return "%Y/%m/%d"
    elif re.search(r"^\d{4}年\d{2}月\d{2}日$", string): return "%Y年%m月%d日"
    elif re.search(r"^\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}$", string): return "%Y年%m月%d日 %H:%M"
    elif re.search(r"^\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}:\d{2}$", string): return "%Y年%m月%d日 %H:%M:%S"
    elif re.search(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", string): return "%Y-%m-%d %H:%M:%S"
    elif re.search(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$", string): return "%Y/%m/%d %H:%M:%S"
    elif re.search(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}$", string): return "%Y/%m/%d %H:%M"
    elif re.search(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", string): return "%Y-%m-%d %H:%M"
    # from dateutil.parser import parse
    # from dateparser import parse

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


def time_count(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        t1 = time.time()
        bk = fn(*args, **kwargs)
        logger.debug(f'[{fn.__name__}] 耗时: {time.time()-t1:.3f}')
        return bk
    return inner


def time_range(start_time: tuple, end_time: tuple, unit: Literal['s', 'ms'] = 's') -> Tuple[int, int]:
    """
    获取一段时间的范围  目前只支持元组范围的 如果要其它格式操作啥的 可以用 datetime 模块 那里也有现成的
    :param start_time: 开始的时间 格式 -> (年, 月, 日, 时, 分, 秒)   里面的都是==>整数/字符串   不用全部写完 如  (年,)  (年,月)
    :param end_time  : 截至的时间 格式同上 不写的默认为最小值 如 月日不写就是1  时分秒不写就是 0  但是年要写 ·4位· 那个
    :param unit      : 返回的结果的单位  s --> 返回秒  |   ms --> 返回毫秒
    """
    start_time_fmt = _get_fmt_time(start_time)
    end_time_fmt = _get_fmt_time(end_time)

    if start_time_fmt > end_time_fmt:
        raise ErrorTimeRange("错误的时间范围,请保证时间线: 开始时间 < 结束时间")

    if start_time_fmt == end_time_fmt:
        logger.warning(f"开始时间: {start_time} 和结束时间: {end_time} 数据值一样了,不报错,但需要留意")

    return get_time(start_time_fmt, unit=unit), get_time(end_time_fmt, unit=unit)


def _get_fmt_time(time_limit: tuple):
    """
    因为最差都会有一个年
    """
    year = time_limit[0]
    assert (isinstance(year, int) and 1970 <= year
            ) or (
            isinstance(year, str) and year.isdigit() and len(year) >= 4 and "1970" <= year
    ), ErrorTimeRange("`年`只可以为大于等于1970年的数字字面量,并且是4位数的值")

    month = time_limit[1] if len(time_limit) >= 2 else 1
    assert (isinstance(month, int) and 1 <= month <= 12
            ) or (
            isinstance(month, str) and month.isdigit() and 1 <= int(month) <= 12
    ), ErrorTimeRange(f"月只可以为是 1-12 整型, 你写的`月`是: [{month}]")

    day = time_limit[2] if len(time_limit) >= 3 else 1
    this_month_max_day = _check_month_day_max(int(year), int(month))
    assert (isinstance(day, int) and 1 <= day <= this_month_max_day
            ) or (
            isinstance(day, str) and day.isdigit() and 1 <= int(day) <= this_month_max_day
    ), ErrorTimeRange(f"{year}年{month}月这个月的日只可以为是 1-{this_month_max_day} 整型, 你写的`日`是: [{day}]")

    hour = time_limit[3] if len(time_limit) >= 4 else 0
    assert (isinstance(hour, int) and 0 <= hour <= 23
            ) or (
            isinstance(hour, str) and hour.isdigit() and 0 <= int(hour) <= 23
    ), ErrorTimeRange(f"时只可以为是 0-23 整型, 你写的`时`是: [{hour}]")

    minute = time_limit[4] if len(time_limit) >= 5 else 0
    assert (isinstance(minute, int) and 0 <= minute <= 59
            ) or (
            isinstance(minute, str) and minute.isdigit() and 0 <= int(minute) <= 59
    ), ErrorTimeRange(f"分只可以为是 0-59 整型, 你写的`分`是: [{minute}]")

    second = time_limit[5] if len(time_limit) == 6 else 0
    assert (isinstance(second, int) and 0 <= second <= 59
            ) or (
            isinstance(second, str) and second.isdigit() and 0 <= int(second) <= 59
    ), ErrorTimeRange(f"秒只可以为是 0-59 整型, 你写的`秒`是: [{second}]")

    return f"{year}-{month:>02}-{day:>02} {hour:>02}:{minute:>02}:{second:>02}"


def _check_month_day_max(year: int, month: int) -> int:
    _, max_day = calendar.monthrange(year, month)  # 第一个参数表示这个月第一天是周几 0->周一  6->周日
    return max_day


if __name__ == "__main__":
    pass
