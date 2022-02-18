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
import re
import sys

from lite_tools.version import VERSION
from lite_tools.utils_jar.logs import logger
from lite_tools.lib_jar.lib_dict_parser import match_case
from lite_tools.today.script_fisher_date import print_date


def _print_base():
    """输出lite-tools基本信息的"""
    print_info = f"lite-tools {VERSION}\n\n"
    print_info += "Usage: lite-tools <command> [options] [args]\n\n"
    print_info += "Available commands:\n"
    print_info += "  fish        获取摸鱼人日历\n"
    print_info += "  balls        获取彩票详情\n"
    print_info += "  news        获取近日热闻,新闻列表 后面可以跟 -h 获取更多操作\n"
    print_info += "  today       获取当天黄历 后接`history`可以获取今日往事 接`oil`获取今日油价\n"
    print_info += "  trans       文件转换相关内容[目前测试版有图片转pdf]\n\n"
    print_info += "Use \"lite-tools <command> -h\" to see more info about a command"
    print(print_info)


@match_case
def chose_option(_, *args):
    _print_base()


@chose_option.register("fish")
def get_fish_date(_, *args):
    print_date()


@chose_option.register("balls")
def get_ball(_, *args):
    pass


@chose_option.register("today")
def get_today_info(_, *args):
    if len(args) > 0:
        args = args[0]
    try:
        from lite_tools.today.oil_price import print_oil
        from lite_tools.today.script_almanac import print_today, print_today_history
    except ImportError:
        logger.warning("today 为进阶版功能 请安装>> 日历版: lite-tools[date] 或者补充版: lite-tools[all]")
        sys.exit(0)
    else:
        if len(args) < 2:
            print_today()
        elif "history" in args:
            print_today_history()
        elif "oil" in args:
            print_oil()
        else:
            print_today()


@chose_option.register("trans")
def trans_files(_, *args):
    if len(args) > 0:
        args = args[0]
    try:
        from lite_tools.trans.pdf import pdf_run
        from lite_tools.trans.excel import excel_run
        from lite_tools.trans.pic import pic_run
        from lite_tools.trans.word import word_run
    except ImportError:
        logger.warning("trans 为进阶版功能 请安装>> 文件版: lite-tools[file] 或者补充版: lite-tools[all]")
        sys.exit(0)
    else:
        mode_args = re.search(r"-m\s+(pdf)", " ".join(args)) or re.search(r"--mode\s+(pdf)", " ".join(args))
        if mode_args:
            mode = mode_args.group(1)
            if mode == "pdf":
                pdf_run(args)
            elif mode == "excel":
                excel_run(args)
            elif mode == "pic":
                pic_run(args)
            elif mode == "word":
                word_run(args)
        else:
            pdf_run(args)


@chose_option.register("news")
def get_hot_news(_, *args):
    if len(args) > 0:
        args = args[0]
    else:
        args = []
    try:
        from lite_tools.news.news_cmd import news_cmdline
    except ImportError:
        logger.warning("news 需要网络请求模块,如果没有需要安装日历版: lite-tools[date] 或补充版: lite-tools[all]")
        sys.exit(0)
    else:
        news_cmdline(args)


def execute():
    args = sys.argv
    if len(args) < 2:
        _print_base()
        return

    command = args.pop(1)
    chose_option(command, args)
