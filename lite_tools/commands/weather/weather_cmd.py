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
from lite_tools.commands.weather.weather_main import get_weather


def _print_weather_base():
    """
    打印关于天气的一些操作
    """
    base_info = "lite_tools weather [options]\n\n"
    base_info += "获取关于天气模块下面的操作:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help    show this help message and exit\n  "
    base_info += "不跟任何选择   默认就是查询本地**当天**天气情况\n  "
    base_info += "城市名         获取指定城市的**当天**天气(支持《市/区/县》只需要写明最小单位城市名就行 -- 不支持《省/镇/乡》)"
    print(base_info)


def weather_cmdline(args: tuple):
    if len(args) == 1:
        get_weather()
    elif args[1] in ["-h", "--help"]:
        _print_weather_base()
    else:
        get_weather(args[1])
