# -*- coding: utf-8 -*-
import time
from lite_tools import get_time, get_ua, try_get, try_get_by_name, timec

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
# print(get_ua('linux', 'android', 'win', 'macos', 'ios'))   # 之前用的库比较老 现在手动添加了一些比较近一点的ua  # 也可以指定chrome、ie  不过资源不全 不过保证是真实浏览器的  firefox还没有搜集 目前chrome=win 
# 上面那个可选参数如上面的扩号
# 还有两个参数  pc  / mobile  对应了linux.macos.win / ios.android
# print(get_ua('pc'))      # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11
# print(get_ua('mobile'))  # Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36

# 下面的在新特性中移除了
# print(get_navigator())   # 这东西好像没用 ua部分已经替换了自己搜集的资源 不用第三方包了
# print(get_navigator('linux', 'android', 'win'))  # # 这东西好像没用 ua部分已经替换了自己搜集的资源 不用第三方包了

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

# print(try_get(test_json, 'a.d.e'))                 # 3   ==> support the Chain operation  推荐这个写法 可以设置默认值 可以设置期望值类型
# print(try_get(test_json, lambda x: x['a']['b']))   # 1   ==> support the lambda operation 
# print(try_get(test_json, 'x'))                     # None  ==> not found      support `expected_type` too
# print(try_get(test_json, 'x', "hello"))            # hello ==> if not found 'x', then set default result
# print(try_get_by_name(test_json, 'e', depth=10))       # [-3, 3]       default depth = 50  this function return the list objection
# print(try_get_by_name(test_json, 'e', in_list=False))    # [-3, 3, 10, {'yy': 'test', 'e': 'good_test'}, 'good_test'] 不获取列表下面的字典的参数
# print(try_get_by_name(test_json, 'e'))                   # [-3, 3, 'newBee', 10, {'yy': 'test', 'e': 'good_test'}, 'good_test'] 可以获取列表里面的字典的下面的值 默认获取
# print(try_get_by_name(test_json, 'e', expected_type=int))          # [-3, 3, 10]   default depth = 50
# print(try_get_by_name(test_json, 'e', expected_type=(int, str)))   # [-3, 3, 10, 'good_test']   default depth = 50

# try_get_by_name 新增特性 过滤器 --> 获取【同级】关系 要获取的值太多需要通过同级关系判断的情况 可以直接传入json字符串

