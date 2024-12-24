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
import random
import calendar

from lite_tools.tools.core.lite_string import color_string


_format_string = """********************************************
<red>摸鱼日历：今天是 {year} 年 {month:>2} 月 {day:>2} 日 星期{week} </red>
--------------------------------------------
{month:>2} 月 {day:>2} 日 过去了 <cyan>{past_hour:>2} 小时</cyan>，还剩余 <green>{left_hour:>2} 小时</green> 
[进度: {hour_progress_percentage:>3}%]  {hour_progressbar}
 
本周过去了 <cyan>{past_day_week} 天</cyan>，还剩余 <green>{left_day_week} 天</green>。
{extra_week_msg}
[进度: {week_day_progress_percentage:>3}%]  {week_day_progressbar}

本月过去了 <cyan>{past_day_month:>2} 天</cyan>，还剩余 <green>{left_day_month:>2} 天</green>。
[进度: {month_day_progress_percentage:>3}%]  {month_day_progressbar}
 
{year}年过去了 <cyan>{past_day_year:>3} 天</cyan>，还剩余 <green>{left_day_year:>3} 天</green>。
[进度: {year_day_progress_percentage:>3}%]  {year_day_progressbar}
 
{rand_tips}
"""
_tips = [
    '人生短暂，现在摸鱼学习不香吗？记得多动多喝水~',
    '工作再累 一定不要忘记摸鱼哦！',
    '有事没事起身去茶水间去厕所去廊道走走~',
    '多加班老板今年又可以换法拉利啦～',
    '珍惜摸鱼时光，不要难为自己～摸鱼才能让自己快乐！',
    '上班是帮老板赚钱，摸鱼是赚老板的钱！',
    '别老在工位上坐着，钱是老板的,但命是自己的。',
    '祝愿天下所有摸鱼人，都能愉快的渡过每一天!',
    '企业是别人的，身体是自己的，永远永远要以自己的身体为重！',
    '今天解决不了的事，明天也解决不了，摸鱼为大~'
]


def _get_chinese_week(localtime):
    """获取星期和提醒"""
    chinese_week = ["一", "二", "三", "四", "五", "六", "日"]
    tm_w_day = localtime.tm_wday
    extra_msg = "<green>当前正是周末啦～</green>" if tm_w_day in [5, 6] else "Other"
    if extra_msg == "Other":
        go_week = 4 - tm_w_day
        extra_msg = f"<yellow>还有 {go_week} 天周末</yellow>" if go_week != 0 else "<blue>明天就是周末啦～坚持摸鱼～</blue>"
    return chinese_week[tm_w_day], extra_msg


def _get_progress_bar(spend: int, mode: str = None, nums: int = 0):
    """
    自动获取范围
    :param spend: 度过的天数
    :param mode : 需要计算的模式 如天[24] 周[7] 月[28-31] 年[365-366]
    :param nums : 传入总共天数 有需要再传
    :return 百分数, 进度条
    """
    if mode == "week":
        nums = 7
    elif mode == "day":
        nums = 24

    percent = int(spend/nums * 100)
    black_block_nums = int(round(spend/nums, 1) * 10)
    blank_block_nums = 10 - black_block_nums
    return percent, "■" * black_block_nums + "□" * blank_block_nums


def _get_hour_info(localtime):
    """获取小时相关的信息"""
    tm_hour = localtime.tm_hour
    left_hour = 24 - tm_hour
    hour_percent, progress_bar = _get_progress_bar(tm_hour, mode='day')
    return tm_hour, left_hour, hour_percent, progress_bar


def _get_week_info(localtime):
    """获取周相关的信息"""
    tm_w_day = localtime.tm_wday + 1
    left_week = 7 - tm_w_day
    week_percent, progress_bar = _get_progress_bar(tm_w_day, mode='week')
    return tm_w_day, left_week, week_percent, progress_bar


def _get_month_info(localtime):
    """获取月相关的信息"""
    now_day = localtime.tm_mday
    now_year = localtime.tm_year
    now_month = localtime.tm_mon
    now_month_max_day = calendar.monthrange(now_year, now_month)[1]
    left_day = now_month_max_day - now_day
    month_percent, progress_bar = _get_progress_bar(now_day, nums=now_month_max_day)
    return now_day, left_day, month_percent, progress_bar


def _get_year_info(localtime):
    """获取年相关信息"""
    now_day = localtime.tm_yday
    now_year = localtime.tm_year
    now_year_max_day = 366 if calendar.isleap(now_year) else 365
    left_day = now_year_max_day - now_day
    year_percent, progress_bar = _get_progress_bar(now_day, nums=now_year_max_day)
    return now_day, left_day, year_percent, progress_bar


def print_date():
    """
    开始计算数据了
    """
    localtime = time.localtime()
    week_info, extra_msg = _get_chinese_week(localtime)
    past_hour, left_hour, hour_progress_percentage, hour_progressbar = _get_hour_info(localtime)
    past_week, left_week, week_progress_percentage, week_progressbar = _get_week_info(localtime)
    past_month, left_month, month_progress_percentage, month_progressbar = _get_month_info(localtime)
    past_year, left_year, year_progress_percentage, year_progressbar = _get_year_info(localtime)
    print(color_string(_format_string.format(
        year=localtime.tm_year,
        month=localtime.tm_mon,
        day=localtime.tm_mday,
        week=week_info,
        past_hour=past_hour,
        left_hour=left_hour,
        hour_progress_percentage=hour_progress_percentage,
        hour_progressbar=hour_progressbar,
        past_day_week=past_week,
        left_day_week=left_week,
        week_day_progress_percentage=week_progress_percentage,
        week_day_progressbar=week_progressbar,
        extra_week_msg=extra_msg,
        past_day_month=past_month,
        left_day_month=left_month,
        month_day_progress_percentage=month_progress_percentage,
        month_day_progressbar=month_progressbar,
        past_day_year=past_year,
        left_day_year=left_year,
        year_day_progress_percentage=year_progress_percentage,
        year_day_progressbar=year_progressbar,
        rand_tips=random.choice(_tips)
    )))


if __name__ == "__main__":
    print_date()
