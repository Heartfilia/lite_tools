from lite_tools import get_ua


print(get_ua())              # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2705.69 Safari/537.36
print(get_ua('chrome'))      # 这个现在和win和不写是一样的结果 后面会把firefox和其它ua补充上
print(get_ua('linux', 'android', 'win', 'macos', 'ios'))   # 之前用的库比较老 现在手动添加了一些比较近一点的ua  # 也可以指定chrome、ie  不过资源不全 不过保证是真实浏览器的  firefox还没有搜集 目前chrome=win 
# 上面那个可选参数如上面的扩号
# 还有两个参数  pc  / mobile  对应了linux.macos.win / ios.android
print(get_ua('pc'))      # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11
print(get_ua('mobile'))  # Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36
