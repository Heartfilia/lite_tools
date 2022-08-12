# -*- coding: utf-8 -*-
import re

from lite_tools.utils_jar.u_code_range import u_range_list, U_range_list

from lite_tools.utils_jar.u_sub_sup_string import SUB_SUP_WORDS_HASH
"""
这里是把常用的先弄了出来 后续还可以拓展举铁参考见code_range   ***这里清理字符串还是有bug  还需要调试***
"""
__ALL__ = ["CleanString", "color_string", "math_string"]


class CleanString(object):
    def __init__(self, mode: str = "xuf", ignore: str = ""):
        self.mode = mode
        self.ignore = ignore

    def get(self, string: str, mode: str = None, ignore: str = ""):
        """
        清除字符串**特殊符号**(并不是清除常用字符)的 -- 通过比对unicode码处理  如果u清理不干净 可以加上e
        x里面==不包含==s  常用的转义字符如:\\a \\b \\n \\v \\t \\r \\f   ==> 目前大部分可以清理干净 还有清理不干净的或者会报错的还在研究样本
        :param string  : 传入的字符串
        :param mode    :
            - 清理模式 可以任意排序组合使用 (下面前面括号内为速记单词(有的话)) -> -
            "a": 直接清理下面全部所有操作
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
        """
        if mode is not None and isinstance(mode, str):
            self.mode = mode
        if ignore is not None and isinstance(ignore, str):
            self.ignore = ignore

        if not isinstance(string, str):
            return ""

        kill_jar = self._scanner(string)

        for kill in kill_jar:
            if ("x" in self.mode and self.__judge_x(kill)) or ("s" in self.mode and self.__judge_s(kill)) or (
                "p" in self.mode and self.__judge_p(kill)) or ("P" in self.mode and self.__judge_big_p(kill)) or (
                "f" in self.mode and self.__judge_f(kill)) or ("e" in self.mode and self.__judge_e(kill)) or (
                "u" in self.mode and self.__judge_u(kill)) or ("U" in self.mode and self.__judge_big_u(kill)) or (
                    "r" in self.mode and self.__judge_r(kill)):
                string = string.replace(kill, "")
        return string

    @staticmethod
    def _scanner(string):
        jar = set(filter(lambda x: not x.isalpha() or not x.isdigit(), string))
        return jar

    def __judge_x(self, kill):
        if kill not in self.ignore and (0 <= ord(kill) < 7 or 14 <= ord(kill) < 32 or 127 <= ord(kill) < 161):
            return True

    def __judge_s(self, kill):
        if kill not in self.ignore and 7 <= ord(kill) < 14:
            return True

    def __judge_p(self, kill):
        if kill not in self.ignore and (
                32 <= ord(kill) < 48 or 58 <= ord(kill) < 65 or 91 <= ord(kill) < 97 or 123 <= ord(kill) < 127):
            return True

    def __judge_big_p(self, kill):
        if kill not in self.ignore and (
            8208 <= ord(kill) < 8232 or 8240 <= ord(kill) < 8287 or 12289 <= ord(kill) < 12310 or
            65072 <= ord(kill) < 65107 or 65108 <= ord(kill) < 65127 or 65128 <= ord(kill) < 65132 or
                65281 <= ord(kill) < 65313):
            return True

    def __judge_f(self, kill):
        if kill not in self.ignore and 65314 <= ord(kill) < 65377:
            return True

    def __judge_u(self, kill):
        if kill not in self.ignore and ord(kill) in u_range_list:
            return True

    def __judge_big_u(self, kill):
        if kill not in self.ignore and ord(kill) in U_range_list:
            return True
    
    def __judge_e(self, kill):
        if kill not in self.ignore and ord(kill) > 65535:
            return True

    def __judge_r(self, kill):
        """
        这里是从888断断续续的有占位符号 所以下面判断范围中小于888的都不用写了
        """
        if kill not in self.ignore and \
            888 <= ord(kill) < 65535 and \
            ord(kill) not in u_range_list and \
            ord(kill) not in U_range_list and \
                not self.__judge_big_p(kill) and not self.__judge_f(kill):
            return True


