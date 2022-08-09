# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:26
# @Author : Lodge
import re
import json as _json
import functools
from typing import Any, Optional, Iterator

from lite_tools.utils_jar.logs import my_logger, get_using_line_info, logger


__ALL__ = ["match_case", 'try_get', 'try_key', 'FlattenJson', 'JsJson']
"""
try_get 取值和 FlattenJson 取值规则不一样 两者的时间复杂度也不一样 
TODO (这里需要优化代码 文件读取位置需要调整)  get_using_line_info  这个也得调整
"""


def try_get(
        renderer, getters=None, default=None, expected_type=None, log=False,
        json=False, options: dict = None) -> Any:
    r"""
    获取字典键值  --> 只获取**一个结果** 如果碰到了列表 只获取**第一个值**或者**特定值**
    只传入一个json串 那么就是转换为字典:
    注意：如果是 点(\.) 或者 竖(\|) 或者数字(\-35/) 或者左中括号(\["a"])--> 如果要匹配 a = {"\0/": 1} 这种类型键 try_get(a, "\\0/")
         在键里面需要加转义符号（不支持小数因为使用率比较低，弄起来又麻烦浪费时间）--> **如果键是花里胡哨的别用这个方法,可能会错**
    如果传入一个字典 json=True 那么就是转为json字符串
    :param renderer: 传入的需要解析的字典或者json串
    :param getters : 链式取值 -- 不传入那么就只是单纯的格式化json传 这里支持管道符多匹配辣 如: a.b.c|a.b.d[-1]|a.c.d
            如果键里面有管道符 --> 请把键里面的管道符用 反斜杠表示 防止转义
            示例:a.b.c.d   a[2].b 或者 a.[2].b  或者 a.[*]b ->*是代表不知道是哪一个列表下面出现的b 如果都有那就取第一个
    :param default : 默认的返回值, 默认返回None, 可以自定义返回值
    :param expected_type: 期望获得的值类型 不是则为 default  可多传如：  expected_type=(list, str)
    :param log     :  是否打印日志
    :param json    :  设置为True 返回值会返回默认的json串
    :param options : 这里就是json.dumps的参数 变成了字典传入 不过我默认值有修改 ensure_ascii=False json那默认的是True 如果读取js文件设置见demo
                   : 如果处理文件：需要加参数 "mode": "file"  (可以额外指定的参数:encoding-默认utf-8) 具体见demo
    :return        : 如果取到则为值，否则为 default 设置的值 默认None
    """
    renderer = _judge_json(renderer, json, options)
    if not renderer and isinstance(options, dict) and options.get('mode') == "file":
        # 这里是把json文件输出到本地文件的时候的情况
        return None
    if not renderer:
        if log is True:
            line, fl = get_using_line_info()
            my_logger(fl, "try_get", line, f"这里需要传入字典或者json串 --> 调用出错->[{getters}]")
        return expected_type
    elif json is True or getters is None:
        # 如果是需要json字符串或者只是单纯想转换字符串 不要传对应值就好了
        return renderer

    if isinstance(getters, str):
        getters, split_string = _split_by_high_core(getters, r"\|")
        for each_getter in getters.split(split_string):    # 兼容 | 管道符号可以多个条件一起操作
            if r"\|" in each_getter:
                each_getter = each_getter.replace(r"\|", "|")  # 防止转义的键里面的管道符恢复原样
            getter = each_getter.strip('. \n\r')          # 去掉首位特殊字符 增加容错 避免有的人还写了空格或者.
            getter, split_string = _split_by_high_core(getter, r"\.")
            # 把转义过的键里面的.排除 然后再把没有转义符的.做分割处理
            if "." in getter:
                origin_getter, renderer = handle_dot_situation(getter, renderer, split_string)
            else:
                origin_getter, renderer = handle_normal_situation(getter, renderer)

            if renderer == "try重试１ダ_get获取２メ_fail失败３よ":
                continue

            try:
                now_result = __main_try_get(renderer, lambda _: eval(origin_getter), default, expected_type, log)
            except Exception as err:
                # 因为有些时候lambda 那里可能会出现问题
                _ = err
                if log is True:
                    line, fl = get_using_line_info()
                    my_logger(fl, "try_get", line, f"请不要连写一堆操作符在 -- [{getters.replace('||', '|')}] 这上面")
                continue
            if now_result != default:
                return now_result
    return default


