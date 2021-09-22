# -*- coding: utf-8 -*-
from .__code_range import (
    __x_range_list, __u_range_list, __p_range_list, __P_range_list, __e_range_list, __s_range_list, __f_range_list
)
"""
这里是把常用的先弄了出来 后续还可以拓展举铁参考见code_range
"""

def clean_string(string: str, mode: str = "xuf", ignore: str = "") -> str:
    '''
    清除字符串特殊符号的 -- 通过比对unicode码处理  如果u清理不干净 可以加上e
    :param string  : 传入的字符串
    :param mode    : - 清理模式 可以组合使用 -> - "x"：\\x开头的符号 - "u": \\u开头的符号 - "p": 英文标点(不含空格) - "P": 中文标点 - "e": emoji - "s": 常用特殊符号 如'\t' '\n' 包含空格 - "f": 全角字符
    :param ignore  : 清理的时候需要忽略的字符--组合使用少量排除 如 ignore="(,}"   不去掉字符串中的那三个字符
    '''
    base_string = ""
    for ch in string:
        if "x" in mode and ord(ch) in __x_range_list and ch not in ignore: continue
        if "u" in mode and ord(ch) in __u_range_list and ch not in ignore: continue
        if "p" in mode and ord(ch) in __p_range_list and ch not in ignore: continue
        if "P" in mode and ord(ch) in __P_range_list and ch not in ignore: continue
        if "e" in mode and (ord(ch) in __e_range_list or ord(ch) > 65535) and ch not in ignore: continue
        if "s" in mode and ord(ch) in __s_range_list and ch not in ignore: continue
        if "f" in mode and ord(ch) in __f_range_list and ch not in ignore: continue
        base_string += ch
    return base_string