def __get_color_front(string: str):
    # 这里是为了传入数字也可以搞
    lower_string = str(string).lower()
    if lower_string in ['黑色', '黑', 'black', 'k', '30', '000000']:
        return 30
    elif lower_string in ['红色', '红', 'red', 'r', '31', 'ff0000']:
        return 31
    elif lower_string in ['绿色', '绿', 'green', 'g', '32', "008000"]:
        return 32
    elif lower_string in ['黄色', '黄', 'yellow', 'y', '33', 'ffff00']:
        return 33
    elif lower_string in ['蓝色', '蓝', 'blue', 'b', '34', '0000ff']:
        return 34
    elif lower_string in ['紫色', '紫', 'purple', 'p', '35', '800080']:
        return 35
    elif lower_string in ['青蓝色', '青蓝', '靛色', '靛', 'cyan', 'c', '36', '00ffff']:
        return 36
    elif lower_string in ['白色', '白', 'white', 'w', '37', 'ffffff']:
        return 37
    elif lower_string in ['深灰色', '灰色', '灰', 'darkgrey', 'dg', '90', 'a9a9a9']:
        return 90
    elif lower_string in ['亮红色', '亮红', 'lightred', 'lr', '91']:
        return 91
    elif lower_string in ['亮绿色', '亮绿', 'lightgreen', 'lg', '92']:
        return 92
    elif lower_string in ['亮黄色', '亮黄', 'lightyellow', 'ly', '93']:
        return 93
    elif lower_string in ['亮蓝色', '亮蓝', 'lightblue', 'lb', '94']:
        return 94
    elif lower_string in ['粉色', '粉', 'pink', '少女粉', '猛男粉', '95', 'ffc0cb']:
        return 95
    elif lower_string in ['亮青色', '亮青', 'lightcyan', 'lc', '96']:
        return 96
    return None


def __get_color_background(string: str, background=True):
    # background 这里是为了排除字体颜色的英文单词给搞到了背景颜色
    lower_string = str(string).lower()
    if background is True and not lower_string.isdigit():
        return None
    if lower_string in ['黑色', '黑', 'black', 'k', '40']:
        return 40
    elif lower_string in ['红色', '红', 'red', 'r', '41']:
        return 41
    elif lower_string in ['绿色', '绿', 'green', 'g', '42']:
        return 42
    elif lower_string in ['黄色', '黄', 'yellow', 'y', '43']:
        return 43
    elif lower_string in ['蓝色', '蓝', 'blue', 'b', '44']:
        return 44
    elif lower_string in ['紫色', '紫', 'purple', 'p', '45']:
        return 45
    elif lower_string in ['青蓝色', '青蓝', '靛色', '靛', 'cyan', 'c', '46']:
        return 46
    elif lower_string in ['白色', '白', 'white', 'w', '47']:
        return 47
    return None


def __get_view_mode(mode: str, viewer=True):
    lower_string = str(mode).lower()
    if viewer is True and not lower_string.isdigit():
        return None
    if lower_string in ["reset", "重置", "0"]:
        return 0         # 不输出任何样式
    elif lower_string in ["bold", "加粗", "b", "1"]:
        return 1         # 加粗
    elif lower_string in ["disable", "禁用", "2"]:
        return 2         # 不知道这个有什么效果 看不出来
    elif lower_string in ["underline", "下划线", "u", "4"]:
        return 4          # 下划线
    elif lower_string in ["flash", "闪烁", "f", "5"]:
        return 5          # 闪烁
    elif lower_string in ["reverse", "反相", "r", "7"]:
        return 7          # 反相
    elif lower_string in ["invisible", "消失", "不可见", "i", "8"]:
        return 8          # 不可见
    elif lower_string in ["strikethrough", "删除线", "s", "9"]:
        return 9          # 删除线
    return None


def _trans_color(string: str, color: str = ""):
    color_map = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "purple": 35,
        "cyan": 36,
        "white": 37,
        "pink": 95
    }
    if color.lower() not in color_map:
        return string
    fresh_string = "".join(re.findall(">(.*?)<", string))
    return f"\033[{color_map[color]}m{fresh_string}\033[0m"


def _decorate_string(string: str):
    """
    这里只能装饰指定的颜色 只能修改字体 颜色装饰方案如下
    <red>xxx</red>          -- 红色
    <yellow>xxx</yellow>    -- 黄色
    <blue>xxx</blue>        -- 蓝色
    <green>xxx</green>      -- 绿色
    <cyan>xxx</cyan>        -- 青色
    <purple>xxx</purple>    -- 紫色
    <pink>xxx</pink>        -- 粉丝
    <black>xxx</black>      -- 黑色
    <white>xxx</white>      -- 白色
    """
    need_trans_strings = re.findall(r"<\w+>.*?</\w+>", string)
    for color_info_string in need_trans_strings:
        color = re.findall(r"<(\w+)>", color_info_string)[0]
        check_color = re.findall(r"</(\w+)>", color_info_string)[0]
        if color != check_color:  # 主要是为了避免 <red>xx</blue> 这种特殊情况
            continue
        could_replace = _trans_color(color_info_string, color)
        string = string.replace(color_info_string, could_replace)

    return string