def _split_by_high_core(getters: str, handle: str):
    """
    切割核心字符串 避免切割错误
    :param getters: 需要切割的字符串
    :param handle : 需要处理的转义后符号如: \\|  \\.
    :return: 替换后的字符串, 可用于切割的标记符
    """
    if handle not in getters:
        return getters, handle[1:]
    only_string = "开始^解_耦$结束"
    cut_string = "开始^切_割$结束"
    getter = getters.replace(
        handle, only_string
    ).replace(
        handle[1], cut_string
    ).replace(
        only_string, handle
    )
    return getter, cut_string


def handle_dot_situation(getter: str, renderer: dict, split_string: str):
    """
    处理有 . 在的情况
    """
    origin_getter = "_"
    getter = getter.split(split_string)
    for now_getter in getter:
        # 把转义过后的键里面的点恢复原样
        if r"\." in now_getter:
            now_getter = now_getter.replace(r"\.", ".")
        if re.search(r"\S*\\\[\S+]\S*", now_getter):
            new_getter = now_getter.replace(r"\[", '[')
            origin_getter += f"['{new_getter}']"
        elif re.search(r"\S+\[-?\d+]", now_getter):
            origin_getter += _get_w_d_rules(now_getter)
        elif re.search(r"\[-?\d+]\S+", now_getter):
            origin_getter += _get_d_w_rules(now_getter)
        elif re.search(r"\[\*]\S+", now_getter):
            # 这里因为会改 render的结构 所以就不要单独处理了
            renderer, origin_getter = handle_reg_rule(
                renderer, origin_getter, now_getter, "try重试１ダ_get获取２メ_fail失败３よ")
            # 避免本来结果就是None或者什么情况
            if renderer == "try重试１ダ_get获取２メ_fail失败３よ":
                continue
        elif re.search(r"\[\d+]", now_getter):
            origin_getter += now_getter  # 这里是为了兼容  a.[2].b  这种格式
        else:
            if re.search(r"^\\-?\d+/$", now_getter):
                origin_getter += f"[{now_getter[1:-1]}]"
            else:
                origin_getter += f"['{now_getter}']"

    return origin_getter, renderer


def handle_normal_situation(each_getter: str, renderer: dict):
    """
    处理没有 . 的情况
    """
    origin_getter = "_"
    if re.search(r"\[\*]\S+", each_getter):
        renderer, origin_getter = handle_reg_rule(
            renderer, origin_getter, each_getter, "try重试１ダ_get获取２メ_fail失败３よ")
        # 避免本来结果就是None或者什么情况
        if renderer == "try重试１ダ_get获取２メ_fail失败３よ":
            origin_getter = "_"
    elif re.search(r"\\\[\S+]", each_getter):
        origin_getter += f"['{each_getter[1:]}']"
    elif re.search(r"\S+\[-?\d+]", each_getter):  # a[2]
        origin_getter += _get_w_d_rules(each_getter)
    elif re.search(r"\[-?\d+]\S+", each_getter):  # [2]b   # 这里是为了兼容 不推荐这样写
        origin_getter += _get_d_w_rules(each_getter)
    else:
        if re.search(r"^\\-?\d+/$", each_getter):
            origin_getter += f"[{each_getter[1:-1]}]"
        elif re.search(r"\\\\-?\d+/", each_getter):
            origin_getter += f"['{each_getter[1:]}']"
        else:
            origin_getter += f"['{each_getter}']"

    return origin_getter, renderer


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


def try_key(renderer, getter, mode: str = "key", expected_type=None, log: bool = False,
            options: dict = None) -> Optional[list]:
    """
    批量获取结果json、字典的键值结果
    :param renderer: 传入的json串或者字典
    :param getter  : 需要匹配的值-->配合mode
    :param mode    : 默认通过键模式匹配(key)->匹配getter相同的键返回值; value-->匹配相同结果的值的键
    :param expected_type : 期望获取到的结果的类型(就是一个简单的类型过滤器)
    :param log           : 报错的时候是否打印日志
    :param options       : 文件处理 或者
        过滤器(只处理兄弟等值--如一个字典里面某个键="x"时候y的值
        {
            "filter": {"equal": {"key1": "value1", "key2": "value2"}, "unequal": {"key1": "value1"}}
        }
        )   --> 只处理等值和不等值 当然其他的也能弄 后面再添加规则
    """
    renderer = _judge_json(renderer, options=options)
    if not renderer and isinstance(options, dict) and options.get('mode') == "file":
        # 这里是把json文件输出到本地文件的时候的情况
        return None
    if not renderer:
        if log is True:
            line, fl = get_using_line_info()
            my_logger(fl, "try_key", line, f"请传入标准的json串或者python字典数据")
        return []
    results_list = []
    for result in _try_get_results_iter(renderer, getter, mode, options):
        if expected_type is None:
            results_list.append(result)
        elif expected_type and isinstance(result, expected_type):
            results_list.append(result)

    return results_list


