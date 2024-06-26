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
目前只弄兽音 其他的不弄了 算法来源是 http://hi.pcmoe.net/roar.html 然后改编成python的
后续会添加其它加密的 默认就这个东西
"""
import re
from lite_tools.commands.whsecret.bearsay import roar_decode, roar_encode
from lite_tools.commands.whsecret.morse import Rule, morse_decode, morse_encode
from lite_tools.utils.lite_table import get_terminal_long
from lite_tools.tools.core.lite_string import color_string


def check_say_mode(string: str) -> int:
    """
    return 0: 这里是需要加密的
    return 1: 这里是需要解密的
    """
    base_str = set(string)
    if len(base_str) > 4:
        return 0
    for each in base_str:
        if each not in ["嗷", "呜", "啊", "~"]:
            return 0
    return 1


def _print_say_help():
    """
    打印 说
    """
    base_info = "lite_tools say <command> [options]\n\n"
    base_info += "关于加解密说话的一些操作:\n"
    base_info += "command arguments:\n  "
    base_info += "bear          [默认 不跟操作也是这个]进入兽音加密解密模式\n  "
    base_info += "morse         进入摩斯加密解密模式\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help    show this help message and exit\n  "
    base_info += "--split       摩斯密码专用 --split=<不含空字符的rule> 分割:默认rule=' ' 默认一个空(所以空就不要写了)\n  "
    base_info += "--short       摩斯密码专用 --short=<不含空字符的rule> 短码:默认rule='.'\n  "
    base_info += "--long        摩斯密码专用 --long=<不含空字符的rule>  长码:默认rule='-'"
    print(base_info)


def bear_mode():
    split_line_long = get_terminal_long() // 2 - 3
    while True:
        try:
            key = input(f"{color_string('bear', 'purple')} >>> ")
        except KeyboardInterrupt:
            break
        else:
            if not key or key in ['quit()', 'exit()']:
                break
            key = key.strip().replace(" ", "").replace("\n", "").replace("\r", "")
            mode = check_say_mode(key)
            if mode == 0:
                s = roar_encode(key)  # 加密
                print(f"{color_string('输出', 'cyan')}: {s}")
            else:
                s = roar_decode(key)  # 解密
                print(f"{color_string('翻译', 'green')}: {s}")
            print(color_string(f"{'-' * split_line_long} bear {'-' * split_line_long}", "yellow"))


def check_morse_mode():
    mode_string = input(f"{color_string('mode:', 'cyan')}【0/不输入:解密】【1:加密】>>> ")
    if mode_string in ["1", 1]:
        return 1   # 加密
    else:
        return 0   # 解密


def morse_decode_check(string: str, rule: Rule) -> bool:
    """检查是否是便标准的解密模式"""
    if rule.short in string:
        string = string.replace(rule.short, "")

    if rule.long in string:
        string = string.replace(rule.long, "")

    if rule.split in string:
        string = string.replace(rule.split, "")

    if not string:
        return True
    else:
        return False


def morse_mode(rule_string: str):
    rule = Rule()
    split = re.search(r"--split=(?P<symbol>[\"']?)(\S+)(?P=symbol)", rule_string)
    if split:
        rule.split = split.group(2)

    short = re.search(r"--short=(?P<symbol>[\"']?)(\S+)(?P=symbol)", rule_string)
    if short:
        rule.short = short.group(2)

    long = re.search(r"--long=(?P<symbol>[\"']?)(\S+)(?P=symbol)", rule_string)
    if long:
        rule.long = long.group(2)

    split_line_long = get_terminal_long() // 2 - 4

    while True:
        try:
            input_string = input(f"{color_string('morse', 'purple')} >>> ")
        except KeyboardInterrupt:
            break
        else:
            if not input_string or input_string in ['quit()', 'exit()']:
                break
            input_string = input_string.strip()
            mode = check_morse_mode()
            if mode:  # 加密
                out_string = morse_encode(input_string, rule)
                tag = color_string("加密>>> ", "green")
            else:
                flag = morse_decode_check(input_string, rule)
                if not flag:
                    print(color_string("请选择正确的模式[当前并非专用模式的解密方案],检查是否需要设置rule【split,long,short】", 'r'))
                    out_string = ""
                else:
                    out_string = morse_decode(input_string, rule)
                tag = color_string("解密>>> ", "green")
            if out_string:
                print(f"{tag}{out_string}")
            print(color_string(f"{'-' * split_line_long} morse {'-' * split_line_long}-", "yellow"))


def cmd_say(args: tuple):
    if len(args) == 1 or "bear" in "".join(args):
        bear_mode()
    elif len(args) > 1 and "morse" in "".join(args):
        morse_mode(" ".join(args[1:]))
    elif len(args) > 1 and args[1] in ["-h", "--help"]:
        _print_say_help()
