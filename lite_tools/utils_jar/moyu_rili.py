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
这里只是我弄的摸鱼日历哈哈哈哈
"""
import time
from lite_tools.lib_jar.lib_string_parser import color_string

_format_string = """
<red>摸鱼日历：今天是 {year} 年 {month:>2} 月 {day:>2} 日 星期{week} </red> 
----------------------------------------
{month:>2} 月 {day:>2} 日 过去了 <cyan>{past_hour:>2} 小时</cyan>，还剩余 <green>{left_hour:>2} 小时</green>。
[进度: {hour_progresspercentage}%] {hour_progressbar}

本周过去了 <cyan>{past_day_week} 天</cyan>，还剩余 <green>{left_day_week} 天</green>。{extra_week_msg}
[进度: {week_day_progresspercentage}%] {week_day_progressbar}

本月过去了 <cyan>{past_day_month:>2} 天</cyan>，还剩余 <green>{left_day_month:>2} 天</green>。
[进度: {month_day_progresspercentage}%] {month_day_progressbar}

{year}年过去了 <cyan>{past_day_year:>3} 天</cyan>，还剩余 <green>{left_day_year:>3} 天</green>。
[进度: {year_day_progresspercentage}%] {year_day_progressbar}

人生短暂，把握每一秒，摸鱼学习不香吗？ 记得多动多喝水~
"""


def _get_chinese_week(localtime) -> str:
    chinese_week = ["一", "二", "三", "四", "五", "六", "日"]
    tm_w_day = localtime.tm_wday
    return chinese_week[tm_w_day]


def _get_progress_bar(spend, mode="day"):
    """
    自动获取范围
    :param spend: 度过的天数
    :param mode : 需要计算的模式 如天[24] 周[7] 月[28-31] 年[365-366]
    :return 百分数, 进度条
    """
    if mode == "week":
        nums = 7
    elif mode == "month":
        nums = 0
    elif mode == "year":
        nums = 0
    else:
        nums = 24

    percent = int(spend/nums * 100)
    black_block_nums = int(round(spend/nums, 1) * 10)  # * "■"
    blank_block_nums = 10 - black_block_nums
    return percent, "■" * black_block_nums + "□" * blank_block_nums


def count_now():
    """
    开始计算数据了
    """
    localtime = time.localtime()
    print_date(
        year=localtime.tm_year,
        month=localtime.tm_mon,
        day=localtime.tm_mday,
        week=_get_chinese_week(localtime),

    )


def print_date(
        year, month, day, week, extra_week_msg,
        past_hour, left_hour, hour_progressbar, hour_progress_percentage,
        past_day_week, left_day_week, week_day_progressbar, week_day_progress_percentage,
        past_day_month, left_day_month, month_day_progressbar, month_day_progress_percentage,
        past_day_year, left_day_year, year_day_progressbar, year_day_progress_percentage):
    print(color_string(_format_string.format(
        year=year, month=month, day=day, week=week, extra_week_msg=extra_week_msg,
        past_hour=past_hour, left_hour=left_hour,
        hour_progressbar=hour_progressbar, hour_progresspercentage=hour_progress_percentage,
        past_day_week=past_day_week, left_day_week=left_day_week,
        week_day_progressbar=week_day_progressbar, week_day_progresspercentage=week_day_progress_percentage,
        past_day_month=past_day_month, left_day_month=left_day_month,
        month_day_progressbar=month_day_progressbar, month_day_progresspercentage=month_day_progress_percentage,
        past_day_year=past_day_year, left_day_year=left_day_year,
        year_day_progressbar=year_day_progressbar, year_day_progresspercentage=year_day_progress_percentage
    )))


def test():
    year = 2022
    month = 1
    day = 6
    week = "三"

    past_hour = 10
    left_hour = 24 - past_hour

    hour_progressbar = "■■■■■■□□□□"
    hour_progress_percentage = 35

    past_day_week = 1
    left_day_week = 7 - past_day_week
    week_day_progressbar = "■■■■■■■□□□"
    week_day_progress_percentage = 10

    past_day_month = 15
    left_day_month = 31 - past_day_month
    month_day_progressbar = "■■□□□□□□□□"
    month_day_progress_percentage = 11

    past_day_year = 111
    left_day_year = 365 - past_day_year
    year_day_progressbar = "■□□□□□□□□□"
    year_day_progress_percentage = 60
    print_date(year, month, day)


if __name__ == "__main__":
    print(_get_progress_bar(19, 'day'))

