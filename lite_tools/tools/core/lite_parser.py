# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:26
# @Author : Lodge
import re
import copy
import json as os_json
from typing import Any, Optional, Iterator, Union, Generator

try:
    from typing import Literal
except ImportError:
    try:
        from typing_extensions import Literal
    except ImportError:
        from lite_tools.utils.pip_ import install

        install('typing_extensions')
        from typing_extensions import Literal

from lite_tools.logs import my_logger, get_using_line_info, logger
from lite_tools.exceptions.DictExceptions import (
    TemplateFormatError, NotJsonException, NotGoalItemException
)


__ALL__ = ['try_get', 'try_key', 'FlattenJson', 'JsJson', 'WrapJson']
"""
try_get 取值和 FlattenJson 取值规则不一样 两者的时间复杂度也不一样 
get_using_line_info  这个也得调整
"""


def try_get(
        renderer: Any,
        getters: Optional[str] = None, default: Any = None, expected_type: Any = None,
        log: bool = False, json: bool = False, options: dict = None
) -> Any:
    r"""
    获取字典键值  --> 只获取**一个结果** 如果碰到了列表 只获取**第一个值**或者**特定值**
    只传入一个json串 那么就是转换为字典:
    注意：这几种东西如果是键需要转义 -->    |  .  [    ]   这四个符号如果是键得加 \
        如 {”a|b[c.d]“: {"x": 666}}  这种我们需要写 --> "a\|b\c\.d\].x"
        如果是纯数字或者小数做主键 请不要用我这个方法 如 {12: {3.14: 666}}  真有这种需求请用json包
    如果传入一个字典 json=True 那么就是转为json字符串
    :param renderer: 传入的需要解析的字典或者json串 或者jsonp格式串都行
    :param getters : 链式取值 -- 不传入那么就只是单纯的格式化json传 这里支持管道符多匹配辣 如: a.b.c|a.b.d[-1]|a.c.d
        这里单词前面如果是数组必须有 .  如 a[1][2].b  或者 a.[1][2].b 或者 a.[1].[2].b  请不要写a[1][2]b 否则碰到 a.b.c咋说
    :param default : 默认的返回值, 默认返回None, 可以自定义返回值
    :param expected_type: 期望获得的值类型 不是则为 default  可多传如：  expected_type=(list, str)
    :param log     :  是否打印日志
    :param json    :  设置为True 返回值会返回默认的json串 默认为去格式的json串
    :param options : 这里就是json.dumps的参数 变成了字典传入 不过我默认值有修改 ensure_ascii=False json那默认的是True 如果读取js文件设置见demo
                   : 如果处理文件：需要加参数 "mode": "file"  (可以额外指定的参数:encoding-默认utf-8) 具体见demo
                   : 一般不建议用我这个包搞这个 虽然可以 但是复杂
    :return        : 如果取到则为值，否则为 default 设置的值 默认None
    """
    renderer = _judge_json(renderer, json, options)
    if not renderer and isinstance(options, dict) and options.get('mode') == "file":
        # 这里是把json文件输出到本地文件的时候的情况
        return default
    if not renderer:
        if log:
            line, fl = get_using_line_info()
            my_logger(fl, "try_get", line, f"这里需要传入字典或者json串 --> 调用出错->[{getters}]")
        return expected_type
    elif json is True or getters is None:
        # 如果是需要json字符串或者只是单纯想转换字符串 不要传对应值就好了
        return renderer

    if isinstance(getters, str):
        getters = symbol_encode(getters)
        for each_getter in getters.split("|"):    # 兼容 | 管道符号可以多个条件一起操作
            origin_getter = trans_to_dict_rule(each_getter)
            decode_getter = symbol_decode(origin_getter)
            try:
                now_result = __main_try_get(renderer, lambda _: eval(decode_getter), default, expected_type, log)
            except Exception as err:
                # 因为有些时候lambda 那里可能会出现问题
                if log:
                    line, fl = get_using_line_info()
                    my_logger(fl, "try_get", line, err)
                continue
            if now_result != default:
                return now_result
    return default


