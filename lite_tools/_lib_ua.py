# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:28
# @Author : Lodge
import random
import json as _json

from lite_tools._lib_dict_parser import match_case
from lite_tools._utils_uainfo import platform_data, browser_data

__ALL__ = ["init_ua", "get_ua", "update_ua"]

ua_win = []
ua_pc = []
ua_mobile = []
ua_linux = []
ua_ie = []
ua_macos = []
ua_ios = []
ua_android = []
ua_chrome = []
ua_edge = []


def __init__ua(kwargs: dict = None):
    # 暂时先不支持mac和linux  但是可以独立调用
    # 下面 的数据先写死 以后找到规律了再像chrome那样存模板和版本拼接
    if kwargs is None:
        kwargs = {}
    inner_ua_ie = [
        'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; Trident/7.0; .NET4.0E; .NET4.0C)'
    ]  # version 11

    inner_ua_linux = [
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/51.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.2922.66 Safari/537.36',
        'Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.2792.97 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/60.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.3578.98 Safari/537.36',
    ]

    inner_ua_macos = [
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_9_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/80.0.963.56 Safari/535.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.3626.121 Safari/537.36'
    ]

    inner_ua_ios = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 Edg/91.0.4472.124',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/91.0.4472.124',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    ]

    chrome_base = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36'
    edge_base = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36 Edg/{}.0.864.67'


def init_ua(**kwargs) -> None:
    """
    这里是初始化ua的 可以先在需要处理的文件头先运行这个地方 限定下面的get_ua的版本的控制
    这里只需要调用一次

    :params kwagrs:  version_max: 限定最大的chrome版本
                    version_min: 限定最小的chrome版本
                    version : 同versionm 也就是小限制的chrome版本
                    version_equal: 等于这版本的chrome
    """
    __init__ua(kwargs)


def get_ua(*args):
    """
    下面的都是实际存在的浏览器版本 很多没有拓展 不过chrome的已经够用了
    :param args :  直接传如需要获取的平台名称 -- 可以传系统 可以传浏览器 如果是浏览器 就是pc端的
                    可以写pc/PC  mobile/MOBILE android macos linux ios win chrome ie  (火狐还没有支持)  
                    ==> eg. get_ua('win')  get_ua('chrome', 'ie')
    """
    if args:
        mode = random.choice(args)
        if mode.lower() in platform_data:
            browser = random.choice(platform_data.get(mode.lower()))
        elif mode.lower()in browser_data:
            browser = mode.lower()
        else:
            browser = "chrome"
    else:
        browser = "chrome"
    


@match_case
def judge_ua(platform):
    return ""   # 这里默认返回chrome相关的资源


def judge_


def update_ua():
    """
    这里会有个同步线上的数据更新到本地数据 不过目前没有搭建稳定的资源库服务器 暂时搁置
    """


if __name__ == "__main__":
    get_ua('chrome', 'win', 'pc', 'linux', 'mac', 'ios', 'mobile', 'android', 'firefox', 'ie', 'opera', "edge")
