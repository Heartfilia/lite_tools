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
print(try_get(test, "a.b[0].c[2].c" ))    # 等同于 test["a"]["b"][0]["c"][2]["c"]          -> 7 

print(try_get(test, "a.b[0].c.[*]c" ))    # 等同于 test["a"]["b"][0]["c"][自动匹配]["c"]    -> 7

# 如果由列表开始 那么数据位需要独立处理 不再和键合并写 （*除外 *得跟键才可以作头部位置)  示例如下
print(try_get(test2, "[1].b.[*]c" ))      # 等同于 test2[1]["b"][自动匹配]["c"]             -> 1
print(try_get(test2, "[*]b.[*]c" ))       # 等同于 test2[自动匹配]["b"][自动匹配]["c"]       -> 1
print(try_get(test3, "[0].[1].b"))        # 等同于 test3[0][1]["b"]                        -> 13
print(try_get(test3, "[0].[*]a"))         # 等同于 test3[0][自动匹配]["a"]                  -> 999

print(try_get(test3, "[0].[*]d.[*]e"))    # 等同于 test3[0][自动匹配]["d"][自动匹配]["e"]    -> 88
# 上面这个连写是因为知道要获取哪个列表下面的什么键下面的值
# 多个不确定的值列表```不要```连续写   如下
print(try_get(test3, "[*].[*]d.[*]e"))  # 错误  -> None
print(try_get(test3, "[*][*]d.[*]e"))   # 错误  -> None

print(try_get(test_json, 'a.d.e'))                 # 3   ==> support the Chain operation  **推荐**这个写法 可以设置默认值 可以设置期望值类型
print(try_get(test_json, lambda x: x['a']['b']))   # 1   ==> support the lambda operation 
print(try_get(test_json, 'x'))                     # None  ==> not found      support `expected_type` too
print(try_get(test_json, 'x', "hello"))            # hello ==> if not found 'x', then set default result  **设置默认**返回值**
print(try_get_by_name(test_json, 'e'))                   # [-3, 3, 'newBee', 10, {'yy': 'test', 'e': 'good_test'}, 'good_test'] 可以获取列表里面的字典的下面的值 默认获取
print(try_get_by_name(test_json, 'e', expected_type=int))          # [-3, 3, 10]   
print(try_get_by_name(test_json, 'e', expected_type=(int, str)))   # [-3, 3, 10, 'good_test']  

"""
过滤器功能下线，实际用处不大 而且还有可能出问题
"""
