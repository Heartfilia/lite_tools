# -*- coding: utf-8 -*-
# @Author  : Lodge
"""
      ┏┛ ┻━━━━━┛ ┻┓
      ┃　　　　　　 ┃
      ┃　　　━　　　┃
      ┃　┳┛　  ┗┳　┃
      ┃　　　　　　 ┃
      ┃　　　┻　　　┃
      ┃　　　　　　 ┃
      ┗━┓　　　┏━━━┛
        ┃　　　┃   神兽保佑
        ┃　　　┃   代码无BUG！
        ┃　　　┗━━━━━━━━━┓
        ┃　　　　　　　    ┣┓
        ┃　　　　         ┏┛
        ┗━┓ ┓ ┏━━━┳ ┓ ┏━┛
          ┃ ┫ ┫   ┃ ┫ ┫
          ┗━┻━┛   ┗━┻━┛
"""
import functools
__ALL__ = ["match_case"]


def match_case(func):
    """
    也是一个装饰器来着    3.10+ 版本已经本身支持 match case的语法了
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

