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
from lite_tools.utils_jar.moyu_rili import print_date


def _print_base():
    """输出lite-tools基本信息的"""
    print_info = f"lite-tools {VERSION}\n\n"
    print_info += "Usage: lite-tools <command> [options] [args]\n\n"
    print_info += "Available commands:\n  fish        获取摸鱼人日历\n"
    print_info += "  trans       文件转换相关内容[目前测试版有图片转pdf]\n\n"
    print_info += "Use \"lite-tools <command> -h\" to see more info about a command"
    print(print_info)


def execute(args):
    # args = sys.argv
    if len(args) < 2:
        _print_base()
        return

    command = args.pop(1)
    if command == "fish":
        print_date()
    elif command == "trans":
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
    else:
        _print_base()
