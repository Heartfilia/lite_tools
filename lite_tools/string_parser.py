# -*- coding: utf-8 -*-
from .__code_range import __u_range_list, __U_range_list
"""
这里是把常用的先弄了出来 后续还可以拓展举铁参考见code_range   ***这里清理字符串还是有bug  还需要调试***
"""

def clean_string(string: str, mode: str = "xuf", ignore: str = "") -> str:
    '''
    清除字符串**特殊符号**(并不是清除常用字符)的 -- 通过比对unicode码处理  如果u清理不干净 可以加上e
    x里面==不包含==s  常用的转义字符如:\\a \\b \\n \\v \\t \\r \\f
    :param string  : 传入的字符串
    :param mode    : 
        - 清理模式 可以任意排序组合使用 (下面前面括号内为速记单词(有的话)) -> - 
        "x"：\\x开头的符号 - 
        "u": \\u转义报错的符号 还有空白字符 - 
        "U": 在win上有字符linux上是空的字符 - 
        "p": (punctuation 小写)英文标点(含空格) - 
        "P": (Punctuation 大写)中文标点 - 
        "e": (emoji) - 
        "s": (special)常用特殊符号 如'\\t' '\\n' 不包含空格 - 
        "f": (full-width characters)全角字符  -- 
        "r": (reserve)预留字符显示为 ֌这样的 -
    :param ignore  : 清理的时候需要忽略的字符--组合使用少量排除 如 ignore="(,}"   不去掉字符串中的那三个字符
    '''
    if not isinstance(string, str): return ""

    kill_jar = _scaner(string)

    for kill in kill_jar:
        if \
        ("x" in mode and __judge_x(kill, ignore)) or \
        ("s" in mode and __judge_s(kill, ignore)) or \
        ("p" in mode and __judge_p(kill, ignore)) or \
        ("P" in mode and __judge_P(kill, ignore)) or \
        ("f" in mode and __judge_f(kill, ignore)) or \
        ("e" in mode and __judge_e(kill, ignore)) or \
        ("u" in mode and __judge_u(kill, ignore)) or \
        ("U" in mode and __judge_U(kill, ignore)) or \
        ("r" in mode and __judge_r(kill, ignore)): 
            string = string.replace(kill, "")
    return string


def __judge_x(char, ignore=""):
    if char not in ignore and (0 <= ord(char) < 7 or 14 <= ord(char) < 32 or 127 <= ord(char) < 161):
        return True


def __judge_s(char, ignore=""):
    if char not in ignore and 7 <= ord(char) < 14:
        return True


def __judge_p(char, ignore=""):
    if char not in ignore and (32 <= ord(char) < 48 or 58 <= ord(char) < 65 or 91 <= ord(char) < 97 or 123 <= ord(char) < 127):
        return True


def __judge_P(char, ignore=""):
    if char not in ignore and \
    (8208 <= ord(char) < 8232 or 8240 <= ord(char) < 8287 or 12289 <= ord(char) < 12310 or 65072 <= ord(char) < 65107 
    or 65108 <= ord(char) < 65127 or 65128 <= ord(char) < 65132 or 65281 <= ord(char) < 65313):
        return True


def __judge_f(char, ignore=""):
    if char not in ignore and 65314 <= ord(char) < 65377:
        return True


def __judge_u(char, ignore=""):
    if char not in ignore and ord(char) in __u_range_list:
        return True


def __judge_U(char, ignore=""):
    if char not in ignore and ord(char) in __U_range_list:
        return True

    
def __judge_e(char, ignore=""):
    if char not in ignore and ord(char) > 65535:
        return True


def __judge_r(char, ignore=""):
    """
    这里是从888断断续续的有占位符号 所以下面判断范围中小于888的都不用写了
    """
    if char not in ignore and \
    888 <= ord(char) < 65535 and \
    ord(char) not in __u_range_list and \
    ord(char) not in __U_range_list and \
    not __judge_P(char) and \
    not __judge_f(char):
        return True


def _scaner(string: str):
    jar = set()
    for ch in string: 
        if ch.isalpha() or ch.isdigit(): continue
        jar.add(ch)
    return jar


def deco_clr(string: str = "", *args) -> str:
    """
    给字体增加颜色 参数如下 使用直接  deco_clr("要加颜色的字体", 34, 5, 44) 需要加的颜色数字直接写下面 只有在规定范围内才能被提取 同一级写了多个只拿第一个
    :param string: 传入的字符串
    :param args   : 参数注解如下面所示
    :param ft_clr : 字体颜色 -> (30, 黑色)(31, 红色)(32, 绿色)(33, 黄色)(34, 蓝色)(35, 紫红色)(36, 青蓝色)(37, 白色)
    :param bk_clr : 背景颜色 -> (40, 黑色)(41, 红色)(42, 绿色)(43, 黄色)(44, 蓝色)(45, 紫红色)(46, 青蓝色)(47, 白色)
    :param vt     : 显示方式 -> (0, 终端默认设置)(1, 高亮显示)(4, 使用下划线)(5, 闪烁)(7, 反白显示)(8, 不可见)   
    """
    base_string = '\033['
    if string and args:
        result_ftclr = list(filter(lambda x: x in args, range(30, 38)))
        result_bkclr = list(filter(lambda x: x in args, range(40, 48)))
        result_vt = list(filter(lambda x: x in args, [0, 1, 4, 5, 7, 8]))
        if result_ftclr:
            base_string += f'{result_ftclr[0]};'
        if result_bkclr:
            base_string += f'{result_bkclr[0]};'
        if result_vt:
            base_string += f'{result_vt[0]};'
        return f"{base_string.strip(';')}m{string}\033[0m"
    return string
