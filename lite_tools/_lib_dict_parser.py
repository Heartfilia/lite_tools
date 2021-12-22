# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:26
# @Author : Lodge
import re
import json as _json
import functools
from typing import Any

from lite_tools._utils_logs import my_logger, get_using_line_info


"""
`try_get需要新增的功能示例如下
a = {"a": [{"a": 1}, {"b": 2}, {"b": 10}]}
==>  try_get(a, "a.[1].b")  -> 2
==>  try_get(a, "a.[*]b")   -> 2

"""

__ALL__ = ["match_case", 'try_get', 'try_get_by_name']


def try_get(
        renderer, getters=None, default=None, expected_type=None, log=False,
        json=False, options: dict = None):
    """ TODO(getters是英文数字混合有问题  需要改)
    获取字典键值  --> 只获取**一个结果** 如果碰到了列表 只获取**第一个值**或者**特定值**
    只传入一个json串 那么就是转换为字典
    如果传入一个字典 json=True 那么就是转为json字符串
    :param renderer: 传入的需要解析的字典或者json串
    :param getters : 链式取值 -- 不传入那么就只是单纯的格式化json传 这里支持管道符多匹配辣 如: a.b.c|a.b.d[-1]|a.c.d
               示例:a.b.c.d   a[2].b 或者 a.[2].b  或者 a.[*]b ->*是代表不知道是哪一个列表下面出现的b 如果都有那就取第一个
    :param default : 默认的返回值, 默认返回None, 可以自定义返回值
    :param expected_type: 期望获得的值类型 不是则为 default  可多传如：  expected_type=(list, str)
    :param log     :  是否打印日志
    :param json    :  设置为True 返回值会返回默认的json串
    :param options : 这里就是json.dumps的参数 变成了字典传入 不过我默认值有修改 ensure_ascii=False json那默认的是True
    :return         : 如果取到则为值，否则为 default 设置的值 默认None
    """
    renderer = __judge_json(renderer, json, options)
    if not renderer:
        if log is True:
            line, fl = get_using_line_info()
            my_logger(fl, "try_get", line, f"这里需要传入字典或者json串 --> 调用出错->[{getters}]")
        return expected_type
    elif json is True or getters is None:
        # 如果是需要json字符串或者只是单纯想转换字符串 不要传对应值就好了
        return renderer

    if isinstance(getters, str):
        for each_getter in getters.split("|"):       # 兼容 | 管道符号可以多个条件一起操作
            getter = each_getter.strip('.|" "|\n|\r')  # 去掉首位特殊字符 增加容错 避免有的人还写了空格或者.
            origin_getter = "_"
            if '.' in getter:
                getter = getter.split('.')
                for now_getter in getter:
                    if re.findall(r"\w+\[-?\d+\]", now_getter):
                        origin_getter += _get_w_d_rules(now_getter)
                    elif re.findall(r"\[-?\d+\]\w+", now_getter):
                        origin_getter += _get_d_w_rules(now_getter)
                    elif re.search(r"\[\*\]\w+", now_getter):
                        # 这里因为会改 render的结构 所以就不要单独处理了
                        renderer, origin_getter = handle_reg_rule(
                            renderer, origin_getter, now_getter, "try重试１ダ_get获取２メ_fail失败３よ")
                        # 避免本来结果就是None或者什么情况
                        if renderer == "try重试１ダ_get获取２メ_fail失败３よ":
                            continue
                    elif re.search(r"[\d+]", now_getter):
                        origin_getter += now_getter  # 这里是为了兼容  a.[2].b  这种格式
                    else:
                        origin_getter += f"['{now_getter}']"
            else:
                if re.search(r"\[\*\]\w+", each_getter):
                    renderer, origin_getter = handle_reg_rule(
                        renderer, origin_getter, each_getter, "try重试１ダ_get获取２メ_fail失败３よ")
                    # 避免本来结果就是None或者什么情况
                    if renderer == "try重试１ダ_get获取２メ_fail失败３よ":
                        continue
                elif re.findall(r"\w+\[-?\d+\]", each_getter):  # a[2]
                    origin_getter += _get_w_d_rules(each_getter)
                elif re.findall(r"\[-?\d+\]\w+", each_getter):  # [2]b   # 这里是为了兼容 不推荐这样写
                    origin_getter += _get_d_w_rules(each_getter)
                else:
                    origin_getter += f"['{each_getter}']"
            try:
                now_result = __main_try_get(renderer, lambda _: eval(origin_getter), default, expected_type, log)
            except Exception:
                # 因为有些时候lambda 那里可能会出现问题
                if log is True:
                    line, fl = get_using_line_info()
                    my_logger(fl, "try_get", line, f"请不要连写一堆操作符在 -- [{getters}] 这上面")
                return default
            if now_result != default and now_result != "try重试１ダ_get获取２メ_fail失败３よ":
                return now_result
    return default


def _get_w_d_rules(now_getter):
    """
    这里是之规则为 -- \\w+\\[-?\\d+\\] 的
    """
    origin_getter = ""
    getter_head = now_getter.split('[')[0]
    origin_getter += f"['{getter_head}']"
    getter_foot = "[" + now_getter.split('[')[1]
    origin_getter += getter_foot
    return origin_getter


def _get_d_w_rules(now_getter):
    """
    这里是之规则为 -- [-?\\d+\\]\\w+ 的
    """
    origin_getter = ""
    getter_head = now_getter.split(']')[0]
    origin_getter += getter_head + "]"
    getter_foot = now_getter.split(']')[1]
    origin_getter += f"['{getter_foot}']"
    return origin_getter


