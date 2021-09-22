# -*- coding: utf-8 -*-
from lite_tools import try_get, try_get_by_name

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

print(try_get(test_json, 'a.d.e'))                 # 3   ==> support the Chain operation  **推荐**这个写法 可以设置默认值 可以设置期望值类型
print(try_get(test_json, lambda x: x['a']['b']))   # 1   ==> support the lambda operation 
print(try_get(test_json, 'x'))                     # None  ==> not found      support `expected_type` too
print(try_get(test_json, 'x', "hello"))            # hello ==> if not found 'x', then set default result  **设置默认**返回值**
print(try_get_by_name(test_json, 'e', depth=10))       # [-3, 3]       default depth = 50  this function return the list objection
print(try_get_by_name(test_json, 'e', in_list=False))    # [-3, 3, 10, {'yy': 'test', 'e': 'good_test'}, 'good_test'] 不获取列表下面的字典的参数
print(try_get_by_name(test_json, 'e'))                   # [-3, 3, 'newBee', 10, {'yy': 'test', 'e': 'good_test'}, 'good_test'] 可以获取列表里面的字典的下面的值 默认获取
print(try_get_by_name(test_json, 'e', expected_type=int))          # [-3, 3, 10]   default depth = 50
print(try_get_by_name(test_json, 'e', expected_type=(int, str)))   # [-3, 3, 10, 'good_test']   default depth = 50

# try_get_by_name 新增特性 过滤器 --> 获取【同级】关系 要获取的值太多需要通过同级关系判断的情况 可以直接传入json字符串

# 可以格式化一下去判断关系 过滤关系可以选择的条件同python的普通运算符 = != > < >= <=   (== 这个效果同 = 做了兼容的)
# 字符串得包裹住 -->   "describe<-'广告'"-->[√]      "describe<-广告"--> [×]
s = '{"code":0,"data":{"activated_benefit_num":4,"benefit_level_info_list":[{"benefit_list":[{"apply_type":1,"describe":"发布文章并选择投放广告，可获得创作收益，收益全部归创作者所有","message":"","name":"文章创作收益","status_code":3,"tag":"","type":1,"url":""},{"apply_type":1,"describe":"发布文章并勾选「声明原创」，可获得更多推荐与创作收益","message":"","name":"文章原创","status_code":3,"tag":"","type":2,"url":""},{"apply_type":1,"describe":"发布横版视频并声明「原创」，产生播放量后，将按照平台规则计算创作收益","message":"","name":"视频创作收益","status_code":3,"tag":"","type":21,"url":""},{"apply_type":1,"describe":"发布横版视频并勾选「原创」，可获得更多推荐与创作收益，并享受原创保护","message":"","name":"视频原创","status_code":3,"tag":"","type":14,"url":""}],"describe":"基础权益","fans_num_threshold":0,"level":100,"type":0},{"benefit_list":[{"apply_type":1,"describe":"发布非转发抽奖类微头条，可获得创作收益，收益全部归作者所有","message":"","name":"微头条创作收益","status_code":0,"tag":"","type":5,"url":""},{"apply_type":1,"describe":"发布原创优质的回答，可获得创作收益，收益全部归作者所有","message":"","name":"问答创作收益","status_code":0,"tag":"","type":17,"url":""},{"apply_type":1,"describe":"开通问答创作收益后，发布回答并勾选「声明原创」，可获得更多推荐与创作收益","message":"","name":"问答原创","status_code":0,"tag":"","type":18,"url":""}],"describe":"百粉权益","fans_num_threshold":100,"level":150,"type":0},{"benefit_list":[{"apply_type":1,"describe":"权益开通后，读者可对作者发布的文章进行打赏，所得收益全部归作者所有","message":"","name":"图文赞赏","status_code":0,"tag":"","type":3,"url":""},{"apply_type":1,"describe":"权益开通后，观众可对作者发布的视频进行打赏，所得收益全部归作者所有","message":"","name":"视频赞赏","status_code":0,"tag":"","type":16,"url":""},{"apply_type":1,"describe":"全网第一手图片，紧追热点，作者免费使用版权图片，为创作赋能","message":"","name":"热点图库","status_code":0,"tag":"","type":15,"url":""},{"apply_type":2,"describe":"一种个性化的推广方式，支持自主设置广告素材并进行投放推广","message":"","name":"自营广告","status_code":0,"tag":"","type":4,"url":"cert_auth"}],"describe":"千粉权益","fans_num_threshold":1000,"level":200,"type":0},{"benefit_list":[{"apply_type":2,"describe":"发布多种形式付费内容，自主定价进行售卖，专栏被购买后作者可获得收益分成","message":"","name":"付费专栏","status_code":0,"tag":"","type":6,"url":"cert_auth"},{"apply_type":1,"describe":"发起微头条抽奖活动，增强与读者的互动，吸引新的粉丝","message":"","name":"头条抽奖","status_code":0,"tag":"","type":8,"url":""},{"apply_type":1,"describe":"支持作品中插入商品卡，商品通过卡片被购买并确认收货后，作者可获得佣金收益","message":"","name":"商品卡","status_code":0,"tag":"","type":9,"url":""},{"apply_type":2,"describe":"付费直播可以为直播课程设置价格，课程被购买后，作者可以获得收益分成","message":"","name":"付费直播","status_code":0,"tag":"","type":19,"url":"cert_auth"}],"describe":"万粉权益","fans_num_threshold":10000,"level":300,"type":0},{"benefit_list":[{"apply_type":1,"describe":"反馈内容可优先获得人工客服的响应，协助你更好地使用平台","message":"","name":"VIP客服","status_code":0,"tag":"","type":13,"url":""},{"apply_type":1,"describe":"平台官方作者社群，可享受平台动态优先了解、专属运营答疑、同领域作者互动","message":"","name":"创作者社群","status_code":0,"tag":"","type":11,"url":""}],"describe":"五万粉权益","fans_num_threshold":50000,"level":400,"type":0},{"benefit_list":[{"apply_type":1,"describe":"创作者成就表彰旨在奖励平台优质帐号，帮助创作者在平台收获更大影响力","message":"","name":"成就表彰","status_code":0,"tag":"","type":23,"url":""}],"describe":"十万粉成就","fans_num_threshold":100000,"level":500,"type":0}],"creator_project_fans_threshold":0,"creator_project_info":{"can_re_join":false,"message":"","status":0,"type":0},"credit_info":{"score":100,"score_change":0,"stick_id":0,"stick_id_list":[],"tip":""},"fans_num":9,"is_low_quality":false},"err_no":0,"message":"success"}'
print(try_get_by_name(s, 'name', filter=["status_code=3"]))  # ['文章创作收益', '文章原创', '视频创作收益', '视频原创']
print(try_get_by_name(s, 'name', filter=["status_code<3", "type=4"]))  # ['自营广告']
print(try_get_by_name(s, 'describe', filter=["status_code<3", "type=4"]))  # ['一种个性化的推广方式，支持自主设置广告素材并进行投放推广']

