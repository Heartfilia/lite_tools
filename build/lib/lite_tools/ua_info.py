# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:28
# @Author : Lodge
import random


def get_ua(*args, **kwargs):
    """下面的都是实际存在的浏览器版本 很多没有拓展 不过chrome的已经够用了"""
    obj_list = []
    if 'pc' in args or 'PC' in args:
        obj_list = ua_pc
    elif 'mobile' in args or 'MOBILE' in args:
        obj_list = ua_mobile
    else:
        for plt in args:
            if plt.lower() == 'android':
                obj_list += ua_android
            if plt.lower() == 'macos':
                obj_list += ua_macos
            if plt.lower() == 'linux':
                obj_list += ua_linux
            if plt.lower() == 'ios':
                obj_list += ua_ios
            if plt.lower() == 'win':   # 这里还缺少firefox版本 后续增加现在这个和chrome相等
                obj_list += ua_win
            if plt.lower() == 'chrome':
                obj_list += ua_chrome
            if plt.lower() == 'ie':
                obj_list += ua_ie
        if not obj_list:
            obj_list = ua_win
    random_ua = random.choice(obj_list)
    del obj_list
    return random_ua

chrome_version = [
    '92.0.4515.43', '91.0.4472.101', '91.0.4472.19', '90.0.4430.24', '89.0.4389.23', '88.0.4324.96', '88.0.4324.27', '87.0.4280.88', '87.0.4280.20',
    '86.0.4240.22', '85.0.4183.87', '85.0.4183.83', '85.0.4183.38', '84.0.4147.30', '83.0.4103.39', '83.0.4103.14', '81.0.4044.138', '81.0.4044.69',
    '81.0.4044.20', '80.0.3987.106', '80.0.3987.16'
]

android_base = [
    'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67',
    'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67',
    'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67',
    'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67',
    'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36',
]

ua_ios = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 Edg/91.0.4472.124',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/91.0.4472.124',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
]

chrome_base = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36'
edge_base = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36 Edg/{}.0.864.67'

# version 80+
ua_chrome = [chrome_base.format(version) for version in chrome_version]   
ua_edge = [edge_base.format(version, version[:2]) for version in chrome_version]
ua_android = [android.format(version) for version in chrome_version for android in android_base]


ua_ie = [
    'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; Trident/7.0; .NET4.0E; .NET4.0C)'
]  # version 11

ua_linux = [
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/51.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.2922.66 Safari/537.36',
    'Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.2792.97 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/60.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.3578.98 Safari/537.36',
]

ua_macos = [
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_9_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/80.0.963.56 Safari/535.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.3626.121 Safari/537.36'
]

ua_win = ua_chrome + ua_edge
ua_pc = ua_win   # 暂时先不支持mac和linux  但是可以独立调用
ua_mobile = ua_ios + ua_android