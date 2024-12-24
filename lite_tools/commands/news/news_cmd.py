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
from typing import List

from prettytable import PrettyTable
from lite_tools.commands.news.script_hot_news import print_hot_news, crawl_detail_from_paper
from lite_tools.commands.news.get_blog_rank import blog_rank
from lite_tools.commands.news.get_global_news import get_china_news, get_world_news

from lite_tools.tools.core.lite_match import match_case
from lite_tools.tools.core.lite_string import color_string
from lite_tools.utils.base_cmd import circle_cmd, input_option


all_tabs = {
    "1": "热门新闻",
    "2": "微博热榜",
    "3": "国内新闻",
    "4": "国际新闻",
    "5": "澎湃新闻",
    "0": "*退出*"
}

menu_tab = PrettyTable([color_string("序号", **{"v": "b", "f": "b"}), color_string("主菜单", **{"v": "b", "f": "b"})])
for ind, tab in all_tabs.items():
    menu_tab.add_row([color_string(ind, **{"v": "b", "f": "g"}), tab])


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
    base_info += "China         获取国内新闻\n  "
    base_info += "world         获取国际新闻\n  "
    base_info += "paper         获取澎湃新闻最新消息\n  "
    print(base_info)


@match_case
def chose_now(_):
    pass


@chose_now.register("1")
def get_daily_briefing(_):
    """
    获取每日简报
    """
    # print_hot_news()
    get_china_news()          # 先不用服务器流程
    input_option(mode="news")


@chose_now.register_all(["2", "weibo"])
def get_blog_rank(option):
    """
    获取微博热榜
    """
    blog_rank()
    if option.isdigit():
        input_option(mode="news")


@chose_now.register_all(["3", "china", "China"])
def from_global_china(option):
    """
    获取国内新闻
    """
    get_china_news()
    if option.isdigit():
        input_option(mode="news")


@chose_now.register_all(["4", "world"])
def from_global_world(option):
    """
    获取国际新闻
    """
    get_world_news()
    if option.isdigit():
        input_option(mode="news")


@chose_now.register_all(["5", "paper"])
def from_paper_new(option):
    """
    获取澎湃新闻最新消息
    """
    crawl_detail_from_paper()
    if option.isdigit():
        input_option(mode="news")


def news_cmdline(args: List[str]):
    if len(args) <= 1:
        print_hot_news()
    elif args[1] in ["-h", "--help"]:
        _print_news_option()
    elif args[1].lower() in ["weibo", "china", "world", "paper"]:
        chose_now(args[1])
    elif args[1] == "shell":
        circle_cmd(menu_tab, chose_now)
    else:
        _print_news_option()

