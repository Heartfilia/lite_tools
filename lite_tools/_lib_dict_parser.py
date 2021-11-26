# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:26
# @Author : Lodge
import re
import json
import functools

from loguru import logger


"""
`try_get需要新增的功能示例如下
a = {"a": [{"a": 1}, {"b": 2}, {"b": 10}]}
==>  try_get(a, "a.[1].b")  -> 2
==>  try_get(a, "a.[*]b")   -> 2

"""

__ALL__ = ["match_case", 'try_get', 'try_get_by_name']


def try_get(renderer, getters, default=None, expected_type=None, log=False, *args, **kwargs):
    """
    获取字典键值  --> 只获取**一个结果** 如果碰到了列表 只获取**第一个值**或者**特定值**
    params renderer: 传入的需要解析的字典或者json串
    params getters : 链式取值 如 a.b.c.d   a[2].b 或者 a.[2].b  或者 a.[*]b ->*是代表不知道是哪一个列表下面出现的b 如果都有那就取第一个 
    params expected_type: 期望获得的值类型 不是则为None  可多传如：  expected_type=(list, str)
    params default: 默认的返回值, 默认返回None, 可以自定义返回值
    return : 如果取到则为值，否则为None
    """
    renderer = __judge_json(renderer)
    if not renderer:
        if log is True:
            logger.error(f"这里需要传入字典或者json串 --> 调用出错->[{getters}]")
        return expected_type
    if isinstance(getters, str):
        getters = getters.strip('.|" "|\n|\r')  # 去掉首位特殊字符 增加容错 避免有的人还写了空格或者.
        origin_getter = "_"
        if '.' in getters:
            getters = getters.split('.')
            for getter in getters:
                if re.findall(r"\w+\[\d+\]", getter):  # a[2].b
                    getter_head = getter.split('[')[0]
                    origin_getter += f"['{getter_head}']"
                    getter_foot = "[" + getter.split('[')[1]
                    origin_getter += getter_foot
                elif re.search(r"\[\*\]\w+", getter):
                    renderer = handle_reg_rule(renderer, origin_getter, getter, "try重试1_get获取2_fail失败3")
                    # 避免本来结果就是None或者什么情况
                    if renderer == "try重试1_get获取2_fail失败3":
                        return default
                    origin_getter = "_"
                elif re.search(r"[\d+]", getter):
                    origin_getter += getter   # 这里是为了兼容  a.[2].b  这种格式
                else:
                    origin_getter += f"['{getter}']"
        else:
            origin_getter += f"['{getters}']"
        getters = lambda _: eval(origin_getter)
    return __main_try_get(renderer, getters, default, expected_type, log)


def handle_reg_rule(renderer, origin_getter, getter, default):
    """
    这里是因为只会出现 [*]a  这种匹配规则 故结果一定是列表 不是的话返回自己规定的错误状态 
    """
    matching_var = getter[3:]
    
    # 这里先获取到列表 [{},{}]
    getters = lambda _: eval(origin_getter)   # a.b.[0].c
    results = __main_try_get(renderer, getters, default)

    if isinstance(results, list):
        for result in results:
            if matching_var in result:
                return result.get(matching_var, default)
    return default


def __main_try_get(renderer, getters, default=None, expected_type=None, log=False):
    if not isinstance(getters, (list, tuple)):
        getters = [getters]
    for getter in getters:
        try:
            result = getter(renderer)
            if expected_type is None or isinstance(result, expected_type):
                return result
        except (AttributeError, KeyError, TypeError, IndexError) as e:
            if log is True:
                logger.error(f"try_get: {e} --line: {e.__traceback__.tb_lineno}")
    return default


# ==============================================================================================================
"""
这里是改版后的,旧版采用递归方式处理 操作比较麻烦 但是功能繁多，速度不够快
新版这里是借鉴了 https://github.com/kingname/JsonPathFinder 二次改进版本,相较于旧版速度提升了,剔除了用不到的功能
"""


def try_get_by_name(renderer, getter: str, mode: str="key", expected_type=None, log: bool=False, *args, **kwargs) -> list:
    """
    批量获取结果json、字典的键值结果
    :param renderer: 传入的json串或者字典
    :param getter  : 需要匹配的值-->配合mode
    :param mode    : 默认通过键模式匹配(key)->匹配getter相同的键返回值; value-->匹配相同结果的值的键
    :expected_type : 期望获取到的结果的类型(就是一个简单的类型过滤器)
    :log           : 报错的时候是否打印日志
    """
    renderer = __judge_json(renderer)
    if not renderer:
        if log is True:
            logger.error(f"请传入标准的json传或者python字典数据")
        return []
    results_list = []
    for result in _try_get_results_iter(renderer, getter, mode):
        if expected_type is None:
            results_list.append(result)
        else:
            if isinstance(result, expected_type):
                results_list.append(result)
    return results_list


def _try_get_results_iter(renderer, getter: str, mode: str="key"):
    if isinstance(renderer, dict):
        key_value_iter = (iter_obj for iter_obj in renderer.items())
    elif isinstance(renderer, list):
        key_value_iter = (iter_obj for iter_obj in enumerate(renderer))
    else: return

    for key, value in key_value_iter:
        if mode == 'key' and key == getter:
            yield value
        elif mode == 'value' and value == getter:
            yield key
        if isinstance(value, (dict, list)):
            yield from _try_get_results_iter(value, getter, mode)


def __judge_json(renderer):
    """判断传入进来的是json串还是字典 自动处理成字典"""
    if isinstance(renderer, (dict, list)):
        return renderer
    elif isinstance(renderer, str):
        try:
            data = json.loads(renderer)
        except json.decoder.JSONDecodeError:
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
            if args and "__module__" in dir(arg0): arg0 = args[0]  # 这里是给类使用
            delegate = registry[arg0]
        except KeyError:
            pass
        else:
            return delegate(arg0, *args, **kwargs)

        return func(arg0, *args, **kwargs)

    def register(value):
        def wrap(func):
            if value in registry:
                raise ValueError(
                    f'@match_case: there is already a handler '
                    f'registered for {value!r}'
                )
            registry[value] = func
            return func
        return wrap

    def register_all(values):
        def wrap(func):
            for value in values:
                if value in registry:
                    raise ValueError(
                        f'@match_case: there is already a handler '
                        f'registered for {value!r}'
                    )
                registry[value] = func
            return func
        return wrap

    wrapper.register = register
    wrapper.register_all = register_all
    return wrapper