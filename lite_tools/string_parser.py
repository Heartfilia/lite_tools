# -*- coding: utf-8 -*-
import itertools
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


def __get_color_front(color_string: str):
    # 这里是为了传入数字也可以搞
    lower_string = str(color_string).lower()
    if lower_string in ['黑色', '黑', 'black', '30']: return 30
    elif lower_string in ['红色', '红', 'red', 'r', '31']: return 31
    elif lower_string in ['绿色', '绿', 'green', 'g', '32']: return 32
    elif lower_string in ['黄色', '黄', 'yellow', 'y', '33']: return 33
    elif lower_string in ['蓝色', '蓝', 'blue', 'b', '34']: return 34
    elif lower_string in ['紫色', '紫', 'purple', 'p', '35']: return 35
    elif lower_string in ['青蓝色', '青蓝', '靛色', '靛', 'cyan', 'c', '36']: return 36
    elif lower_string in ['白色', '白', 'white', 'w', '37']: return 37
    elif lower_string in ['深灰色', '灰色', '灰', 'darkgrey', 'dg', '90']: return 90
    elif lower_string in ['亮红色', '亮红', 'lightred', 'lr', '91']: return 91
    elif lower_string in ['亮绿色', '亮绿', 'lightgreen', 'lg', '92']: return 92
    elif lower_string in ['亮黄色', '亮黄', 'lightyellow', 'ly', '93']: return 93
    elif lower_string in ['亮蓝色', '亮蓝', 'lightblue', 'lb', '94']: return 94
    elif lower_string in ['粉色', '粉', 'pink', '少女粉', '猛男粉', '95']: return 95
    elif lower_string in ['亮青色', '亮青', 'lightcyan', 'lc', '96']: return 96
    return None


def __get_color_background(color_string: str, backgroud=True):
    # backgroud 这里是为了排除字体颜色的英文单词给搞到了背景颜色
    lower_string = str(color_string).lower()
    if backgroud is True and not lower_string.isdigit(): return None
    if lower_string in ['黑色', '黑', 'black', '40']: return 40
    elif lower_string in ['红色', '红', 'red', 'r', '41']: return 41
    elif lower_string in ['绿色', '绿', 'green', 'g', '42']: return 42
    elif lower_string in ['黄色', '黄', 'yellow', 'y', '43']: return 43
    elif lower_string in ['蓝色', '蓝', 'blue', 'b', '44']: return 44
    elif lower_string in ['紫色', '紫', 'purple', 'p', '45']: return 45
    elif lower_string in ['青蓝色', '青蓝', '靛色', '靛', 'cyan', 'c', '46']: return 46
    elif lower_string in ['白色', '白', 'white', 'w', '47']: return 47
    return None


def __get_view_mode(mode: str, viewer=True):
    lower_string = str(mode).lower()
    if viewer is True and not lower_string.isdigit(): return None
    if lower_string in ["reset", "重置", "0"]: return 0            # 不输出任何样式
    elif lower_string in ["bold", "加粗", "b", "1"]: return 1           # 加粗
    elif lower_string in ["disable", "禁用", "2"]: return 2        # 不知道这个有什么效果 看不出来
    elif lower_string in ["underline", "下划线", "u", "4"]: return 4      # 下划线
    elif lower_string in ["flash", "闪烁", "f", "5"]: return 5          # 闪烁
    elif lower_string in ["reverse", "反相", "r", "7"]: return 7        # 反相
    elif lower_string in ["invisible", "消失", "不可见", "i", "8"]: return 8      # 不可见
    elif lower_string in ["strikethrough", "删除线", "s", "9"]: return 9  # 删除线
    return None


def deco_clr(string: str = "", *args, **kwargs) -> str:
    """
    给字体增加颜色 参数如下 使用直接  deco_clr("要加颜色的字体", 34, 5, 44) 需要加的颜色数字直接写下面 只有在规定范围内才能被提取 同一级写了多个只拿第一个
    如果传入英文 只有RGBYWPC 可以缩写 黑色black需要写全 大小写都无所谓  英文属于<<字体颜色>> 
    可以使用字典传参 设置字体颜色背景颜色 显示方式 如：{"f": "red", "b": "yellow", "v": "default", 'lenght': 20}  # 这里限定了20个字符宽度(实际会大于20个只不过我这里做了处理) length 键弄l也可以
    :param string: 传入的字符串
    :param args  : 参数注解如下面所示  传入非字典类型的时候 只有第一个参数起作用在字体颜色上面  -->传入字典同下操作
    :param kwargs: 这里传入需要用 **{}   
    :param f     : 字体颜色 -> (30, 黑色/black)(31, 红色/r/red)(32, 绿色/g/green)(33, 黄色/y/yellow)(34, 蓝色/b/blue)(35, 紫色/p/purple)(36, 青蓝色/c/cyan)(37, 白色/w/white)
                            -> (90, darkgrey)(91, lightred)(92, lightgreen)(93, lightyellow)(94, lightblue)(95, pink)(96, lightcyan)
    :param b     : 背景颜色 -> (40, 黑色/black)(41, 红色/r/red)(42, 绿色/g/green)(43, 黄色/y/yellow)(44, 蓝色/b/blue)(45, 紫色/p/purple)(46, 青蓝色/c/cyan)(47, 白色/w/white)
    :param v     : 显示方式 -> (0, 重置/reset)(1, 加粗/b/bold)(2, 禁止/disable)(4, 使用下划线/u/underline)(5, 闪烁/f/flash)(7, 反相/r/reverse)(8, 不可见/i/invisible)(9, 删除线/s/strikethrough)   
    """
    base_string = '\033['
    if (string and kwargs) or (string and args and isinstance(args[0], dict)):
        if string and args and isinstance(args[0], dict): kwargs = args[0]
        lenght = kwargs.get('lenght', 0) or kwargs.get('l', 0)
        if isinstance(lenght, int) or (isinstance(lenght, str) and lenght.isdigit()):
            lenght = int(lenght) 

        f = kwargs.get('f')
        if f: 
            f_string = __get_color_front(f)
            base_string += f"{f_string};" if f_string is not None else ""

        b = kwargs.get('b')
        if b: 
            b_string = __get_color_background(b, backgroud=False) 
            base_string += f"{b_string};" if b_string is not None else ""

        v = kwargs.get('v')
        if v: 
            v_string = __get_view_mode(v, viewer=False)  
            base_string += f"{v_string:>02};" if v_string is not None else ""
        
        
        if base_string == '\033[': return string    # 如果操作一通后还是和原来字符串一样就不装饰
        if not kwargs.get('lenght') and not kwargs.get('l', 0): lenght = 0
        else: lenght -= len(string)
        return f"{base_string.strip(';')}m{string}{' ' * lenght}\033[0m"

    elif string and args:
        result_ftclr = list(filter(__get_color_front, map(__get_color_front, args)))
        result_bkclr = list(filter(__get_color_background, args))
        result_vt = list(filter(__get_view_mode, args))
        if result_ftclr:
            base_string += f'{result_ftclr[0]};'
        if result_bkclr:
            base_string += f'{result_bkclr[0]};'
        if result_vt:
            base_string += f'0{result_vt[0]};'
        return f"{base_string.strip(';')}m{string}\033[0m"

    return string
