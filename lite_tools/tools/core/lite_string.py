# -*- coding: utf-8 -*-
import re
import os
import math
from urllib.parse import quote_plus
from typing import Optional, Union

from lite_tools.utils.u_code_range import u_range_list, U_range_list
from lite_tools.utils.u_sub_sup_string import SUB_SUP_WORDS_HASH
"""
这里是把常用的先弄了出来 后续还可以拓展举铁参考见code_range   ***这里清理字符串还是有bug  还需要调试***
"""
__ALL__ = ["clean_html", "CleanString", "color_string", "math_string", "PrettySrt"]


class PrettySrt:
    _RE_RAW = re.compile(r"(\d+.*?)\n(\d{2}:\d{2}:\d{2},\d{1,3} --> \d{2}:\d{2}:\d{2},\d{1,3})\n(.*)\n?")

    def __init__(self, srt_file: str) -> None:
        self._srt = self._check_and_get(srt_file)
        self._source_root = srt_file  # 记录源文件路径 或许能用到
        self._start = 1   # 会被重写
        self._rows = []
        self._init_rows()
        self._last_ind = 0  # 记录最后一个序号/会被更新 有的程序会
        self._result = ""  # 缓存处理好的结果

    def _update_last_ind(self):
        if self._rows:
            for row in self._rows[::-1]:  # 倒着查
                if row and len(row) == 3:
                    last_item = row[-1][0]
                    sort_id_obj = re.search(r"^(\d+)", last_item)
                    if sort_id_obj:
                        self._last_ind = int(sort_id_obj.group(1))
                        break

    @staticmethod
    def _check_and_get(srt: str) -> str:
        """
        判断文件是否存在 并获取到 文本信息
        """
        if not os.path.exists(srt):
            raise Exception(f"[{srt}]文件未找到")
        with open(srt, "r", encoding='utf-8') as fr:
            content = fr.read()
        return content

    @staticmethod
    def _string_time_to_ts(ot: str) -> Union[int, float]:
        """
        把 xx:xx:xx,xxx 的时间 换成对应的 秒 数
        """
        result_t = 0
        base_time = ot.split(",")
        if len(base_time) == 2:
            result_t += float(f"0.{base_time[1]}")
        h, m, s = base_time[0].split(":")
        result_t += int(h) * 3600
        result_t += int(m) * 60
        result_t += int(s)
        return result_t

    @staticmethod
    def _handle_ts_to_string(t: float) -> str:
        """
        这里是我用自己写的方法实现的， 没有用其它包 应该有 但是我直接用这个好了
        :param t:
        :return:
        """
        base_time_fmt = "{H:>02}:{M:>02}:{S:>02},{F:<03}"
        new_h = t // 3600
        new_m = (t % 3600) // 60
        new_s = (t % 3600) % 60
        fs = str(t).split(".")
        fs = str(fs[-1])[:3] if len(fs) > 1 else "000"
        return base_time_fmt.format(H=int(new_h), M=int(new_m), S=int(new_s), F=fs)

    def _combine_new_time_line(self, start_ts: float, end_ts: float) -> str:
        """
        把 float, float  ->  xx:xx:xx,xxx --> xx:xx:xx,xxx
        """
        start = self._handle_ts_to_string(start_ts)
        end = self._handle_ts_to_string(end_ts)
        return f"{start} --> {end}"

    def _trans_time(self, time_line: str):
        """
        传入的是 xx:xx:xx,xxx --> xx:xx:xx,xxx
        """
        time_start, time_end = time_line.split("-->")  # 需要处理前后的空格
        start_ts = self._string_time_to_ts(time_start.strip())
        end_ts = self._string_time_to_ts(time_end.strip())
        return start_ts, end_ts

    def _init_rows(self):
        self._rows = self._RE_RAW.findall(self._srt)

    def pretty_number(self, start: int = 1, clear_other: bool = True):
        """
        美化每一行的序号
        :param start       : 配置开始的序号 默认从1开始
        :param clear_other : 清理其它信息，比如有些时候后面会跟发音人信息，是否需要清理掉 默认清理
        """
        self._start = start    # 如果配置了这里 那么后面重新排的时候会从这里开始
        if self._rows and self._rows[0] and len(self._rows[0]) == 3:
            if not self._rows[0][0].startswith(str(start)):
                # 如果第一行不是以需要的行号开始 那么需要更新每一行

                for ind, row in enumerate(self._rows):
                    this_row_line = row[0]
                    this_row_line = re.sub(r"^\d+", str(start), this_row_line)
                    new_line = (this_row_line,) + row[1:]
                    self._rows[ind] = new_line

                    start += 1

            if clear_other:
                for ind, row in enumerate(self._rows):
                    this_row_line = row[0]
                    if not re.search(r"^\d+$", this_row_line):
                        sort_id = re.sub(r"^(\d+).*", r"\1", this_row_line)
                        new_line = (sort_id,) + row[1:]
                        self._rows[ind] = new_line

        # 不管是否存在行 都需要返回对象
        self._update_last_ind()  # 不管什么操作 都要记录一下最后的序号 用作结尾
        return self

    def pretty_words(self, max_line: int = 0, clear_back: str = "。，！？丶、"):
        """
        用来美化每一行的数据
        :param max_line  : 用来限制每一行最多多少字，超过的将会进行分行 - 同时把时间也根据字数平均分配
        :param clear_back: 用来清理每一行结尾的特殊字符的（这里不要随便用字，容易把字去掉，用符号即可）
        """
        change = False
        new_row = []  # 缓存
        if self._rows:
            for ind, row in self._rows:
                if len(row) == 3:
                    # ind 行这里不做记录 因为后面要重新排序
                    now_row_number = row[0]
                    this_row_line_reg = re.search(r"^(\d+)", now_row_number)
                    if this_row_line_reg:
                        now_start_number = int(this_row_line_reg.group(1))
                    else:
                        now_start_number = 1
                    time_line = row[1]
                    words_line = row[2]

                    if clear_back:
                        rule = f"[{clear_back}]+$"
                        words_line = re.sub(rule, "", words_line)  # 先清理一次 避免后面判断误伤

                    if words_line and max_line and len(words_line) > max_line:
                        change = True
                        # 需要分隔处理的情况
                        split_number = math.ceil(len(words_line) / max_line)
                        start_ts, end_ts = self._trans_time(time_line)
                        ts_duration = end_ts - start_ts
                        each_word_ts = round(ts_duration / len(words_line))   # 每一个字多少时间

                        for ind_line in range(split_number):
                            new_words = words_line[max_line * ind_line:max_line * (ind_line + 1)]
                            spend_ts = each_word_ts * len(new_words)
                            new_end_ts = start_ts + spend_ts
                            new_time_row = self._combine_new_time_line(start_ts, new_end_ts)
                            new_row.append((now_start_number, new_time_row, new_words))
                            start_ts = min(new_end_ts, end_ts)
                            now_start_number += 1
                    else:
                        if clear_back:
                            new_row.append((row[0], row[1], words_line))  # 因为前面已经清理了一次了
                        else:
                            new_row.append(row)

        if change:
            # 如果有改动 这里需要重新排行号
            results = []
            new_start = self._start
            for row in new_row:
                results.append((str(new_start),) + row[1:])
                new_start += 1

            self._rows = results
            # 排完行号后重新记录新的尾行号
            self._update_last_ind()

        return self

    def add_tail_ind(self):
        """
        因为有的工具 最后一行不多一个 空序号行 合成到视频里面容易丢失最后一段话 所以这里是做的兼容 补最后一行序号的
        """
        if self._rows and len(self._rows[-1]) != 1:
            self._last_ind += 1
            self._rows.append((str(self._last_ind),))  # 最后一行独立判断

    def _handle_string(self):
        result = ""
        if not self._rows:
            template = "{ind_line}\n{time_range}\n{words}\n\n"
            for row in self._rows:
                if len(row) == 3:
                    result += template.format(ind_line=row[0], time_range=row[1], words=row[2])
                elif len(row) == 1:
                    result += f"{row[0]}\n"  # 结尾补空行
        self._result = result

    def show(self):
        """
        展示现在改好的结果
        """
        self._handle_string()
        print(self._result)

    def save(self, save_path: str = None, encoding: str = "utf-8"):
        """
        将处理好的保存下来
        :param save_path : 如果不传入，将会是原路径覆盖
        :param encoding  : 默认存的格式
        """
        self._handle_string()
        with open(save_path, "w", encoding=encoding) as fw:
            fw.write(save_path)


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
    def _scanner(string: str):
        jar = set(filter(lambda x: not x.isalpha() or not x.isdigit(), string))
        return jar

    def __judge_x(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and (0 <= ord(kill) < 7 or 14 <= ord(kill) < 32 or 127 <= ord(kill) < 161):
            return True
        return None

    def __judge_s(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and 7 <= ord(kill) < 14:
            return True
        return None

    def __judge_p(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and (
                32 <= ord(kill) < 48 or 58 <= ord(kill) < 65 or 91 <= ord(kill) < 97 or 123 <= ord(kill) < 127):
            return True
        return None

    def __judge_big_p(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and (
            8208 <= ord(kill) < 8232 or 8240 <= ord(kill) < 8287 or 12289 <= ord(kill) < 12310 or
            65072 <= ord(kill) < 65107 or 65108 <= ord(kill) < 65127 or 65128 <= ord(kill) < 65132 or
                65281 <= ord(kill) < 65313):
            return True
        return None

    def __judge_f(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and 65314 <= ord(kill) < 65377:
            return True
        return None

    def __judge_u(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and ord(kill) in u_range_list:
            return True
        return None

    def __judge_big_u(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and ord(kill) in U_range_list:
            return True
        return None

    def __judge_e(self, kill: str) -> Optional[bool]:
        if kill not in self.ignore and ord(kill) > 65535:
            return True
        return None

    def __judge_r(self, kill: str) -> Optional[bool]:
        """
        这里是从888断断续续的有占位符号 所以下面判断范围中小于888的都不用写了
        """
        if kill not in self.ignore and \
            888 <= ord(kill) < 65535 and \
            ord(kill) not in u_range_list and \
            ord(kill) not in U_range_list and \
                not self.__judge_big_p(kill) and not self.__judge_f(kill):
            return True
        return None


def clean_html(html: str, white_tags: list = None) -> str:
    """
    采用了米乐大佬的包 usepy
    """
    try:
        from usepy import useCleanHtml
    except ImportError:
        from lite_tools.utils.pip_ import install

        install('usepy')
        from usepy import useCleanHtml
    content = useCleanHtml(html, white_tags)
    return content


def __get_color_front(string: str) -> Optional[int]:
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


def __get_color_background(string: str, background: bool = True) -> Optional[int]:
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


def __get_view_mode(mode: str, viewer=True) -> Optional[int]:
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
    return 0


def _trans_color(string: str, color: str = "") -> str:
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


def _decorate_string(string: str) -> str:
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
        if not kwargs.get('length') and not kwargs.get('l', 0):
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


def cookie_s2d(cookie: str) -> dict:
    """
    把字符串cookie转换成字典格式 a=1;b=2 -> {"a": "1", "b": "2"}
    """
    if not cookie:
        return {}
    # return dict(map(
    #     lambda x: (x.strip().split('=', 1)[0], x.strip().split('=', 1)[1]),
    #     cookie.strip().rstrip(';').split(';')
    # ))

    # 发现有的cookie是 xxxx 没有=的 这种cookie直接放进去就好了
    cookies = {}
    for each in cookie.strip().rstrip(';').split(';'):
        if "=" not in each:
            cookies[""] = each
        else:
            k, v = each.split("=", 1)
            cookies[k] = v
    return cookies


def cookie_d2s(cookie: Union[dict, list], space: bool = False) -> str:
    """
    把字典格式的cookie转换成字符串格式 {"a": "1", "b": "2"} -> a=1;b=2
    或者 把[{"name":"a","value":1}] ->a=1
    space: 如果需要cookie后面添加空格的配置这个
    """
    if not cookie:
        return ""
    space_key = "+++++" if space else ""
    if isinstance(cookie, dict):
        ck_s = f';{space_key}'.join(map(lambda x: f"{x[0]}={quote_plus(x[1])}".lstrip("="), cookie.items()))
    else:
        ck_s = f';{space_key}'.join(map(lambda x: f"{x['name']}={quote_plus(x['value'])}", cookie))
    ck_s = ck_s.replace(" ", '%20')
    if space:
        ck_s = ck_s.replace(f";{space_key}", '; ')
    return ck_s


def pretty_indent(s: str, indent: int = 2, remove_empty_line: bool = True, strict_indent: bool = False):
    """
    这个地方主要是把 那种大缩进的代码去掉空格 这样子更加好看啊
    :param s         : 传入的多行字符串
    :param indent    : 默认最小缩进是 2 空格
    :param remove_empty_line : 是否移除空白行
    :param strict_indent     : 严格缩进 为（True的话一定得是以每一行的最小共同空格数进行缩进） (默认False:已经顶格的数据跳过，处理其它的)
    """
    each_row = s.split("\n")
    min_space = 0   # 最小需要剔除的空格数量

    temp_slice = []   # 因为替换了\t的后续替换需要用到
    for row in each_row:
        start_tab = re.search("^(\t\t)", row)
        if start_tab:
            start_tab_string = start_tab.group(1).count("\t")
            row = re.sub(r"^\t+", " " * start_tab_string * indent, row)

        if not row.strip():
            if not remove_empty_line:
                temp_slice.append("")
            continue
        else:
            empty_len = len(row) - len(row.lstrip())
            if strict_indent and empty_len == 0:   # 严格模式 必须保证用最小单位进行处理
                min_space = 0   # 这时候直接就不需要处理了 后续流程也不走了
                break
            if min_space == 0 or empty_len < min_space:
                min_space = empty_len
            temp_slice.append(row)   #

    if min_space == 0:  # 如果无须改动 直接返回
        return s

    new_slice = map(lambda xl: xl.removeprefix(" " * min_space), temp_slice)

    return "\n".join(new_slice)
