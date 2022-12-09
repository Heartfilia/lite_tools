# -*- coding: utf-8 -*-
from lite_tools.tools.core.lite_parser import try_key

# about try_get   // try_key
r"""
关于一些写法的推荐
本方法**不建议**那些**花里胡哨**的键都用这个功能处理太麻烦了而且使用率又低我就没有搞兼容
正常的键是：英文+数字+下划线   其它的键只做了部分兼容，如果遇到就换dict里面的get好了
1. 涉及到列表                            如  a[0].b     不建议 a.[0]b   -- 虽然结果一样的,我做了兼容的
2. 列表的每个操作符和普通元素要分开          如  a[0][1].b   不要写 a[0][1]b
3. 每个提取操作最好都是用 . 分开           如  [0].a[1]   不要写 [0]a[1]
4. 有些时候要是不知道怎么写了 就单独提取数据  如  a.[0].b.c.[1] 
5. 如果*键*里面有 [ | . ] 那么得加转义        如  {"a.b": {"[c|x]": {5: "666"}}}  写法: a\.b.\[c\|x.\5/   --数字键前后得加 \数字/
"""
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
        ],
        "c": [1, 2, 3]
    }
}

test2 = [
    {"a": 9},
    {"b": [
        {"c": "1"}
    ]}
]

test3 = [[{"c": 100}, {"b": 13}, {"a": 999}, {"d": [{"e": 88}]}]]

test4 = {"a": [{"b": 1}, {"c": 2}]}
# print(try_get(test4, "a[0].b"))           # 1  这两个是等价的  所以这两种格式之间得注意 不要a[0]b 这样子写 得有个.
# print(try_get(test4, "b.a|c.b|a[-1].c"))  # 2   ---> 本次更新的支持管道符多值匹配

# print(try_get(test, "a.b.[0].c.[2].c"))  # 等同于 test["a"]["b"][0]["c"][2]["c"]          -> 7
# print(try_get(test, "a.b[0].c[2].c"))    # 等同于 test["a"]["b"][0]["c"][2]["c"]          -> 7

"""
try_get_by_name 和 try_key 是等价的 都能用 try_key 简短一点
"""
# print(try_get(test_json, 'a.d.e'))                 # 3   ==> support the Chain operation  **推荐**这个写法 可以设置默认值 可以设置期望值类型
# print(try_get(test_json, 'x'))                     # None  ==> not found      support `expected_type` too
# print(try_get(test_json, 'x', "hello"))            # hello ==> if not found 'x', then set default result  **设置默认**返回值**
# print(try_key(test_json, 'e'))                   # [-3, 3, 10, {'yy': 'test', 'e': 'good_test'}, 'good_test', 'newBee'] 可以获取列表里面的字典的下面的值 默认获取

"""
try_get 和 try_key 在处理文件是等价的：以下是文件处理操作 主要设置在options里面
"""
# 读文件的时候options 可用参数
read_options = {
    "mode": "file",           # 如果是处理文件,一定要写这个 读取文件的时候这里传入文件路径
    "encoding": "utf-8",      # 默认这个, 可以自己改
}

# try_get("xxx.json", options={"mode": "file"})

# 写文件的时候options 可用参数
write_options = {
    "mode": "file",           # 如果是处理文件,一定要写这个 输出文件的时候这里传入对象
    "encoding": "utf-8",      # 默认这个, 可以自己改
    "output": "输出文件路径",   # 这里输出文件的时候一定要设置
    "skipkeys": False,        # 跳过的键
    "ensure_ascii": False,    # 这里默认是True 我不想他转我换了
    "check_circular": True,
    "allow_nan": True,        # 允许空
    "indent": None,           # 缩进
    "separators": None,       # 分割
    "sort_keys": False        # 是否排序
}
# try_get({"a": 1}, options={"mode": "file", "output": "某位置"})
"""
过滤器功能下线，实际用处不大 而且还有可能出问题
"""