def symbol_encode(origin_string: str) -> str:
    """
    把特殊符号加密 避免后面出问题
    """
    origin_string = origin_string.replace(r"\.", chr(64446))
    origin_string = origin_string.replace(r"\[", chr(64447))
    origin_string = origin_string.replace(r"\]", chr(64448))
    origin_string = origin_string.replace(r"\|", chr(64449))
    return origin_string


def symbol_decode(decode_string: str) -> str:
    decode_string = decode_string.replace(chr(64446), ".")
    decode_string = decode_string.replace(chr(64447), "[")
    decode_string = decode_string.replace(chr(64448), "]")
    decode_string = decode_string.replace(chr(64449), "|")
    return "_" + decode_string


def trans_to_dict_rule(origin_string: str):
    result = ""
    for string in origin_string.split('.'):
        if "[" not in string:
            result += f"['{string}']"
        elif "[" in string and string.endswith("]"):
            if not string.startswith("["):
                result += re.sub(r"(^[^\[]+)", r"['\1']", string)
            else:
                result += string
    return result


def __main_try_get(renderer: Any, getter: Any, default=None, expected_type=None, log: bool = False):
    try:
        result = getter(renderer)  # lambda function
        if expected_type is None or isinstance(result, expected_type):
            return result
    except (AttributeError, KeyError, TypeError, IndexError) as e:
        if log:
            line, fl = get_using_line_info()
            my_logger(fl, "try_get", line, e)
    return default


# ==============================================================================================================
"""
这里是改版后的,旧版采用递归方式处理 操作比较麻烦 但是功能繁多，速度不够快
新版这里是借鉴了 https://github.com/kingname/JsonPathFinder 二次改进版本,相较于旧版速度提升了,剔除了用不到的功能
"""


