# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:27
# @Author : Lodge
import re
import time
import calendar
import datetime
import functools
from typing import Union, Tuple, Any
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from lite_tools.logs import logger
from lite_tools.utils.u_re_time import NORMAL_PATTERN
from lite_tools.exceptions.TimeExceptions import TimeFormatException, ErrorTimeRange

"""
这里可以用 但是比较臃肿 暂时不支持 年月日通过游标操作获得年月日 可以实现 但是不知道参数取名和其他的冲突问题
TODO(my_logger 在多线程中的路径有问题 -- 我也懒得修复 这个是个小问题)
"""

__ALL__ = ['get_time', 'time_count', 'time_range']


def get_time(goal: Union[str, int, float, None] = None, fmt: Union[bool, str, Tuple[str, str]] = False,
             unit: Literal["ms", "s"] = "s", instance: Union[None, type] = None, cursor: Union[str, int, float] = 0,
             **kwargs):
    """
    返回时间的数值(整数) 或者 格式化好了的数据 优先级 goal > fmt > double = cursor  如果传入字符串并且满足fmt格式 将会转换为时间戳
    异常的时候默认返回当前时间
    params goal: 传入准确的时间戳 最好十位 额外可以设置的参数有 double fmt 如果需要把格式化时间转换为数字需要设置double=True, fmt设置为对应的格式
           : 如果传入的是 xx前 如 1个月前 3小时前 基于此时此刻计算 如1月前 (现在是2023.7.19 17:26:05) -得到-> (2023.6.19 17:26:05)
    params fmt : 返回格式化后的数据 True/False 默认%Y-%m-%d %H:%M:%S格式 传入其它格式按照其它格式转换
               : 建议：如果是需要处理 格式化时间戳 转换成 时间戳的操作 只传入一个字符串 表示输入格式 并直接写上 ** timestamp=True or ts=True **
               : 建议：使用复合结构，来保证传入格式和输出格式正常 (传入格式, 输出格式)
    params unit : 单位默认s/秒 还仅支持 ms/毫秒  这个数据默认取整 --> 可以设置 unit="ms/s" 对double后的结果取整
    params instance: 写 int/float 即可按照int或者float返回数据
    params cursor: 默认传入游标单位/天  可以是正可以是负 可以是整数可以是字符串 注意是有大小写区别的
                   更多的参数: Y:年 m:月 d:日 H:时 M:分 S:秒 （同时间那边的参数格式）如 cursor="-2Y"  如果写一堆 全部累加
    params kwargs: 兼容不重要参数 如果写了 ** timestamp=True or ts=True **  那么一定是把这个转时间戳的
    """
    input_fmt, output_fmt = _get_user_fmt(fmt, **kwargs)   # output_fmt 这个参数在后面 转格式化时间的时候才用得到
    if not input_fmt and isinstance(goal, str):
        goal, input_fmt = _guess_fmt(goal)
        if not input_fmt:
            temp_goal = handle_vague_rule(goal)  # 模糊匹配时间
            if temp_goal:
                goal = temp_goal
            input_fmt = "%Y-%m-%d %H:%M:%S"

    times = _get_unit_times(unit)
    if kwargs.get('double') is True:   # 兼容老版本
        instance = float
    if instance is not None and instance not in [int, float]:
        instance = int

    # 先把不需要处理的格式的模板先返回
    if not goal:
        if fmt is False:
            if not cursor:
                # 没有游标处理操作的优先返回
                return _default_now_time(instance, times)
            else:
                # 有游标操作的部分
                return _cursor_to_timestamp(instance, cursor, times)
        else:
            now = datetime.datetime.now() + datetime.timedelta(seconds=_get_offset(cursor))
            return now.strftime(output_fmt)
    elif goal and isinstance(goal, (float, int)) and fmt is False:
        # 对传入的时间戳进行位移   估计很少概率会用到  返回的也是时间戳
        return _cal_cursor_timestamp(goal, times, instance, cursor)
    elif goal and isinstance(goal, (float, int)):
        # 转换时间戳 转换为 格式化时间
        return _timestamp_to_f_time(goal, output_fmt, cursor)
    elif isinstance(goal, str) and (len(goal) != 10 or len(goal) != 13) and (
            not isinstance(fmt, bool) or kwargs.get('timestamp') is True or kwargs.get('ts') is True) and not output_fmt:
        # 传入了格式化的时间 然后又传了格式化时间的格式 所以这里将会返回 时间戳
        return _fmt_to_timestamp(goal, input_fmt, times, instance)
    # 增加一个 传入是 a 格式 处理成b格式的情况
    elif goal and isinstance(goal, str) and input_fmt and output_fmt:  # 只有传入了输入输出格式的例子才会走到这里
        # 依据输入格式 将传入对象 格式化为 指定的输出格式
        return _fmt_to_fmt(goal, input_fmt, output_fmt, cursor)
    else:
        if fmt and cursor:  # 特殊情况 先留着
            return _cursor_to_f_time(cursor, output_fmt)
        else:
            logger.critical("不兼容的格式 默认返回 None 希望能把你传入的参数发送给我 我兼容")


