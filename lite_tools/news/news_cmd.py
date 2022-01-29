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
from loguru import logger
from lite_tools.lib_jar.lib_dict_parser import match_case

try:
    from prettytable import PrettyTable
    from lite_tools.news.script_hot_news import print_hot_news
except ImportError:
    raise ImportError


all_tabs = {
    "1": "每日简报",
    "2": "微博热榜",
    "3": "国内新闻",
    "4": "国际新闻",
    "0/q": "退出"
}

menu_tab = PrettyTable(["序号", "主菜单"])
for ind, tab in all_tabs.items():
    menu_tab.add_row([ind, tab])


@match_case
def chose_now(_):
    pass


@chose_now.register("1")
def get_daily_briefing(_):
    """
    获取每日简报
    """


@chose_now.register("2")
def get_blog_rank(_):
    """
    获取微博热榜
    """


@chose_now.register("3")
def get_china_news(_):
    """
    获取国内新闻
    """


@chose_now.register("4")
def get_world_news(_):
    """
    获取国际新闻
    """


def circle_cmd():
    while True:
        _clear_screen()
        print(menu_tab)
        option = _input_option("选择操作")
        if option in ["0", "q", "Q", "exit", "quit"]:
            break


def news_cmdline(args: list):
    args = ["xxx.py", "xxx"]
    if len(args) <= 1:
        print_hot_news()


def _clear_screen():
    if "win" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def _input_option(option) -> str:
    result = input(f"news: {option} >>> ")
    return result