def _try_get_results_iter(renderer, getter, mode: str = "key", options: dict = None):
    if isinstance(renderer, dict):
        key_value_iter = (iter_obj for iter_obj in renderer.items())
    elif isinstance(renderer, list):
        key_value_iter = (iter_obj for iter_obj in enumerate(renderer))
    else:
        return

    for key, value in key_value_iter:
        if mode == 'key' and key == getter:
            if options and options.get('filter') and isinstance(options.get('filter'), dict):
                flag = _filter_rules(renderer, options.get('filter'))
                if flag:
                    yield value
            else:
                yield value
        elif mode == 'value' and value == getter:
            yield key
        if isinstance(value, (dict, list)):
            yield from _try_get_results_iter(value, getter, mode, options)


def _filter_rules(renderer, filter_option: dict):
    """
    这里是为了后续能多条件筛选留着的 这里下面目前只有等值判断
    """
    flag = False
    # 等于情况
    equal_option = filter_option.get('equal')
    if equal_option and isinstance(equal_option, dict):
        flag = _judge_filter_rules_equal(renderer, equal_option)
        if not flag:
            return False

    # 不等于
    unequal_option = filter_option.get('unequal')
    if unequal_option and isinstance(unequal_option, dict):
        flag = _judge_filter_rules_unequal(renderer, unequal_option)
        if not flag:
            return False

    # 更多规则后面在这里如上添加就好了
    return flag


def _judge_filter_rules_equal(renderer, equal_options: dict):
    """
    判断是否是兄弟规则: 这里是只处理等值  后续可以按照这个模版处理其他规则的 新建一个函数处理就好了
    """
    if not isinstance(renderer, dict):
        return False
    right = False
    for f_key, f_value in equal_options.items():
        if renderer.get(f_key) == f_value:
            right = True
        else:
            return False
    else:
        return right


def _judge_filter_rules_unequal(renderer, unequal_options: dict):
    """
    判断是否是兄弟规则: 这里是只处理不等值  后续可以按照这个模版处理其他规则的 新建一个函数处理就好了
    """
    if not isinstance(renderer, dict):
        return False
    right = False
    for f_key, f_value in unequal_options.items():
        if renderer.get(f_key) != f_value:
            right = True
        else:
            return False
    else:
        return right


def _judge_json(renderer, json=False, options=None):
    """
    判断传入进来的是json串还是字典 自动处理成字典
    如果传入了options那么就可以转成json
    """
    if options is None:
        options = {}
    if options.get('mode') == "file":
        # 如果要直接操作文件的js 那么走这里
        return _js_file_local(renderer, options)
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


def _js_file_local(renderer, options):
    if isinstance(renderer, str):
        # 如果传入的是字符串,那么就是想要从本地js里面获取json
        try:
            with open(renderer, 'r', encoding=options.get('encoding', 'utf-8')) as fr:  # file read
                return _json.load(fr)
        except FileNotFoundError:
            logger.error(f"{renderer} -- 路径错误没有找到js文件")
        except (UnicodeEncodeError, UnicodeDecodeError):
            logger.error(f"{renderer} -- 尝试更换正确的 options={{\"encoding\": \"需求的编码\"}}")
        except Exception as err:
            logger.error(f"读取 {renderer}错误: {err}")
    elif isinstance(renderer, (list, dict)):
        # 默认输出utf-8 修改添加进 options里面的encoding
        outfile_dir = options.get("output")
        if not outfile_dir:
            logger.error(f"需要输出的路径地址 options={{\"output\": \"输出的路径\"}}")
            return None
        try:
            with open(options.get("output"), 'w', encoding=options.get('encoding', 'utf-8')) as fw:  # file write
                return _json.dump(renderer, fw,
                                  skipkeys=options.get("skipkeys", False),
                                  ensure_ascii=options.get("ensure_ascii", False),    # 这里默认是True 我不想他转我换了
                                  check_circular=options.get("check_circular", True),
                                  allow_nan=options.get("allow_nan", True),
                                  indent=options.get("indent"),
                                  separators=options.get("separators"),
                                  sort_keys=options.get("sort_keys", False),
                                  default=options.get("default"),
                                  cls=options.get("cls"))
        except (FileNotFoundError, FileExistsError):
            logger.error(f"路径错误: {options.get('output')}")
        except Exception as err:
            logger.error(f"读取 {renderer}错误: {err}")
    return None


