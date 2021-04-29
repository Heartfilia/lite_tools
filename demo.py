# -*- coding: utf-8 -*-
import time
from lite_tools import get_time, get_ua, get_navigator, try_get, try_get_by_name, timec

# about time  ==> get_time  timer

# print(get_time())                                              # 1617702062
# print(get_time(cursor=-10))                                    # 1616838062
# print(get_time(cursor=7, double=True))                         # 1618306862.682278
# print(get_time(cursor=7, fmt=True))                            # 2021-04-13 17:41:02
# print(get_time(double=True))                                   # 1617701814.704276
# print(get_time(fmt=True))                                      # 2021-04-06 17:36:54
# print(get_time(fmt=True, fmt_str="%Y::%m::%d::"))              # 2021::04::06::
# print(get_time(1617701814))                                    # 2021-04-06 17:36:54   
# print(get_time("2021-04-06 17:36", double=True, fmt_str="%Y-%m-%d %H:%M"))  # 1617701760.0  时间格式需要用fmt_str来对应 默认样式无须再写
# print(get_time("2021-04-06 17:36:54", double=True))            # 1617701814.0
# print(get_time("1617701814"))                                  # 2021-04-06 17:36:54   support string too
# print(get_time(1617701814, fmt_str="%Y::%m::%d::%H~%M~%S"))    # 2021::04::06::17~36~54
# timer 是一个装饰器 只用于统计被装饰的函数耗时 日志等级为 debug

@timec    # time count
def run(name):
    time.sleep(0.2)
    print(f'hello {name} done')   # hello lite-tools done
run('lite-tools')   # 2021-04-27 09:20:01.949 | DEBUG    | lite_tools.time_info:inner:84 - >>> [run] -- cost time:0.20811


# about ua  ==> get_ua   //  get_navigator

# print(get_ua())                            # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2705.69 Safari/537.36
# print(get_ua('linux', 'android', 'win', 'macos', 'ios'))   # 之前用的库比较老 现在手动添加了一些比较近一点的ua  
# 上面那个可选参数如上面的扩号
# 还有两个参数  pc  / mobile  对应了linux.macos.win / ios.android
# print(get_ua('pc'))      # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11
# print(get_ua('mobile'))  # Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36

# print(get_navigator())
# print(get_navigator('linux', 'android', 'win'))


# about try_get   // try_get_by_name
test_json = {
    "a": {
        "b": 1,
        "c": 2,
        "e": -3,
        "d": {
            "e": 3,
            "f": 4,
            "g": {
                "h": 6,
                "i": {
                    "j": {
                        "k": {
                            'l': {
                                'm': {
                                    'n': {
                                        'o': {
                                            'p': {
                                                'q': {
                                                    'r': {
                                                        's': {
                                                            't': {
                                                                'u': {
                                                                    'v': {
                                                                        'w': {
                                                                            'x': {
                                                                                'y': {
                                                                                    'z': {
                                                                                        'e': 10,
                                                                                        "oo": {
                                                                                            'e': {"yy": "test", "e": "good_test"}
                                                                                        }
                                                                                    },
                                                                                    'xx': [{"e": "newBee"}]
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "_e": -3,
        },
        "_b": -2,
    },
    "_a": -1
}

# print(try_get(test_json, 'a.d.e'))                 # 3   ==> support the Chain operation
# print(try_get(test_json, lambda x: x['a']['b']))   # 1   ==> support the lambda operation
# print(try_get(test_json, 'x'))                     # None  ==> not found      support `expected_type` too
# print(try_get(test_json, 'x', default="hello"))    # hello ==> if not found 'x', then set default result
# print(try_get_by_name(test_json, 'e', depth=10))                   # [-3, 3]       default depth = 50  this function return the list objection
print(try_get_by_name(test_json, 'e', in_list=False))               # [-3, 3, 10, {'yy': 'test', 'e': 'good_test'}, 'good_test'] 不获取列表下面的字典的参数
print(try_get_by_name(test_json, 'e'))                   # [-3, 3, 'newBee', 10, {'yy': 'test', 'e': 'good_test'}, 'good_test'] 可以获取列表里面的字典的下面的值 默认获取
# print(try_get_by_name(test_json, 'e', expected_type=int))          # [-3, 3, 10]   default depth = 50
# print(try_get_by_name(test_json, 'e', expected_type=(int, str)))   # [-3, 3, 10, 'good_test']   default depth = 50



from lite_tools import get_md5, get_sha, get_sha3, get_b64e, get_b64d


# about hashlib  ==> get_md5, get_sha, get_sha3  || default mode=256
s = "test_information"
# print(get_md5(s))                # 5414ffd88fcb58417e64ecec51bb3a6b
# print(get_md5(s, upper=True))    # 5414FFD88FCB58417E64ECEC51BB3A6B
# print(get_md5(s, to_bin=True))   # b'T\x14\xff\xd8\x8f\xcbXA~d\xec\xecQ\xbb:k'
# print(get_sha(s))                # d09869fdf901465c8566f0e2debfa3f6a3d878a8157e199c7c4c6dd755617f33
# print(get_sha(s, to_bin=True))   # b'\xd0\x98i\xfd\xf9\x01F\\\x85f\xf0\xe2\xde\xbf\xa3\xf6\xa3\xd8x\xa8\x15~\x19\x9c|Lm\xd7Ua\x7f3'
# print(get_sha(s, mode=1))        # ada5dfdf0c9a76a84958310b838a70b6fd6d01f6   # default mode=256  // mode: 1 224 256 384 512
# print(get_sha3(s))               # 9c539ca35c6719f546e67837ff37fe7791e53fe40715cd4da0167c78c9adc2e8
# print(get_sha3(s, to_bin=True))  # b'\x9cS\x9c\xa3\\g\x19\xf5F\xe6x7\xff7\xfew\x91\xe5?\xe4\x07\x15\xcdM\xa0\x16|x\xc9\xad\xc2\xe8'
# print(get_sha3(s, mode=1))       # return "" // SUPPORT: sha3_224 sha3_256 sha3_384 sha3_512// only need inputting: 224 256 384 512  # default mode=256 // mode: 224 256 384 512
# print(get_sha3(s, mode=384))     # 95c09e20a139843eae877a64cd95d6a629b3c9ff383b5460557aab2612682d4228d05fe41606a79acf5ae1c4de35160c


# about base64  ==> get_b64e, get_b64d
res_b64_encode = get_b64e(s)              
# print(res_b64_encode)          # dGVzdF9pbmZvcm1hdGlvbg==

res_b64_bin = get_b64e(s, to_bin=True)
# print(res_b64_bin)               # b'dGVzdF9pbmZvcm1hdGlvbg=='

res_b32_encode = get_b64e(s, mode=32)  # default mode=64  // mode: 16 32 64 85
# print(res_b32_encode)            # ORSXG5C7NFXGM33SNVQXI2LPNY======


res_b64_decode = get_b64d(res_b64_encode)
# print(res_b64_decode)            # test_information

res_b32_decode = get_b64d(res_b32_encode, mode=32)  # default mode=64  // mode: 16 32 64 85
# print(res_b32_decode)            # test_information