# 新增特性 in: key<#value    not in: key>#value   # 这里是**值** 是否在**key的值** 中 
print(try_get_by_name(s, 'describe', filter=["describe<#'广告'"]))  # 这里的意思就是describe里面包含了广告的describe的值 ['发布文章并选择投放广告，可获得创作收益，收益全部归创作者所有', '一种个性化的推广方式，支持自主设置广告素材并进行投放推广']
print(try_get_by_name(s, 'describe', filter=["describe>#'广告'"]))  # 这里的意思就是describe里面不包含了广告的describe的值 ['基础权益', '百粉权益', '千粉权益', '万粉权益', '五万粉权益', '十万粉成就', '发布文章并勾选「声明原创」，可获得更多推荐与创作收益', '发布横版视频并声明「原创」，产生播放量后，将按照平台规则计算创作收益', '发布横版视频并勾选 「原创」，可获得更多推荐与创作收益，并享受原创保护', '发布非转发抽奖类微头条，可获得创作收益，收益全部归作者所有', '发布原创优质的回答，可获得创作收益，收益全部归作者所有', '开通问答创作收益后，发布回答并勾选「声明原创」，可 获得更多推荐与创作收益', '权益开通后，读者可对作者发布的文章进行打赏，所得收益全部归作者所有', '权益开通后，观众可对作者发布的视频进行打赏，所得收益全部归作者所有', '全网第一手图片，紧追热点，作者免费使用版权图片，为创作赋能', '发布多种形式付费内容，自主定价进行售卖，专栏被购买后作者可获得收益分成', '发起微头条抽奖活动，增强与读者的互动，吸引新的粉丝', '支持作品中插入商品卡，商品通过卡片被购买并确认收货后，作者可获得佣金收益', '付费直播可以为直播课程设置价格，课程被购买后，作者可以获得收益分成', '反馈内容可优先获得人工客服的响应，协助你更好地使用平台', '平台官方作者社群，可享受平台动态优先了解、专属运营答疑、同领域作者互动', '创作者成就表彰旨在奖励平台优质帐号，帮助创作者在平台收获更大影响力']
print(try_get_by_name(s, 'name', filter=["describe<#'广告'"]))  # 这里的意思就是describe里面包含了广告的同级的name的值 ['文章创作收益', '自营广告']
print(try_get_by_name(s, 'name', filter=["describe<#'广告'", 'status_code=0']))  # 这里就是表示多条件的并列关系的处理 ['自营广告']
print(try_get_by_name(s, 'fans_num', filter=["is_low_quality=false"]))  # [9]  布尔或者空置判断按照json的结果或者python的结果一样的  <---json的样式

