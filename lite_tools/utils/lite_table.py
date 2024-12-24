# -*- encoding: utf-8 -*-
import os
import sys
"""
这里只先实现基础的打印功能  后面再添加
"""
from lite_tools.tools.core.lite_string import color_string


class LiteTable:
    """
    这里先不忙弄 后面才会搞这个 这里很多细节要弄
    """
    def __init__(self, fields: list = None, column: str = "-", row: str = "|", corner: str = "+", align: str = "c"):
        base_item = {}
        if fields and isinstance(fields, list):
            for field in fields:
                base_item[field] = []


def print_head(title: str, error: int = 0):
    """
    param error: 是误差来的 因为有颜色的字符会有字符宽度错误问题
    """
    ts = get_terminal_long()
    line_string = "+" + "-" * (ts - 2) + "+"
    title_long = 0 - error
    for char in title:
        title_long += char_long(char)
    l_blank = (ts // 2 - 1) - (title_long // 2)
    r_blank = ts - 2 - l_blank - title_long
    title_line = "".join(["|", l_blank * " ", title, " " * r_blank, "|"])
    return f"{line_string}\n{title_line}\n{line_string}\n"


def get_terminal_long() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 100


def char_long(char) -> int:
    return 2 if ord(char) > 7000 else 1   # 随便界定了一个范围而已


def clear_screen():
    if sys.platform in ["win32", "win64"]:
        _ = os.system("cls")
    else:
        _ = os.system("clear")


if __name__ == "__main__":
    s = print_head(color_string("测试<red>中文</red>然后和英文mixed"), error=9)
    print(s)