class FlattenJson(object):
    def __init__(self, array):
        self.dict_data = _judge_json(array)
        self.result_data = {}    # 只定义最小单位 平铺前面全部单位
        self._start()

    def __str__(self):
        return _json.dumps(self.result_data)

    def _start(self):
        _ = [_ for _ in self._flat_now(self.dict_data)]
        del _

    def __dict__(self):
        return self.result_data

    def _flat_now(self, dict_data, base_node="") -> dict:
        if isinstance(dict_data, dict):
            key_value_iter = (iter_obj for iter_obj in dict_data.items())
            flag = "dict"
        elif isinstance(dict_data, list):
            key_value_iter = (iter_obj for iter_obj in enumerate(dict_data))
            flag = "list"
        else:
            self.result_data[base_node.rstrip(".")] = dict_data
            return

        for key, value in key_value_iter:
            e_key = self._encode_key(key, flag)
            if flag == "list":
                temp_node = base_node.rstrip(".") + e_key
            else:
                temp_node = base_node + e_key
            yield from self._flat_now(value, temp_node)

    @staticmethod
    def _encode_key(key, flag) -> str:
        if flag == "list":
            return f"[{key}]."
        if "." in key:
            key = key.replace('.', r'\.')
        elif "[" in key:
            key = key.replace('[', r'\[')
        return key + "."

    def show(self) -> None:
        """就是打印一下扁平化的结果"""
        print(self.result_data)

    def get_all(self) -> Iterator:
        yield from self.result_data.items()

    def path(self, value) -> Iterator:
        """通过值取键的路径"""
        for key, result in self.result_data.items():
            if result == value:
                yield key

    def get(self, getter: str, default=None):
        """按照键值方式取值"""
        return self.result_data.get(getter, default)


class JsJson(object):
    """
    TODO(2022.2.22周二 阴历正月二十二)这里后面再做各种兼容模式 现在只兼容了 天气模块那个格式处理
    """
    def __init__(self, javascript=None, reg_rule=None):
        """
        :param javascript: 就是传入的需要解析的文本串
        :param reg_rule  : 是可以自定义的 避免识别不到 但是得有两个分组 键-值
        """
        self._h = javascript
        self.result = {}
        self._parse_now(reg_rule)

    def get(self, key, default=None):
        return self.result.get(key, default)    # 直接实例化对象也能获取result

    def get_all(self) -> Iterator:
        yield from self.result.items()

    def _parse_now(self, reg_rule):
        if reg_rule is None:
            reg_rule = r"(?<=var )?.*?(\S+) *= *({.*?\});"   # 解析天气模块用的
        items = re.findall(reg_rule, self._h if self._h.endswith(';') else f"{self._h};")
        # if not items:
        #     list_data = [(str(ind), value) for ind, value in re.finditer("", self._h)]

        for key, value in items:
            # flag = self._check_valid_symbol(value)
            # if flag:
            self._check_json(key, value)
        del items

    def _check_json(self, key, value):
        """
        判断是不是json文件
        """
        result = _judge_json(value)
        if result is not None:
            self.result[key] = result

    @staticmethod
    def _check_valid_symbol(need_check_js: str) -> bool:
        """
        判断这个js文件是不是有效的成对出现的符号 -- 貌似也用不到这里 先留着叭
        """
        temp_stack = []
        for char in re.findall(r"[(\[{)\]\}]", need_check_js):
            if char in ["(", "[", "{"]:     # 40  91  123
                temp_stack.append(char)
            elif char in [")", "]", "}"]:   # 41  93  125
                if not temp_stack:
                    return False
                last_char = temp_stack.pop()
                if abs(ord(char) - ord(last_char)) > 2:
                    return False
        return not temp_stack

    def __str__(self):
        return try_get(self.result, json=True)

    def __repr__(self):
        return try_get(self.result, json=True)


def match_case(func):
    """
    也是一个装饰器来着
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
