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
from typing import Any

from lite_tools.lib_jar.lib_try import try_catch


def clear_screen():
    if sys.platform in ["win32", "win64"]:
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def input_option(option="无效选项返回上一级菜单", mode="news") -> str:
    result = input(f"{mode}: {option} >>> ")
    return result


@try_catch(log=False)
def circle_cmd(menu_tab: Any, chose_now):
    """
    循环输入cmd
    :param menu_tab: 菜单界面 字典来的{"序号": "描述"}也可以 pretty 格式化对象也可以
    :param chose_now: 选择函数 -- 每个脚本自己处理
    """
    while True:
        clear_screen()
        print(menu_tab)
        option = input_option("选择序号")
        if option.lower() in ["0", "q", "o", "exit", "quit", ".exit", "quit()", "exit()"]:
            break
        chose_now(option)