# 可以格式化一下去判断关系 过滤关系可以选择的条件同python的普通运算符 = != > < >= <=   (== 这个效果同 = 做了兼容的)
# 字符串得包裹住 -->   "describe<-'广告'"-->[√]      "describe<-广告"--> [×]
s = '{"code":0,"data":{"activated_benefit_num":4,"benefit_level_info_list":[{"benefit_list":[{"apply_type":1,"describe":"发布文章并选择投放广告，可获得创作收益，收益全部归创作者所有","message":"","name":"文章创作收益","status_code":3,"tag":"","type":1,"url":""},{"apply_type":1,"describe":"发布文章并勾选「声明原创」，可获得更多推荐与创作收益","message":"","name":"文章原创","status_code":3,"tag":"","type":2,"url":""},{"apply_type":1,"describe":"发布横版视频并声明「原创」，产生播放量后，将按照平台规则计算创作收益","message":"","name":"视频创作收益","status_code":3,"tag":"","type":21,"url":""},{"apply_type":1,"describe":"发布横版视频并勾选「原创」，可获得更多推荐与创作收益，并享受原创保护","message":"","name":"视频原创","status_code":3,"tag":"","type":14,"url":""}],"describe":"基础权益","fans_num_threshold":0,"level":100,"type":0},{"benefit_list":[{"apply_type":1,"describe":"发布非转发抽奖类微头条，可获得创作收益，收益全部归作者所有","message":"","name":"微头条创作收益","status_code":0,"tag":"","type":5,"url":""},{"apply_type":1,"describe":"发布原创优质的回答，可获得创作收益，收益全部归作者所有","message":"","name":"问答创作收益","status_code":0,"tag":"","type":17,"url":""},{"apply_type":1,"describe":"开通问答创作收益后，发布回答并勾选「声明原创」，可获得更多推荐与创作收益","message":"","name":"问答原创","status_code":0,"tag":"","type":18,"url":""}],"describe":"百粉权益","fans_num_threshold":100,"level":150,"type":0},{"benefit_list":[{"apply_type":1,"describe":"权益开通后，读者可对作者发布的文章进行打赏，所得收益全部归作者所有","message":"","name":"图文赞赏","status_code":0,"tag":"","type":3,"url":""},{"apply_type":1,"describe":"权益开通后，观众可对作者发布的视频进行打赏，所得收益全部归作者所有","message":"","name":"视频赞赏","status_code":0,"tag":"","type":16,"url":""},{"apply_type":1,"describe":"全网第一手图片，紧追热点，作者免费使用版权图片，为创作赋能","message":"","name":"热点图库","status_code":0,"tag":"","type":15,"url":""},{"apply_type":2,"describe":"一种个性化的推广方式，支持自主设置广告素材并进行投放推广","message":"","name":"自营广告","status_code":0,"tag":"","type":4,"url":"cert_auth"}],"describe":"千粉权益","fans_num_threshold":1000,"level":200,"type":0},{"benefit_list":[{"apply_type":2,"describe":"发布多种形式付费内容，自主定价进行售卖，专栏被购买后作者可获得收益分成","message":"","name":"付费专栏","status_code":0,"tag":"","type":6,"url":"cert_auth"},{"apply_type":1,"describe":"发起微头条抽奖活动，增强与读者的互动，吸引新的粉丝","message":"","name":"头条抽奖","status_code":0,"tag":"","type":8,"url":""},{"apply_type":1,"describe":"支持作品中插入商品卡，商品通过卡片被购买并确认收货后，作者可获得佣金收益","message":"","name":"商品卡","status_code":0,"tag":"","type":9,"url":""},{"apply_type":2,"describe":"付费直播可以为直播课程设置价格，课程被购买后，作者可以获得收益分成","message":"","name":"付费直播","status_code":0,"tag":"","type":19,"url":"cert_auth"}],"describe":"万粉权益","fans_num_threshold":10000,"level":300,"type":0},{"benefit_list":[{"apply_type":1,"describe":"反馈内容可优先获得人工客服的响应，协助你更好地使用平台","message":"","name":"VIP客服","status_code":0,"tag":"","type":13,"url":""},{"apply_type":1,"describe":"平台官方作者社群，可享受平台动态优先了解、专属运营答疑、同领域作者互动","message":"","name":"创作者社群","status_code":0,"tag":"","type":11,"url":""}],"describe":"五万粉权益","fans_num_threshold":50000,"level":400,"type":0},{"benefit_list":[{"apply_type":1,"describe":"创作者成就表彰旨在奖励平台优质帐号，帮助创作者在平台收获更大影响力","message":"","name":"成就表彰","status_code":0,"tag":"","type":23,"url":""}],"describe":"十万粉成就","fans_num_threshold":100000,"level":500,"type":0}],"creator_project_fans_threshold":0,"creator_project_info":{"can_re_join":false,"message":"","status":0,"type":0},"credit_info":{"score":100,"score_change":0,"stick_id":0,"stick_id_list":[],"tip":""},"fans_num":9,"is_low_quality":false},"err_no":0,"message":"success"}'
# print(try_get_by_name(s, 'name', filter=["status_code=3"]))  # ['文章创作收益', '文章原创', '视频创作收益', '视频原创']
# print(try_get_by_name(s, 'name', filter=["status_code<3", "type=4"]))  # ['自营广告']
# print(try_get_by_name(s, 'describe', filter=["status_code<3", "type=4"]))  # ['一种个性化的推广方式，支持自主设置广告素材并进行投放推广']
# 新增特性 in: key<-value    not in: key>-value   # 这里是值 是否在key的值 中 