def handle_reg_rule(renderer, origin_getter, getter, default):
    """
    这里是因为只会出现 [*]a  这种匹配规则 故结果一定是列表 不是的话返回自己规定的错误状态 
    """
    matching_var = getter[3:]
    
    # 这里先获取到列表 [{},{}]
    results = __main_try_get(renderer, lambda _: eval(origin_getter), default)

    if isinstance(results, list):
        for result in results:
            if not isinstance(result, dict):
                continue
            if matching_var in result:
                return result.get(matching_var, default), "_"
    return default, origin_getter


def __main_try_get(renderer, getters: Any, default=None, expected_type=None, log=False):
    if not isinstance(getters, (list, tuple)):
        getters = [getters]
    for getter in getters:
        try:
            result = getter(renderer)  # lambda function
            if expected_type is None or isinstance(result, expected_type):
                return result
        except (AttributeError, KeyError, TypeError, IndexError) as e:
            if log is True:
                line, fl = get_using_line_info()
                my_logger(fl, "try_get", line, e)
    return default


# ==============================================================================================================
"""
这里是改版后的,旧版采用递归方式处理 操作比较麻烦 但是功能繁多，速度不够快
新版这里是借鉴了 https://github.com/kingname/JsonPathFinder 二次改进版本,相较于旧版速度提升了,剔除了用不到的功能
"""


def try_get_by_name(renderer, getter, mode: str = "key", expected_type=None, log: bool = False) -> list:
    """
    批量获取结果json、字典的键值结果 TODO(增加一个 try_key 的别名)
    :param renderer: 传入的json串或者字典
    :param getter  : 需要匹配的值-->配合mode
    :param mode    : 默认通过键模式匹配(key)->匹配getter相同的键返回值; value-->匹配相同结果的值的键
    :param expected_type : 期望获取到的结果的类型(就是一个简单的类型过滤器)
    :param log           : 报错的时候是否打印日志
    """
    renderer = __judge_json(renderer)
    if not renderer:
        if log is True:
            line, fl = get_using_line_info()
            my_logger(fl, "try_get_by_name", line, f"请传入标准的json串或者python字典数据")
        return []
    results_list = []
    for result in _try_get_results_iter(renderer, getter, mode, expected_type):
        results_list.append(result)
    return results_list


def _try_get_results_iter(renderer, getter, mode: str = "key", expected_type=None):
    if isinstance(renderer, dict):
        key_value_iter = (iter_obj for iter_obj in renderer.items())
    elif isinstance(renderer, list):
        key_value_iter = (iter_obj for iter_obj in enumerate(renderer))
    else:
        return

    for key, value in key_value_iter:
        if mode == 'key' and key == getter:
            if expected_type is None:
                yield value
            else:
                if isinstance(value, expected_type):
                    yield value
        elif mode == 'value' and value == getter:
            if expected_type is None:
                yield key
            else:
                if isinstance(value, expected_type):
                    yield key
        if isinstance(value, (dict, list)):
            yield from _try_get_results_iter(value, getter, mode)


def __judge_json(renderer, json=False, options=None):
    """
    判断传入进来的是json串还是字典 自动处理成字典
    如果传入了options那么就可以转成json
    """
    if options is None:
        options = {}
    if isinstance(renderer, (dict, list)):
        if json is True:
            try:
                return _json.dumps(
                    renderer,
                    skipkeys=options.get('skipkeys', False),
                    ensure_ascii=options.get('ensure_ascii', False),   # 这里我是按照了自己常用修改成这个了
                    check_circular=options.get('check_circular', True),
                    allow_nan=options.get('allow_nan', True),
                    cls=options.get('cls', None),
                    indent=options.get('indent', None),
                    separators=options.get('separators', None),
                    default=options.get('default', None),
                    sort_keys=options.get('sort_keys', False)
                )
            except Exception as err:
                return str(err)
        return renderer
    elif isinstance(renderer, str):
        try:
            if json is True:
                return renderer
            data = _json.loads(renderer)
        except _json.decoder.JSONDecodeError:
            return None
        else:
            return data


def match_case(func):
    """
    也是一个装饰器来着
    I have changed the name. (original name -> value_dispatch)
    修改了原来的命名 使其更加好记 采用了如下源的代码
    新增优化,支持了类 内部函数的调用->同原方案一样 主要是 dispatches by value of the first arg""
    """
    # This source file is part of the EdgeDB open source project.
    #
    # Copyright 2021-present MagicStack Inc. and the EdgeDB authors.
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    #
    """Like singledispatch() but dispatches by value of the first arg.
    Example:
        @match_case
        def eat(fruit):
            return f"I don't want a {fruit}..."
        @eat.register('apple')
        def _eat_apple(fruit):
            return "I love apples!"
        @eat.register('eggplant')
        @eat.register('squash')
        def _eat_what(fruit):
            return f"I didn't know {fruit} is a fruit!"
    An alternative to applying multuple `register` decorators is to
    use the `register_all` helper:
        @eat.register_all({'eggplant', 'squash'})
        def _eat_what(fruit):
            return f"I didn't know {fruit} is a fruit!"
    """

    registry = {}

    @functools.wraps(func)
    def wrapper(arg0, *args, **kwargs):
        try:
            if args and "__module__" in dir(arg0):
                arg0 = args[0]  # 这里是给类使用
            delegate = registry[arg0]
        except KeyError:
            pass
        else:
            return delegate(arg0, *args, **kwargs)

        return func(arg0, *args, **kwargs)

    def register(value):
        def wrap(func):
            if value in registry:
                return func
            registry[value] = func
            return func
        return wrap

    def register_all(values):
        def wrap(func):
            for value in values:
                if value in registry:
                    continue
                registry[value] = func
            return func
        return wrap

    wrapper.register = register
    wrapper.register_all = register_all
    return wrapper