def _fmt_to_fmt(goal: str, input_fmt: str, output_fmt: str, cursor: Any):
    # A格式转换为B格式
    date = datetime.datetime.strptime(goal, input_fmt)
    new_date = date + datetime.timedelta(seconds=_get_offset(cursor))
    return new_date.strftime(output_fmt)


def _get_user_fmt(fmt, **kwargs) -> Tuple[Union[str, bool], str]:
    """
    三种情况
    """
    if isinstance(fmt, bool):     # 如果穿了bool值 那么我就来猜格式
        if kwargs.get('timestamp') is True or kwargs.get('ts') is True:
            return "", ""
        return "", "%Y-%m-%d %H:%M:%S"
    elif isinstance(fmt, str):    # 如果传了一个字符串 那么输出为这个格式 输入我来猜
        if kwargs.get('timestamp') is True or kwargs.get('ts') is True:
            return fmt, ""   # 如果指定了 需要把这个格式化时间转成 时间戳
        return "", fmt
    elif isinstance(fmt, tuple) and len(fmt) == 1:  # 如果穿了元组但是只有一个值 同样我来猜输入 输出为传入的格式
        return "", fmt[0]
    elif isinstance(fmt, tuple) and len(fmt) == 2:  # 指定传入的格式 和 输出的格式
        return fmt[0], fmt[1]
    return "", "%Y-%m-%d %H:%M:%S"  # 默认匹配的 输出


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


def handle_vague_rule(string: str):
    """
    新增模糊时间匹配 这里返回  符合 %Y-%m-%d %H:%M:%S 的值
    """
    base_time = datetime.datetime.now()
    if "前天" in string:
        base_time = base_time - datetime.timedelta(days=2)
    elif "昨天" in string:
        base_time = base_time - datetime.timedelta(days=1)
    elif "前" in string or "后" in string:
        nums = float(re.search(r"(\d+\.?\d*)", string).group(1))
        nums = -nums if "前" in string else nums
        if "秒" in string:
            base_time = base_time + datetime.timedelta(seconds=nums)
        elif "分" in string:
            base_time = base_time + datetime.timedelta(minutes=nums)
        elif "时" in string:
            base_time = base_time + datetime.timedelta(hours=nums)
        elif "天" in string:
            base_time = base_time + datetime.timedelta(days=nums)
        elif "周" in string:
            base_time = base_time + datetime.timedelta(weeks=nums)
        elif "月" in string:
            base_time = base_time + datetime.timedelta(days=nums * 30)
        elif "年" in string:
            base_time = base_time + datetime.timedelta(days=nums * 365)
        return base_time.strftime("%Y-%m-%d %H:%M:%S")

    pt_flag = False

    pattern = re.search(r"(\d{2,4})[年.-](\d{1,2})[月.-](\d{1,2})日?", string.strip())
    if pattern:
        year_temp = pattern.group(1)
        year = f"20{year_temp}" if len(year_temp) == 2 else year_temp   # 目前看来 写两位年的一定是20年
        month = int(pattern.group(2))
        day = int(pattern.group(3))
        pt_flag = True
    else:
        pattern = re.search(r"(\d{1,2})[月.-](\d{1,2})日?", string.strip())
        if pattern:
            if "年" not in string:
                year = base_time.year
            else:
                yp = re.search(r"(\d{2,4})年", string)
                year_temp = yp.group(1)
                year = f"20{year_temp}" if len(year_temp) == 2 else year_temp
            month = int(pattern.group(1))
            day = int(pattern.group(2))
            pt_flag = True
        else:
            year = base_time.year
            month = base_time.month
            day = base_time.day

    pattern = re.search(r"(\d{1,2}):(\d{1,2}):(\d{1,2})$", string.strip())
    if pattern:
        hour = int(pattern.group(1))
        minute = int(pattern.group(2))
        second = int(pattern.group(3))
        pt_flag = True
    else:
        pattern = re.search(r"(\d{1,2}):(\d{1,2})$", string.strip())
        if pattern:
            hour = int(pattern.group(1))
            minute = int(pattern.group(2))
            second = 0
            pt_flag = True
        else:
            hour = minute = second = 0
    if pt_flag is True:
        return f"{year}-{month:>02}-{day:>02} {hour:>02}:{minute:>02}:{second:>02}"

    pattern = re.search(r"(\d+):(\d+):(\d+)$", string.strip())
    if pattern:
        hour = int(pattern.group(1))
        minute = int(pattern.group(2))
        second = int(pattern.group(3))
        return f"{base_time.year}-{base_time.month}-{base_time.day} {hour:>02}:{minute:>02}:{second:>02}"

    pattern = re.search(r"(\d+):(\d+)$", string.strip())
    if pattern:   # 匹配 昨天 9:01 这种格式的数据
        hour = int(pattern.group(1))
        minute = int(pattern.group(2))
        return f"{base_time.year}-{base_time.month}-{base_time.day} {hour:>02}:{minute:>02}:00"

    return ""


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


