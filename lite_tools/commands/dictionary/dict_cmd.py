import os
import json
from typing import Optional, Tuple

from prettytable import PrettyTable
from lite_tools.logs import logger
from lite_tools.utils.json_download import get_goal_dir
from lite_tools.utils.lite_table import clear_screen, print_head
from lite_tools.tools.core.lite_string import color_string


def get_dict():
    base_root = get_goal_dir("dict", "dictionary.json", "http://static.litetools.top/source/json/dictionary.json")
    if not os.path.exists(base_root):
        logger.warning("字典源数据获取异常...")
        return
    with open(base_root, "r", encoding='utf-8') as fp:
        data = json.load(fp)
    return data


def circle_pang_pian(data: dict) -> Tuple[int, Optional[dict]]:
    """
    根据 偏旁部首 的笔画 选择 偏旁部首
    0 没有获取到
    1 普通查询
    2 生僻字查询
    """
    clear_screen()
    print(color_string(print_head("可以选择的偏旁部首笔画以及生僻字,下面选择的是偏旁部首笔画数以及 *生僻字"), "green"))
    print(color_string(f"{list(data.keys())}", "cyan"))
    bihua = input(">>> ")
    if not bihua or bihua not in data.keys():
        return 0, None
    if bihua == "*":
        return 2, data[bihua]
    return 1, data[bihua]


def circle_pian_zi(data: dict) -> Optional[dict]:
    """循环选择 偏旁部首"""
    clear_screen()
    print(color_string(print_head("选择查询的偏旁部首序号即可"), "green"))

    check_ind = {}
    split_num = need_split(data.keys())
    if split_num == 2:
        zi, check_ind = wrap_dict(data)
    else:
        zi = PrettyTable(["序号", "偏旁部首"])
        for ind, key in enumerate(data.keys()):
            zi.add_row([str(ind), key])
            check_ind[str(ind)] = key
    print(zi)
    ind = input(">>> ")
    if not ind or ind not in check_ind.keys():
        return
    return data[check_ind[ind]]


def wrap_dict(data: dict):
    check_ind = {}
    temp_save = []
    zi = PrettyTable(["序号", "偏旁部首", " 序号", " 偏旁部首"])
    for ind, key in enumerate(data.keys()):
        check_ind[str(ind)] = key
        if len(temp_save) < 4:
            temp_save.extend([str(ind), key])
        if len(temp_save) == 4:
            zi.add_row(temp_save)
            temp_save = []
    if len(temp_save) == 2:
        temp_save.extend(["", ""])
        zi.add_row(temp_save)
    return zi, check_ind


def need_split(keys):
    if len(keys) > 15:
        return 2
    return 1


def circle_zi(data: dict):
    """剩余部位的笔画"""
    clear_screen()
    print(print_head("选择除偏旁部首外剩余的笔画数,可选笔画数如下"))
    print(color_string(f"{list(data.keys())}", "cyan"))
    ind = input(">>> ")
    if not ind or ind not in data.keys():
        return
    return data[ind]


def circle_zi_detail(data: dict):
    clear_screen()

    split_num = need_split(data.keys())
    if split_num == 2:
        dt = PrettyTable(["字", "拼音", "五笔", " 字", " 拼音", " 五笔"])
        temp_save = []
        for word, info in data.items():
            if len(temp_save) < 6:
                temp_save.extend([word, info['pinyin'], info['wubi']])
            if len(temp_save) == 6:
                dt.add_row(temp_save)
                temp_save = []
        if len(temp_save) == 3:
            temp_save.extend(["", "", ""])
            dt.add_row(temp_save)
    else:
        dt = PrettyTable(["字", "拼音", "五笔"])
        for word, info in data.items():
            dt.add_row([word, info['pinyin'], info['wubi']])
    print(dt)


def dict_cmdline():
    json_file = get_dict()
    if not json_file:
        return
    mode, pians = circle_pang_pian(json_file)
    if mode == 1:  # 普通字
        zis = circle_pian_zi(pians)
        if not zis:
            return
        detail = circle_zi(zis)
        if not detail:
            return
        circle_zi_detail(detail)
    elif mode == 2:  # 生僻字
        circle_zi_detail(pians)
    else:   # 没有输入或者异常输入
        return


if __name__ == "__main__":
    dict_cmdline()
