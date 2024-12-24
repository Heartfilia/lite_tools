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
from lite_tools.commands.balls.fuli import get_fuli
from lite_tools.commands.balls.tiyu import get_tiyu

from lite_tools.tools.core.lite_match import match_case


def _print_ball_option():
    """
    打印关于ball的一些操作
    """
    base_info = "lite_tools ball [options]\n\n"
    base_info += "获取关于新闻模块下面的操作:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help    show this help message and exit\n  "
    base_info += "fuli/fl/福利   福利彩票\n  "
    base_info += "tiyu/ty/体育   体育彩票"
    print(base_info)


@match_case
def chose_now(_):
    pass


@chose_now.register_all(["fuli", "fl", "福利"])
def get_fl_info(option):
    """
    获取福利彩票
    """
    get_fuli()


@chose_now.register_all(["tiyu", "ty", "体育"])
def get_gym_info(option):
    """
    体育彩票
    """
    get_tiyu()


def ball_cmdline(args: list):
    if args[1] in ["fuli", "tiyu"]:
        chose_now(args[1])
    else:
        _print_ball_option()
