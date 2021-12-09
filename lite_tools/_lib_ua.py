# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:28
# @Author : Lodge
import re
import random

from lite_tools._utils_uainfo import platform_data, browser_data, versions

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
    # 判断模版里面有多少个 {}
    rule = r"\{\}"  # 不写出来 写在re里面会给我报黄
    p_nums = len(re.findall(rule, template))
    # 提取版本号
    if not p_nums:
        return template   # 如果没有匹配到证明是完整的ua 不需要组合

    if browser in ["chrome", "edge"]:
        browser = "chromium"
    version = random.choice(versions.get(browser))

    if p_nums == 1:
        return template.format(version)
    elif p_nums == 2:
        return template.format(version, version)
    return template