def try_key(renderer, getter, mode: Literal['key', 'value'] = "key", expected_type=None, log: bool = False,
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
        return []
    if not renderer:
        if log:
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


regex = re.compile(r"^[^(]+\((.*)\);?", flags=re.S)  # jsonP匹配模板


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
        if json:
            try:
                return os_json.dumps(
                    renderer,
                    skipkeys=options.get('skipkeys', False),
                    ensure_ascii=options.get('ensure_ascii', False),   # 这里我是按照了自己常用修改成这个了
                    check_circular=options.get('check_circular', True),
                    allow_nan=options.get('allow_nan', True),
                    cls=options.get('cls', None),
                    indent=options.get('indent', None),
                    separators=options.get('separators', None) or (",", ":"),   # 默认无格式
                    default=options.get('default', None),
                    sort_keys=options.get('sort_keys', False)
                )
            except Exception as err:
                return str(err)
        return renderer
    elif isinstance(renderer, str):
        try:
            if json:
                return renderer
            if (renderer.startswith('{') and renderer.endswith("}")) or (
                    renderer.startswith('[') and renderer.endswith("]")):
                # 标准的 json 数组串 不需要任何操作
                pass
            elif regex.search(renderer):  # 如果是jsonP的格式
                renderer = regex.search(renderer).group(1)
            data = os_json.loads(renderer)
        except os_json.decoder.JSONDecodeError:
            return None
        else:
            return data
    return None


def _js_file_local(renderer, options):
    if isinstance(renderer, str):
        # 如果传入的是字符串,那么就是想要从本地js里面获取json
        try:
            with open(renderer, 'r', encoding=options.get('encoding', 'utf-8')) as fr:  # file read
                return os_json.load(fr)
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
                return os_json.dump(renderer, fw,
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
        return os_json.dumps(self.result_data)

    def _start(self):
        _ = [_ for _ in self._flat_now(self.dict_data)]
        del _

    def __dict__(self):
        return self.result_data

    def _flat_now(self, dict_data, base_node="") -> Generator[Any, None, None]:
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

    def exists(self, getter: str) -> bool:
        return True if getter in self.result_data else False


class JsJson(object):
    """
    不做这个识别操作了 (2022.2.22周二 阴历正月二十二)这里后面再做各种兼容模式 现在只兼容了 天气模块那个格式处理
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
        for char in re.findall(r"[(\[{)\]}]", need_check_js):
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


class WrapJson(object):
    def __init__(self, template: Union[dict, list]):
        """
        :param template: 传入的最小单元组的模板 模板的最小级别单位不允许传入具体的值
        如 {
            ”a“: str,         # a 必须为字符串
            "b": {
                "c": list     # c 必须为列表
            },
            "d": ...          # 忽略格式但是必须存在（不允许是list,tuple,set,dict...这些集合类型）
        }
        """
        self.check_items = FlattenJson(template)          # 后面提取数据需要这个校验
        for tes_key, each_value in self.check_items.get_all():
            if type(each_value) is not type and each_value is not ...:
                logger.error("模板只允许 基本单位的类型(int, str, float, bool) 以及 省略符号(...) 可以忽略参数类型")
                logger.warning("其中(list,dict,set,tuple..)这些类型不允许用 ...匹配,只能指定是list或者tuple类型,否则返回None")
                logger.error("不支持typing的进阶操作及具体值")
                raise TemplateFormatError
        self.results = []  # 给列表操作的时候用的 --> 用这个函数请避免用在多线程,毕竟这个效果只是为了单线程服务
        self.template = template

    def get_all(self, items: Union[str, list, dict]):
        dict_item = _judge_json(items)   # str --> 为了兼容json数据,json可以直接转换为python数据类型处理
        if not dict_item:
            raise NotJsonException

        if isinstance(dict_item, dict):
            # 如果初始的数据格式样式为字典,那么返回的结果就是字典，只是单纯压缩数据
            try:
                result = self._wrap_from_dict(dict_item)
            except NotGoalItemException:
                return {}
        elif isinstance(dict_item, list):
            # 如果初始的数据是列表 那么就提出来的结果也是列表
            self.results = []
            for _ in self._wrap_from_list(dict_item):
                ...
            result = self.results
        else:
            result = ""   # 走不到这里来, 我只是看不惯idea的报错提示

        return result

    @staticmethod
    def _parse_rules(key: str) -> str:
        base_key = ""
        split_key = key.split('.')   # a   [0]   c
        for sk in split_key:
            if sk.endswith(']') and sk.startswith('[') and re.search(r'^\[-?\d+]', sk):
                base_key += sk
            else:
                if sk.find('[') != -1 and sk.find(']') != -1:
                    ind_xs = re.findall(r'(\[\d+])', sk)
                    sk = re.sub(r'\[\d+]', "", sk)
                    base_key += f"['{sk}']"
                    for ind in ind_xs:
                        base_key += ind
                else:
                    base_key += f"['{sk}']"
        return base_key

    def _wrap_from_dict(self, item: dict) -> dict:
        base_model = copy.deepcopy(self.template)
        flatten_json = FlattenJson(item)
        for key, value in self.check_items.get_all():
            parser_key = self._parse_rules(key)
            if value in [list, tuple, set, dict, frozenset]:
                result = try_get(item, key)
                if not isinstance(result, value):
                    raise NotGoalItemException
            else:
                result = flatten_json.get(key)
                if value != type(result) and self.check_items.get(key) is not ...:
                    raise NotGoalItemException
            exec(f"base_model{parser_key} = {repr(result)}")

        return base_model

    def _wrap_from_list(self, item: list):
        for each in item:
            if isinstance(each, list):
                yield from self._wrap_from_list(each)
            elif isinstance(each, dict):
                try:
                    result = self._wrap_from_dict(each)
                except NotGoalItemException:
                    pass
                else:
                    self.results.append(result)


if __name__ == "__main__":
    a = [1, 2, 3]