def color_string(string: str = "", *args, **kwargs) -> str:
    """
    新加方案二 --> 直接可以修改对应块的颜色 -- 旧方案依旧保留 -- 毕竟旧方案可以设置背景和显示样式
             --> <red>今天</red>，我新增了一个<yellow>颜色</yellow>方案，让<blue>color string</blue>使用更加<green>方便.</green>

    给字体增加颜色 参数如下 使用直接  color_string("要加颜色的字体", 34, 5, 44) 需要加的颜色数字直接写下面 只有在规定范围内才能被提取 同一级写了多个只拿第一个
    如果传入英文 只有RGBYWPC 可以缩写 黑色black需要写全 大小写都无所谓  英文属于<<字体颜色>> 
    可以使用字典传参 设置字体颜色背景颜色 显示方式 如：{"f": "red", "b": "yellow", "v": "default", 'length': 20}
                                                # 这里限定了20个字符宽度(实际会大于20个只不过我这里做了处理) length 键弄l也可以
    :param string: 传入的字符串
    :param args  : 参数注解如下面所示  传入非字典类型的时候 只有第一个参数起作用在字体颜色上面  -->传入字典同下操作
    :param kwargs: 这里传入需要用 **{}
    :params f    : 字体颜色 -> (30, 黑色/black)(31, 红色/r/red)(32, 绿色/g/green)(33, 黄色/y/yellow)(34, 蓝色/b/blue)
     【注意这里的颜色,90以上的      (35, 紫色/p/purple)(36, 青蓝色/c/cyan)(37, 白色/w/white)(90, darkgrey)(91, lightred)
     可能只在windows起作用】       (92, lightgreen)(93, lightyellow)(94, lightblue)(95, pink)(96, lightcyan)
    :params b    : 背景颜色 -> (40, 黑色/black)(41, 红色/r/red)(42, 绿色/g/green)(43, 黄色/y/yellow)(44, 蓝色/b/blue)
                                (45, 紫色/p/purple)(46, 青蓝色/c/cyan)(47, 白色/w/white)
    :params v    : 显示方式 -> (0, 重置/reset)(1, 加粗/b/bold)(2, 禁止/disable)(4, 使用下划线/u/underline)(5, 闪烁/f/flash)
                                (7, 反相/r/reverse)(8, 不可见/i/invisible)(9, 删除线/s/strikethrough)
    """
    if not args and not kwargs and not string:
        return ""
    elif not args and not kwargs:
        return _decorate_string(string)
    base_string = '\033['
    if (string and kwargs) or (string and args and isinstance(args[0], dict)):
        if string and args and isinstance(args[0], dict):
            kwargs = args[0]
        length = kwargs.get('length', 0) or kwargs.get('l', 0)
        if isinstance(length, int) or (isinstance(length, str) and length.isdigit()):
            length = int(length)

        f = kwargs.get('f') or kwargs.get('font')
        if f: 
            f_string = __get_color_front(f)
            base_string += f"{f_string};" if f_string is not None else ""

        b = kwargs.get('b') or kwargs.get('background') or kwargs.get('backg')
        if b: 
            b_string = __get_color_background(b, background=False)
            base_string += f"{b_string};" if b_string is not None else ""

        v = kwargs.get('v') or kwargs.get('view') or kwargs.get("viewtype") or kwargs.get('vt')
        if v: 
            v_string = __get_view_mode(v, viewer=False)  
            base_string += f"{v_string:>02};" if v_string is not None else ""
        
        if base_string == '\033[':
            return string    # 如果操作一通后还是和原来字符串一样就不装饰
        if not kwargs.get('lenght') and not kwargs.get('l', 0):
            length = 0
        else:
            length -= len(string)
        return f"{base_string.strip(';')}m{string}{' ' * length}\033[0m"

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


def math_string(string: str) -> str:
    """
    这里是为了方便数学和化学之类的使用  规则(_下标符号   ^上标符) 这两个只管符号后面一个字符 (&xxx; 这个就是一个特殊符号)
    :param string: 传入的数学规则串 // 规则上下标标识符后一个字符变 如 Fe^2^+  --> Fe²⁺    H_2O  --> H₂O
                    &radic;4  --> √4    // 有一些字母不会有对应关系就没有改变规则原来是什么样就是什么样
    :return str  : 返回组装后的字符串
    """
    # 第一步提取出原字符串中可能是上下规则的字符
    # 第二步直接从对应的hash表获取替换关系
    new_string = string
    for rule in set(re.findall(r"\^\S|_\S|&\w+;", string)):
        getter = SUB_SUP_WORDS_HASH.get(rule)
        if getter:
            new_string = new_string.replace(rule, getter)
    return new_string
