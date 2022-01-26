# -*- coding: utf-8 -*-
import time
from lite_tools import get_time, time_count

# about time  ==> get_time  timer

print(get_time())                                              # 1617702062
# cursor 支持年月日时分秒的设置方式 但是同时设置多个只会最大范围的那个起效过 如 cursor="-2Y3m" 只会-2Y 有效果 两年前的意思
print(get_time(cursor=-10))                                    # 1616838062
print(get_time(cursor=7, double=True))                         # 1618306862.682278
print(get_time(cursor=7, fmt=True))                            # 2021-04-13 17:41:02
print(get_time(double=True))                                   # 1617701814.704276
print(get_time(fmt=True))                                      # 2021-04-06 17:36:54
print(get_time(fmt="%Y::%m::%d::"))                            # 2021::04::06::
print(get_time(1617701814))                                    # 2021-04-06 17:36:54   
print(get_time("2021-04-06 17:36", double=True, fmt="%Y-%m-%d %H:%M"))  # 1617701760.0  时间格式需要用fmt_str来对应 默认样式无须再写
print(get_time("2021-04-06 17:36:54", double=True))            # 1617701814.0
print(get_time("1617701814"))                                  # 2021-04-06 17:36:54   support string too
print(get_time(1617701814, fmt="%Y::%m::%d::%H~%M~%S"))    # 2021::04::06::17~36~54
# time_count 是一个装饰器 只用于统计被装饰的函数耗时 日志等级为 debug


@time_count
def run(name):
    time.sleep(0.2)
    print(f'hello {name} done')   # hello lite-tools done


run('lite-tools')   # 2021-04-27 09:20:01.949 | DEBUG    | xxx:84 - >>> [run] -- cost time:0.20811
