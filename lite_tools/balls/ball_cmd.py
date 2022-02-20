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
try:
    import requests
    from prettytable import PrettyTable
    from lite_tools.balls.fuli import get_fuli
    from lite_tools.balls.tiyu import get_tiyu
except ImportError:
    raise ImportError

from lite_tools.lib_jar.lib_dict_parser import match_case
from lite_tools.lib_jar.lib_string_parser import color_string


ball_items = {
    "1": "福利彩票",
    "2": "体育彩票",
    "0": "*退出*"
}

ball_menu = PrettyTable([color_string("序号", **{"v": "b", "f": "r"}), color_string("主菜单", **{"v": "b", "f": "r"})])
for ind, tab in ball_items.items():
    ball_menu.add_row([color_string(ind, **{"v": "b", "f": "g"}), tab])


def _print_ball_option():
    """
    打印关于ball的一些操作
    """
    base_info = "lite_tools ball [options]\n\n"
    base_info += "获取关于新闻模块下面的操作:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help    show this help message and exit\n  "
    base_info += "不跟任何选择  会把两个彩票的数据都打印出来\n  "
    base_info += "fuli          福利彩票\n  "
    base_info += "tiyu          体育彩票"
    print(base_info)


@match_case
def chose_now(_):
    pass


@chose_now.register_all(["1", "fuli", "fl"])
def get_fl_info(option):
    """
    获取福利彩票
    """
    get_fuli()


@chose_now.register_all(["2", "tiyu", "ty"])
def get_gym_info(option):
    """
    体育彩票
    """
    get_tiyu()


def news_cmdline(args: list):
    if len(args) <= 1:
        pass
    elif args[1] in ["-h", "--help"]:
        _print_ball_option()
    elif args[1] in ["fuli", "tiyu"]:
        chose_now(args[1])
    else:
        _print_ball_option()

