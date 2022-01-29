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
from lite_tools.lib_jar.lib_dict_parser import match_case

try:
    from prettytable import PrettyTable
    from lite_tools.news.script_hot_news import print_hot_news
    from lite_tools.news.get_blog_rank import blog_rank
    from lite_tools.news.get_global_news import get_china_news, get_world_news
except ImportError:
    raise ImportError


all_tabs = {
    "1": "每日简报",
    "2": "微博热榜",
    "3": "国内新闻",
    "4": "国际新闻",
    "0": "*退出*"
}

menu_tab = PrettyTable(["序号", "主菜单"])
for ind, tab in all_tabs.items():
    menu_tab.add_row([ind, tab])


def _print_news_option():
    """
    打印关于news的一些操作
    """
    base_info = "lite_tools news [options]\n\n"
    base_info += "获取关于新闻模块下面的操作:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help    show this help message and exit\n  "
    base_info += "shell         进入shell控制终端查询新闻模式--包含下面所有单独的操作\n  "
    base_info += "不跟任何选择  默认就是打印 -- 每日简报\n  "
    base_info += "weibo         获取微博热榜\n  "
    base_info += "china         获取国内新闻\n  "
    base_info += "world         获取国际新闻"
    print(base_info)


@match_case
def chose_now(_):
    pass


@chose_now.register("1")
def get_daily_briefing(_):
    """
    获取每日简报
    """
    print_hot_news()
    _input_option()


@chose_now.register_all(["2", "weibo"])
def get_blog_rank(option):
    """
    获取微博热榜
    """
    blog_rank()
    if option.isdigit():
        _input_option()


@chose_now.register_all(["3", "china"])
def from_global_china(option):
    """
    获取国内新闻
    """
    get_china_news()
    if option.isdigit():
        _input_option()


@chose_now.register_all(["4", "world"])
def from_global_world(option):
    """
    获取国际新闻
    """
    get_world_news()
    if option.isdigit():
        _input_option()


@try_catch(log=False)
def circle_cmd():
    while True:
        _clear_screen()
        print(menu_tab)
        option = _input_option("选择序号")
        if option.lower() in ["0", "q", "o", "exit", "quit", ".exit", "quit()", "exit()"]:
            break
        chose_now(option)


def news_cmdline(args: list):
    if len(args) <= 1:
        print_hot_news()
    elif args[1] in ["-h", "--help"]:
        _print_news_option()
    elif args[1] in ["weibo", "china", "world"]:
        chose_now(args[1])
    elif args[1] == "shell":
        circle_cmd()
    else:
        _print_news_option()


def _clear_screen():
    if "win" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def _input_option(option="任意键返回上一级菜单") -> str:
    result = input(f"news: {option} >>> ")
    return result
