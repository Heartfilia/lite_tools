# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:28
# @Author : Lodge
import os
import re
import json
import random

from lite_tools.utils import VERSION
from lite_tools.utils.lite_dir import lite_tools_dir
from lite_tools.utils.u_ua_info import platform_data, browser_data


__ALL__ = ["get_ua"]

"""
下面操作的实现逻辑如下

输入参数 ---随机选择--[浏览器]--->browser_data --随机选择--> versions ==> 可用ua
            |⌈``⌉                   ↑
            ||系|                   |
            ||统|                   |
            ↓⌊__⌋                   |
        platform_data --随机选择--[浏览器]
"""


def get_ua(*args) -> str:
    """
    下面的都是实际存在的浏览器版本 很多没有拓展 不过chrome的已经够用了
    :param args :  直接传如需要获取的平台名称 -- 可以传系统 可以传浏览器 如果是浏览器 就是pc端的
                    可以写pc/PC  mobile/MOBILE android macos linux ios win chrome ie  (火狐还没有支持)  
                    ==> eg. get_ua('win')  get_ua('chrome', 'ie')
    """
    template = browser_data.get("chrome")
    if args:
        mode = random.choice(args)
        if mode.lower() in platform_data:
            platform = platform_data.get(mode.lower())
            browser_dict = random.choice(platform)
            for browser, templates in browser_dict.items():
                if isinstance(templates, list):
                    template = random.choice(templates)
                else:
                    template = templates
            else:
                browser = "chrome"  # 走不到这里 但是不写这里 pycharm会标注pep8问题
        elif mode.lower() in browser_data:
            browser = mode.lower()
            template = browser_data.get(browser)
        else:
            browser = "chrome"
    else:
        browser = "chrome"

    return judge_ua(browser, template)
    

def judge_ua(browser, template) -> str:
    # 判断模版里面是否需要替换
    p_nums = re.search(r"\{tag}", template)
    if not p_nums:
        return template   # 如果没有匹配到证明是完整的ua 不需要组合

    if browser in ["chrome", "edge"]:
        browser = "chromium"
    version = random.choice(get_versions().get(browser))

    return template.format(tag=version)


__UA_CACHE: dict = {}   # 尽量减少io读取 用空间换时间


def get_versions() -> dict:
    global __UA_CACHE
    if __UA_CACHE:
        return __UA_CACHE

    ua_path = os.path.join(lite_tools_dir(), "browser", "ua_version.json")
    if not os.path.exists(ua_path):
        from lite_tools.utils.u_ua_info import versions
        __UA_CACHE = versions
    else:
        try:
            with open(ua_path, 'r', encoding='utf-8') as fp:
                __UA_CACHE = json.load(fp)
        except Exception as err:
            _ = err
            from lite_tools.utils.u_ua_info import versions
            __UA_CACHE = versions

    return __UA_CACHE


def lite_ua(name=None) -> str:
    base_ua = f"python-lite-tools/{VERSION} Based On Script Engine"
    if name is not None:
        base_ua = f"{base_ua} {name}"
    return base_ua


if __name__ == "__main__":
    print(get_ua())
    print(get_ua('mobile'))
    print(get_ua('win'))
    print(get_ua('linux'))
    print(get_ua('ios'))
    print(get_ua('pc'))
    print(get_ua('chrome'))
    print(get_ua('edge'))
    print(get_ua('mac'))