def _timestamp_to_f_time(goal, fmt_str, cursor):
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
    date = datetime.datetime.fromtimestamp(int_time) + datetime.timedelta(seconds=_get_offset(cursor))
    return date.strftime(fmt_str)


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
        return string, ""
    # 这个方案是 微博 的时间转换 为了方便我直接放这里了  "Tue Jul 25 11:00:40 +0800 2023"
    # 以后如果涉及了 这种英文的 记得在这个位置 单独添加一个函数处理
    if re.search(r"^\w+ \w+ \d{2} \d{2}:\d{2}:\d{2} \+0800 \d{4}$", string.strip()):
        return str(datetime.datetime.strptime(string.strip(), '%a %b %d %H:%M:%S +0800 %Y')), "%Y-%m-%d %H:%M:%S"

    string = string.replace('T', ' ')  # 把带了时区标志的时间变成原样
    string = re.sub(r"\.\d{3}Z|Z$", "", string)  # 把带了时区标志的时间 和 秒后面 还有为微秒之类的 变成原样

    for rule, sure_fmt, extra in NORMAL_PATTERN:
        if re.search(rule, string):
            if extra:
                temp = re.split(r"\W", get_time(fmt=True))
                if extra == "Y":
                    string = f"{temp[0]}-{string}"
                    sure_fmt = f"%Y-{sure_fmt}"
                elif extra == "Ymd":
                    string = f"{temp[0]}-{temp[1]}-{temp[2]} {string}"
                    sure_fmt = f"%Y-%m-%d {sure_fmt}"
            return string, sure_fmt
    return string, ""


def _get_offset(cursor: Union[str, int, float]) -> Union[int, float]:
    """
    通过传入的游标标志位 来判断时间  返回的是秒
    """
    offset = 0
    if isinstance(cursor, (int, float)):
        # 如果直接传数字 就按照天处理
        offset = cursor * 86400
    elif isinstance(cursor, str):
        level_year = re.search(r"(-?\d+\.?\d*)Y", cursor)
        level_month = re.search(r"(-?\d+\.?\d*)m", cursor)
        level_day = re.search(r"(-?\d+\.?\d*)d", cursor)
        level_hour = re.search(r"(-?\d+\.?\d*)H", cursor)
        level_minute = re.search(r"(-?\d+\.?\d*)M", cursor)
        level_second = re.search(r"(-?\d+\.?\d*)S", cursor)
        year = float(level_year.group(1)) if level_year else 0
        month = float(level_month.group(1)) if level_month else 0
        day = (float(level_day.group(1)) if level_day else 0) + (year * 365) + (month * 30)
        hour = float(level_hour.group(1)) if level_hour else 0
        minute = float(level_minute.group(1)) if level_minute else 0
        second = float(level_second.group(1)) if level_second else 0
        return datetime.timedelta(days=day, hours=hour, minutes=minute, seconds=second).total_seconds()
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

    return get_time(start_time_fmt, unit=unit, ts=True), get_time(end_time_fmt, unit=unit, ts=True)


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
    print(get_time())
    # print(get_time(instance=float))
    # print(get_time(unit='ms'))
    # print(get_time(unit='ms', instance=float))
    # print(get_time(fmt=True))
    # print(get_time("20230822", fmt="%Y%m%d", ts=True))
    # print(get_time("230822", ts=True))
    # print(get_time(1692633600, fmt=True))
    # get_time("2022/12/12 10:11", fmt="%Y/%m/%d %H:%M")
    # print(get_time("2天前"))
    # print(get_time("2天前", timestamp=True))
    # print(get_time("2周前", timestamp=True))
    # print(get_time("2周前"))
    # print(get_time("2023年11.02", fmt=("%Y年%m.%d", "%Y-%m-%d %H:%M:%S")))
    # print(get_time("2023年11.02", fmt=("%Y年%m.%d", "%Y-%m-%d %H:%M:%S"), cursor="3.5H30S"))
    # print(get_time("2023年11.02", fmt=("%Y年%m.%d", "%Y-%m-%d %H:%M:%S"), cursor="-3.5H"))
    # print(get_time(fmt=True, cursor=-1))
    # print(get_time(fmt=True, cursor="1Y2m1d"))
    # print(get_time("Tue Jul 25 11:00:40 +0800 2023"))
    print(time_range((2022,11), (2022,12,6)))    # 没有内置的格式 需要手动指定格式 转换位时间戳
