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
import sys

from lite_tools.version import VERSION
from lite_tools.utils_jar.moyu_rili import print_date


def _print_base():
    """输出lite-tools基本信息的"""
    print(f"lite-tools {VERSION}\nUsage: lite-tools <command>\n"
          f"Available commands: fish\n"
          f"waiting for more options")


def execute():
    args = sys.argv
    if len(args) < 2:
        _print_base()
        return

    command = args.pop(1)
    if command == "fish":
        print_date()
    else:
        _print_base()