s2 = {"hello": [{"nihao": 222, "yes": True}, {"nihao": 333, "yes": False}, {"nihao": 444, "yes": None}]}
print(try_get_by_name(s2, 'nihao', filter=["yes=False"]))               # [333]    <---- python 的样式
print(try_get_by_name(s2, 'nihao', filter=["yes=true"]))                # [222]    <---- json   的样式
print(try_get_by_name(s2, 'nihao', filter=["yes=None"]))                # [444]    <---- python 的样式
print(try_get_by_name(s2, 'nihao', filter=["yes=null"]))                # [444]    <---- json   的样式

# 因为之前的那种<-  >- 很容易和右边的数字冲突 现在修改成#判断
# 新增key的结果是否在列表中  in：key#>iter   not in: key#<iter     # 这里是**key的值** 是否在**iter**中
print(try_get_by_name(s2, 'nihao', filter=["yes#>[true, null]"]))       # [222, 444]   python或者json格式混用都可以
print(try_get_by_name(s2, 'nihao', filter=["yes#>[True, None]"]))       # [222, 444]
print(try_get_by_name(s2, 'nihao', filter=["yes#>[True, None]", "nihao=444"]))  # [444]   # 同样支持多条件判断
print(try_get_by_name(s2, 'nihao', filter=["yes#<[true, null]"]))       # [333]

# log 这个报错参数只有在 有filter过滤器存在的时候并且过滤器错误会报错并停止程序  不用过滤器不会退出程序 只会报响应的错误 没有则不报错
# 这种会报错 因为广告不作为字符串处理 这里【不打印】日志【不会停止】程序 【打印了日志】会直接【终结程序】并报相应错误,无返回值->直接推出了全部程序
# print(try_get_by_name(s, 'name', filter=["describe<#广告"], log=True))  # 2021-05-28 10:37:01.777 | ERROR    | lite_tools.dict_parser:__do_filter_func:164 - 类型错误 --> name '广告' is not defined

# 新更新功能 支持处理列表相关数据了
test = {
    "a": {
        "b": [
            {"c": [
                    {"a": 5}, 
                    {"b": 6}, 
                    {"c": 7}
                ]
            }, 
            {"c": 2}
        ]
    }
}

test2 = [
    {"a": 9},
    {"b": [
        {"c": "1"}
    ]}
]

test3 = [[{"c": 100}, {"b": 13}, {"a": 999}, {"d": [{"e": 88}]}]]

print(try_get(test, "a.b.[0].c.[2].c" ))  # 等同于 test["a"]["b"][0]["c"][2]["c"]          -> 7 
print(try_get(test, "a.b.[0].c.[*]c" ))   # 等同于 test["a"]["b"][0]["c"][自动匹配]["c"]    -> 7
print(try_get(test2, "[1].b.[*]c" ))      # 等同于 test2[1]["b"][自动匹配]["c"]             -> 1
print(try_get(test3, "[0].[1].b"))        # 等同于 test3[0][1]["b"]                        -> 13
print(try_get(test3, "[0].[*]a"))        # 等同于 test3[0][自动匹配]["a"]                   -> 999
print(try_get(test3, "[0].[*]d.[*]e"))    # 等同于 test3[0][自动匹配]["d"][自动匹配]["e"]    -> 88
