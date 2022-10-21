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
from lite_tools.tools.utils.logs import logger
from lite_tools.tools.core.lite_string import color_string
from lite_tools.tools.core.lite_match import match_case
from lite_tools.commands.today.fisher_date import print_date
from lite_tools.tools.utils.lite_dir import lite_tools_dir


# _my_image = """
# ┏┓┏┳━━┳━┳━━┳━┳━┳┓┏━┓
# ┃┃┃┣┓┏┫━╋┓┏┫┃┃┃┃┃┃━┫
# ┃┗┫┃┃┃┃━┫┃┃┃┃┃┃┃┗╋━┃
# ┗━┻┛┗┛┗━┛┗┛┗━┻━┻━┻━┛
# """

_my_image = """
██░░░██░████░████░████░░▄███▄░░░▄███▄░░██░░░▄███▄
██░░░██░░██░░██▄░░░██░░██▀░▀██░██▀░▀██░██░░░▀█▄▀▀
██░░░██░░██░░██▀░░░██░░██▄░▄██░██▄░▄██░██░░░▄▄▀█▄
████░██░░██░░████░░██░░░▀███▀░░░▀███▀░░████░▀███▀
"""


def _print_base():
    """输出lite-tools基本信息的"""
    print_info = _my_image + "\n"
    print_info += f"lite-tools {color_string(VERSION, 'cyan')}  当前版本均为测试版,等1.0修复稳定了才是正式的\n\n"
    print_info += "Usage: lite-tools <command> [options] [args]\n\n"
    print_info += "Available commands:\n"
    # print_info += "  flush       清理本地关于lite-tools的全部缓存(慎用)\n"   # 有这个功能但是不对外展示
    print_info += "  fish        获取摸鱼人日历\n"
    print_info += "  acg         更多详情见 -h 默认输出今日视频记录(没搞完但是可以体验基础操作没有同步更新操作)\n"
    # print_info += "  ball        获取彩票详情\n"   # 这里先不提供了 目前要学习其他的 不搞这个地方了
    print_info += "  news        获取近日热闻,新闻列表 后面可以跟 -h 获取更多操作\n"
    print_info += "  today       获取当天黄历 后接`history`可以获取今日往事 接`oil`获取今日油价\n"
    print_info += "  weather     默认获取本地天气信息 跟 -h 获取更多操作\n"
    print_info += "  trans       文件转换相关内容[目前测试版有图片转pdf]\n\n"
    print_info += "Use \"lite-tools <command> -h\" to see more info about a command"
    print(print_info)


@match_case
def chose_option(_, *args):
    _ = args
    _print_base()


@chose_option.register_all(["--version", "-V"])
def get_version(_, *args):
    _ = args
    print(VERSION)


@chose_option.register("fish")
def get_fish_date(_, *args):
    _ = args
    print_date()


@chose_option.register("flush")
def flush_local(_, *args):
    # 写一写的忧郁了要不要弄这个删除本地文件的操作  因为我这些本来我就做了移除操作
    root = lite_tools_dir()
    # 然后对下面的内容的文件夹进行操作  可选参数 acg  today  history


@chose_option.register("ball")
def get_ball(_, *args):
    from lite_tools.commands.balls.ball_cmd import ball_cmdline
    ball_cmdline(args[0])


@chose_option.register("weather")
def get_weather(_, *args):

    from lite_tools.commands.weather.weather_cmd import weather_cmdline
    weather_cmdline(args[0])


@chose_option.register("today")
def get_today_info(_, *args):
    if len(args) > 0:
        args = args[0]

    from lite_tools.commands.today.oil_price import print_oil
    from lite_tools.commands.today.script_almanac import print_today, print_today_history

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
        from lite_tools.commands.trans.pdf import pdf_run
        from lite_tools.commands.trans.excel import excel_run
        from lite_tools.commands.trans.pic import pic_run
        from lite_tools.commands.trans.word import word_run
    except ImportError:
        logger.warning("trans 需要一些额外的包[reportlab][Pillow] 也可以使用安装>> lite-tools[all]")
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

    from lite_tools.commands.news.news_cmd import news_cmdline
    news_cmdline(args)


@chose_option.register("acg")
def handle_video_logs(_, *args):
    """
    处理视频播放信息 我是打算弄acg内容的 但是其它视频好像也可以兼容
    """
    if len(args) > 0:
        args = args[0]
    else:
        args = []
    try:
        from lite_tools.commands.acg.main import main_animation
    except ImportError:
        sys.exit(0)
    else:
        main_animation(args)


def execute():
    args = sys.argv
    if len(args) < 2:
        _print_base()
        return

    command = args.pop(1)
    chose_option(command, args)


if __name__ == "__main__":
    _print_base()
    # flush_local(1)
