# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:28
# @Author : Lodge
import json
import random
from ._utils_uainfo import ua_data


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


def __init__ua(kwargs: dict={}):
    # 暂时先不支持mac和linux  但是可以独立调用
    # 下面 的数据先写死 以后找到规律了再像chrome那样存模板和版本拼接
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

    version_max = kwargs.get('version_max')  # version_less_than
    version_min = kwargs.get('version_min') # version_more_than
    version_equal = kwargs.get('version_equal')   # version_equal
    version_num = kwargs.get('version', 70)

    for now_version, versions in ua_data["chrome_version"].items(): 
        if version_max and version_min and version_min > version_max: continue  # 如果两个筛选都存在 并且要求大于的版本值比要求小于的版本值还要大就跳过
        elif version_max and now_version > version_max: continue
        elif version_min and now_version < version_min: continue
        elif version_equal and now_version != version_equal: continue

        if not version_max and not version_min and not version_equal and (now_version < version_num): continue
        # 
        for version in versions:
            ua_chrome.append(chrome_base.format(version))
            ua_win.append(chrome_base.format(version))
            ua_pc.append(chrome_base.format(version))
            ua_edge.append(edge_base.format(version, version[:2]))
            ua_win.append(edge_base.format(version, version[:2]))
            ua_pc.append(edge_base.format(version, version[:2]))
            for android in ua_data["android_base"]:
                ua_android.append(android.format(version))
                ua_mobile.append(android.format(version))
    
    # 这里是给上面筛选了全部被pass掉了后加的默认值
    if not ua_chrome or not ua_win or not ua_pc or not ua_mobile or not ua_android: 
        __set_default(chrome_base, edge_base)

    for _uaios in inner_ua_ios: ua_ios.append(_uaios)
    for _uaie in inner_ua_ie: ua_ie.append(_uaie)
    for _ualinux in inner_ua_linux: ua_linux.append(_ualinux)
    for _uamacos in inner_ua_macos: ua_macos.append(_uamacos)


def init_ua(**kwargs) -> None:
    """
    这里是初始化ua的 可以先在需要处理的文件头先运行这个地方 限定下面的get_ua的版本的控制
    这里只需要调用一次

    :param kwagrs:  version_max: 限定最大的chrome版本
                    version_min: 限定最小的chrome版本
                    version : 同versionm 也就是小限制的chrome版本
                    version_equal: 等于这版本的chrome
    """
    __init__ua(kwargs)


def get_ua(*args):
    """
    下面的都是实际存在的浏览器版本 很多没有拓展 不过chrome的已经够用了
    版本控制试用 init_ua(这里面传入规定)  在全局调用一次即可 后续使用get_ua都直接用的这里的数据
    :param args :  直接传如需要获取的平台名称 
                    可以写pc/PC  mobile/MOBILE android macos linux ios win chrome ie  (火狐还没有支持)  
                    ==> eg. get_ua('win')  get_ua('chrome', 'ie')
    """
    if not ua_win or not ua_pc or not ua_mobile:
        # 这里是
        __init__ua()

    obj_list = []
    if 'pc' in args or 'PC' in args:
        obj_list = ua_pc
    elif 'mobile' in args or 'MOBILE' in args:
        obj_list = ua_mobile
    else:
        for plt in args:
            if plt.lower() == 'android': obj_list += ua_android
            if plt.lower() == 'macos': obj_list += ua_macos
            if plt.lower() == 'linux': obj_list += ua_linux
            if plt.lower() == 'ios': obj_list += ua_ios
            if plt.lower() == 'win': obj_list += ua_win   # 这里还缺少firefox版本 后续增加现在这个和chrome相等
            if plt.lower() == 'chrome': obj_list += ua_chrome
            if plt.lower() == 'ie': obj_list += ua_ie
        if not obj_list: obj_list = ua_win
    random_ua = random.choice(obj_list)
    del obj_list
    return random_ua


def __set_default(chrome_base, edge_base):
    ua_chrome.append(chrome_base.format(ua_data["default_version"]))
    ua_win.append(chrome_base.format(ua_data["default_version"]))
    ua_pc.append(chrome_base.format(ua_data["default_version"]))
    ua_edge.append(edge_base.format(ua_data["default_version"], ua_data["default_version"][:2]))
    ua_win.append(edge_base.format(ua_data["default_version"], ua_data["default_version"][:2]))
    ua_pc.append(edge_base.format(ua_data["default_version"], ua_data["default_version"][:2]))
    for android in ua_data["android_base"]:
        ua_android.append(android.format(ua_data["default_version"]))
        ua_mobile.append(android.format(ua_data["default_version"]))


def update_ua():
    """
    这里会有个同步线上的数据更新到本地数据 不过目前没有搭建稳定的资源库服务器 暂时搁置
    """