# print(try_get_by_name(s, 'describe', filter=["describe<#'广告'"]))  # 这里的意思就是describe里面包含了广告的describe的值 ['发布文章并选择投放广告，可获得创作收益，收益全部归创作者所有', '一种个性化的推广方式，支持自主设置广告素材并进行投放推广']
# print(try_get_by_name(s, 'describe', filter=["describe>#'广告'"]))  # 这里的意思就是describe里面不包含了广告的describe的值 ['基础权益', '百粉权益', '千粉权益', '万粉权益', '五万粉权益', '十万粉成就', '发布文章并勾选「声明原创」，可获得更多推荐与创作收益', '发布横版视频并声明「原创」，产生播放量后，将按照平台规则计算创作收益', '发布横版视频并勾选 「原创」，可获得更多推荐与创作收益，并享受原创保护', '发布非转发抽奖类微头条，可获得创作收益，收益全部归作者所有', '发布原创优质的回答，可获得创作收益，收益全部归作者所有', '开通问答创作收益后，发布回答并勾选「声明原创」，可 获得更多推荐与创作收益', '权益开通后，读者可对作者发布的文章进行打赏，所得收益全部归作者所有', '权益开通后，观众可对作者发布的视频进行打赏，所得收益全部归作者所有', '全网第一手图片，紧追热点，作者免费使用版权图片，为创作赋能', '发布多种形式付费内容，自主定价进行售卖，专栏被购买后作者可获得收益分成', '发起微头条抽奖活动，增强与读者的互动，吸引新的粉丝', '支持作品中插入商品卡，商品通过卡片被购买并确认收货后，作者可获得佣金收益', '付费直播可以为直播课程设置价格，课程被购买后，作者可以获得收益分成', '反馈内容可优先获得人工客服的响应，协助你更好地使用平台', '平台官方作者社群，可享受平台动态优先了解、专属运营答疑、同领域作者互动', '创作者成就表彰旨在奖励平台优质帐号，帮助创作者在平台收获更大影响力']
# print(try_get_by_name(s, 'name', filter=["describe<#'广告'"]))  # 这里的意思就是describe里面包含了广告的同级的name的值 ['文章创作收益', '自营广告']
# print(try_get_by_name(s, 'name', filter=["describe<#'广告'", 'status_code=0']))  # 这里就是表示多条件的并列关系的处理 ['自营广告']
# print(try_get_by_name(s, 'fans_num', filter=["is_low_quality=false"]))  # [9]  布尔或者空置判断按照json的结果或者python的结果一样的  <---json的样式
s2 = {"hello": [{"nihao": 222, "yes": True}, {"nihao": 333, "yes": False}, {"nihao": 444, "yes": None}]}
# print(try_get_by_name(s2, 'nihao', filter=["yes=False"]))               # [333]    <---- python 的样式
# print(try_get_by_name(s2, 'nihao', filter=["yes=true"]))                # [222]    <---- json   的样式
# print(try_get_by_name(s2, 'nihao', filter=["yes=None"]))                # [444]    <---- python 的样式
# print(try_get_by_name(s2, 'nihao', filter=["yes=null"]))                # [444]    <---- json   的样式

# 因为之前的那种<-  >- 很容易和右边的数字冲突 现在修改成#判断
# 新增key的结果是否在列表中  in：key#>iter   not in: key#<iter     # 这里是key的值 是否在iter中
print(try_get_by_name(s2, 'nihao', filter=["yes#>[true, null]"]))       # [222, 444]   python或者json格式混用都可以
print(try_get_by_name(s2, 'nihao', filter=["yes#>[True, None]"]))       # [222, 444]
print(try_get_by_name(s2, 'nihao', filter=["yes#>[True, None]", "nihao=444"]))  # [444]   # 同样支持多条件判断
print(try_get_by_name(s2, 'nihao', filter=["yes#<[true, null]"]))       # [333]

# log 这个报错参数只有在 有filter过滤器存在的时候并且过滤器错误会报错并停止程序  不用过滤器不会退出程序 只会报响应的错误 没有则不报错
# 这种会报错 因为广告不作为字符串处理 这里【不打印】日志【不会停止】程序 【打印了日志】会直接【终结程序】并报相应错误,无返回值->直接推出了全部程序
# print(try_get_by_name(s, 'name', filter=["describe<#广告"], log=True))  # 2021-05-28 10:37:01.777 | ERROR    | lite_tools.dict_parser:__do_filter_func:164 - 类型错误 --> name '广告' is not defined

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

