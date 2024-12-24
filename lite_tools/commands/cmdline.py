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
import os.path
import re
import sys

import requests
from lite_tools.utils import VERSION
from lite_tools.logs import logger
from lite_tools.utils.lite_dir import lite_tools_dir
from lite_tools.tools.core.lite_string import color_string
from lite_tools.tools.core.lite_match import match_case
from lite_tools.tools.time.lite_time import get_time
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.commands.today.fisher_date import print_date


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
    print_info += "  -V,--version   输出版本信息\n"
    print_info += "  flush          清理本地关于lite-tools的记录(慎用)\n"
    print_info += "  dict           部首查词,拼音的肯定你也知道怎么读,方便生僻字查询\n"
    print_info += "  fish           获取摸鱼人日历\n"
    print_info += "  fresh          更新一些lite-tools需要的资源 可以后跟具体参数\n"
    print_info += "  say            加解密:默认 <bear>兽说 <morse>摩斯\n"
    # print_info += "  acg            更多详情见 -h 默认输出今日视频记录(没搞完但是可以体验基础操作没有同步更新操作)\n"
    # print_info += "  ball           获取彩票详情\n"   # 这里先不提供了 目前要学习其他的 不搞这个地方了
    print_info += "  news           获取近日热闻,新闻列表 后面可以跟 -h 获取更多操作\n"
    print_info += "  today          获取当天黄历 后接`history`可以获取今日往事 接`oil`获取今日油价\n"
    print_info += "  weather        默认获取本地天气信息 跟 -h 获取更多操作\n"
    print_info += "  trans          文件转换相关内容[目前测试版有图片转pdf]\n\n"
    print_info += "Use \"lite-tools <command> -h\" to see more info about a command"
    print(print_info)


def _print_new_version_tip(new_version: str):
    # 模板直接摘取自博哥的哈哈哈
    print(f"""──────────────────────────────────────────────────────────────
New version available {color_string(VERSION, 'red')} → {color_string(new_version, 'green')}
Run>>> {color_string('pip install --upgrade lite-tools', 'yellow')} to update!
""")


def _get_last_check_version(fun):
    def wrap():
        if "beta" in VERSION:
            # 如果版本里面有version 那么就是开发中 所以就不提示更新了 也不用请求浪费网络
            return
        version_path = os.path.join(lite_tools_dir(), ".version")
        if not os.path.exists(version_path):
            return fun()   # 不存在 需要重新获取的
        with open(version_path, "r", encoding='utf-8') as fp:
            version_log = fp.read()  # "时间|版本"    至少缓存10分钟 10分钟内有变动不提示
        t, v = version_log.split("|")
        if get_time() - int(t) >= 600:  # 如果现在的时间比缓存的时间相差超过10分钟 将重新请求缓存
            return v
    return wrap


@try_catch(log=False)
@_get_last_check_version
def _get_version():
    resp = requests.get(
        'https://pypi.org/simple/lite-tools/',
        headers={"user-agent": "lite-tools Spider Engine"},
        timeout=3
    )
    stable_version = re.findall('>lite_tools-([^b]+)-py3-none-any.whl</a>', resp.text)
    online_last_stable_version = stable_version[-1]  # 线上最后一个稳定版
    return online_last_stable_version


def check_new_version(check: bool = True):
    def sure_version(version: str):
        return tuple(map(lambda x: int(x), version.split(".")))
    online_last_stable_version = _get_version()
    if online_last_stable_version is None:
        return
    now_stable_version = re.sub(r"-beta\d+", "", VERSION)     # 现在的稳定版
    if sure_version(now_stable_version) < sure_version(online_last_stable_version):
        _print_new_version_tip(new_version=online_last_stable_version)
    with open(os.path.join(lite_tools_dir(), ".version"), "w", encoding='utf-8') as fp:
        fp.write(f"{get_time()}|{online_last_stable_version}")  # "时间|版本"    至少缓存10分钟 10分钟内有变动不提示


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


@chose_option.register("say")
def bear_say(_, *args):
    _ = args
    from lite_tools.commands.whsecret.says import cmd_say
    cmd_say(args[0])


@chose_option.register("flush")
def flush_local(_, *args):
    from lite_tools.commands.flush.flush_cmd import flush_cmdline
    flush_cmdline(args[0])


@chose_option.register("dict")
def flush_local(_, *args):
    try:
        from lite_tools.commands.dictionary.dict_cmd import dict_cmdline
    except ImportError:
        logger.warning("dict 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
        sys.exit(0)
    dict_cmdline()


@chose_option.register("fresh")
def fresh_something(_, *args):
    # 联网更新一些资源 这里是手动操作
    try:
        from lite_tools.commands.fresh.fresh_cmd import fresh_cmdline
    except ImportError:
        logger.warning("fresh 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
        sys.exit(0)
    fresh_cmdline(args[0])


@chose_option.register("ball")
def get_ball(_, *args):
    try:
        from lite_tools.commands.balls.ball_cmd import ball_cmdline
    except ImportError:
        logger.warning("ball 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
        sys.exit(0)
    ball_cmdline(args[0])


@chose_option.register("weather")
def get_weather(_, *args):
    try:
        from lite_tools.commands.weather.weather_cmd import weather_cmdline
    except ImportError:
        logger.warning("weather 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
        sys.exit(0)

    weather_cmdline(args[0])


@chose_option.register("today")
def get_today_info(_, *args):
    if len(args) > 0:
        args = args[0]

    try:
        from lite_tools.commands.today.oil_price import print_oil
        from lite_tools.commands.today.script_almanac import print_today, print_today_history
    except ImportError:
        logger.warning("today 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
        sys.exit(0)

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
    try:
        from lite_tools.commands.news.news_cmd import news_cmdline
    except ImportError:
        logger.warning("news 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
        sys.exit(0)
    news_cmdline(args)


@chose_option.register("update")
def update_lite_tools(_, *args):
    from lite_tools.utils.pip_ import install

    install('lite-tools', update=True, source="https://pypi.org/simple")


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
        check_new_version()
        return

    command = args.pop(1)
    check = True if command != "update" else False
    chose_option(command, args)
    check_new_version(check)


if __name__ == "__main__":
    # _print_base()
    check_new_version()
