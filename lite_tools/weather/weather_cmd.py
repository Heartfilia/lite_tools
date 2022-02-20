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
    "2": "自动选择",
    "3": "手动查询",
    "0": "*退出*"
}


@match_case
def chose_now(_):
    pass

