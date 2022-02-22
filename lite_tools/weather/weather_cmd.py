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
import os
import sys
from lite_tools.lib_jar.lib_try import try_catch
from lite_tools.lib_jar.lib_string_parser import color_string
from lite_tools.lib_jar.lib_dict_parser import match_case, try_key
from lite_tools.utils_jar.base_cmd import circle_cmd, input_option

try:
    from prettytable import PrettyTable
    from lite_tools.weather.weather_main import get_weather
except ImportError:
    raise ImportError


all_tabs = {
    "1": "本地天气",
    "2": "手动查询",
    "0": "*退出*"
}


def _print_weather_base():
    """
    打印关于天气的一些操作
    """
    base_info = "lite_tools weather [options]\n\n"
    base_info += "获取关于新闻模块下面的操作:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help    show this help message and exit\n  "
    base_info += "不跟任何选择    默认就是查询本地**当天**天气情况\n  "
    base_info += "shell         进入shell控制终端查询天气模式--包含下面所有单独的操作 额外支持**最近一周天气情况**\n  "
    base_info += "城市名         获取指定城市的**当天**天气(支持《市/区/县》只需要写明最小单位城市名就行 -- 不支持《省/镇/乡》)"
    print(base_info)


@match_case
def chose_now(city):
    pass


@chose_now.register("1")
def get_daily_briefing(_):
    """
    获取每日简报
    """
    print_hot_news()
    input_option(mode="weather")


@chose_now.register_all(["2", "weibo"])
def get_blog_rank(option):
    """
    获取微博热榜
    """
    blog_rank()
    if option.isdigit():
        input_option(mode="weather")


@chose_now.register_all(["3", "china"])
def from_global_china(option):
    """
    获取国内新闻
    """
    get_china_news()
    if option.isdigit():
        input_option(mode="weather")


@chose_now.register_all(["4", "world"])
def from_global_world(option):
    """
    获取国际新闻
    """
    get_world_news()
    if option.isdigit():
        input_option(mode="weather")


def news_cmdline(args: list):
    if len(args) <= 1:
        _print_weather_base()
    elif args[1] in ["-h", "--help"]:
        _print_weather_base()
    elif args[1] == "shell":
        circle_cmd(all_tabs, chose_now)
    else:
        chose_now(args[1])


if __name__ == "__main__":
    _print_weather_base()
