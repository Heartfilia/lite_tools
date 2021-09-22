# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:26
# @Author : Lodge
import re
import json
import random
from loguru import logger



"""
try_get_by_name 的功能比较复杂 如果json太大可能效率不够 后续有时间再重构一下 目前是能用的 
`try_get需要新增的功能示例如下
a = {"a": [{"a": 1}, {"b": 2}, {"b": 10}]}
==>  try_get(a, "a.[1].b")  -> 2
==>  try_get(a, "a.[*]b")   -> 2

"""


def try_get(renderer, getters, default=None, expected_type=None, log=False):
    """
    获取字典键值  --> 只获取**一个结果** 如果碰到了列表 只获取**第一个值**或者**特定值**
    params renderer: 传入的需要解析的字典或者json串
    params getters : 链式取值 如 a.b.c.d   或者 a.[2].b  或者 a.[*]b  也可以 
    params expected_type: 期望获得的值类型 不是则为None  可多传如：  expected_type=(list, str)
    params default: 默认的返回值, 默认返回None, 可以自定义返回值
    return : 如果取到则为值，否则为None
    """
    renderer = __judge_json(renderer)
    if not renderer:
        logger.error(f"这里需要传入字典或者json串 --> 调用出错->[{getters}]")
        return expected_type
    if isinstance(getters, str):
        getters = getters.strip('.|" "|\n|\r')  # 去掉首位特殊字符 增加容错 避免有的人还写了空格或者.
        origin_getter = "_"
        if '.' in getters:
            getters = getters.split('.')
            for getter in getters:
                if re.search(r"[\d+]", getter):
                    origin_getter += getter
                elif re.search(r"\[\*\]\w+", getter):
                    renderer = handle_reg_rule(renderer, origin_getter, getter, "try重试1_get获取2_fail失败3")
                    # 避免本来结果就是None或者什么情况
                    if renderer == "try重试1_get获取2_fail失败3":
                        return default
                    origin_getter = "_"
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


def try_get_by_name(renderer, getter: str, filter: list = None, expected_type=None, depth: int = 50, in_list: bool = True, log: bool = False) -> list:
    """
    通过名称获取字典里面的字符 这里做底层就是避免有的人乱调用 expected_type本身也是一种过滤器 和filter不建议共用 如果用了优先级高于filter
    :param renderer : 传入的字典或者json串
    :param getter : 需要获取的键的名称
    :param depth : 遍历深度,默认50层
    :param expected_type : 期望获得的值类型 不是则为None  可多传如：  expected_type=(list, str)
    :param log: 是否打印报错的提示日志 默认不打印
    :param in_list: 如果结果在一个列表里面的`字典`里面是否获取 默认获取 只判断列表里面的`字典`的值
    :param filter: 过滤器 -- 目前这个版本更新的是兄弟关系获取 如: [key=value]  key=value 键值关系 目前取值范围只有一个关系 兄弟关系 只会处理同一级字典内容的判断
                                                            示例: ["status>=200", "name='lodge'"]  表示获取的getter里面同一级关系为status>=200 和 name='lodge' 
                    当前支持的条件: =/== 等于 < <= > >= 条件判断    A<#B 因为A只能为键所以这个: B in A   同理 A>#B : B not in A // 这个支持A的值是字符串或者可迭代对象 
                    如: item[A] = str/tuple/dict/set  都可以用B来判断 B可以为字符串:判断item[A]的str结果是否包含B  B为数字或者字符串：判断item[A]的tuple/dict/set是否包含B 
    """
    try:
        renderer = __judge_json(renderer)
        if not renderer:
            logger.error(f"这里需要传入字典或者json串 --> 调用出错->[{getter}]")
            return expected_type
        if isinstance(renderer, list):
            renderer = {"try_get_by_name_dict_data": renderer}
        _ = __try_get_by_name(renderer=renderer, getter=getter, depth=depth, expected_type=expected_type, filter=filter, in_list=in_list, log=log)
    except (AttributeError, KeyError, TypeError, IndexError) as e:
        if log is True:
            logger.error(f"try_get_by_name: {e} -- {type(e)} --line: {e.__traceback__.tb_lineno}")
        return []
    except Exception as res:
        return res.args[0] if res.args else []


def __try_get_by_name(renderer: dict, getter: str, expected_type, in_list, result: list = None, filter=None, depth: int = 50, is_first=True, log=False) -> list:
    """
    通过名称获取字典里面的字符  这里做底层就是避免有的人乱调用  :不支持列表嵌套列表那种提取 一般碰不到 懒得弄 如: [[{"a": 1}]]
    :param renderer : 传入的字典
    :param getter : 需要获取的键的名称
    :param result : 外面不需要传这个参数 这个作内部参数校验
    :param depth : 遍历深度,默认50层
    :param is_first : 是否是第一次传入,外面不需要传这个数据
    :param in_list: 如果结果在一个列表里面的`字典`里面是否获取 默认不获取 只判断列表里面的`字典`的值
    :param filter: 过滤器--> 只处理同级关系
    """
    if is_first is True:
        result = []
    if depth < 0 or not renderer:
        raise Exception(result)
    need_parse_next_renderer = dict()
    for key, value in renderer.items():
        if re.sub(r"#_#\d+", "", key) == getter:
            if expected_type is not None and not isinstance(value, expected_type):
                if isinstance(value, dict):
                    need_parse_next_renderer.update(__do_dict_sample(value))
                continue
            if filter is not None:
                ok = __do_filter_func(filter, renderer, log)
                if ok:
                    result.append(value)
            else:
                result.append(value)

        if isinstance(value, dict):
            need_parse_next_renderer.update(__do_dict_sample(value))
        if isinstance(value, list) and in_list is True:
            for item in value:
                if isinstance(item, dict):
                    res, need_dict = __handle_to_dict(item, getter, filter, expected_type, log)
                    result += res
                    need_parse_next_renderer.update(need_dict)

    depth -= 1
    return __try_get_by_name(need_parse_next_renderer, getter, expected_type, in_list, result, filter=filter, depth=depth, is_first=False, log=log)


def __handle_to_dict(data: dict, getter, filter, expected_type, log):
    """就是判断字典里面值是否一样"""
    back_dict = dict()
    back_result = list()
    for key, value in data.items():
        if re.sub(r"#_#\d+", "", key) == getter:
            if expected_type is not None and not isinstance(value, expected_type):
                if isinstance(value, dict):
                    back_dict.update(__do_dict_sample(value))
                continue
            if filter is not None:
                ok = __do_filter_func(filter, data, log)
                if ok:
                    back_result.append(value)
            else:
                back_result.append(value)

        if isinstance(value, dict):
            back_dict.update(__do_dict_sample(value))
        
        if isinstance(value, list):
            back_dict.update({f"need_parse_next#_#{random.randint(1, 999999999999)}": value})
        
    return back_result, back_dict 


def __do_dict_sample(data: dict):
    """这个操作是为了让字典扁平化的时候 避免外层和内层名称相同  上面处理了这个的操作意思是一样"""
    back_dict = dict()
    for new_key, new_value in data.items():
        new_key = f"{new_key}#_#{random.randint(1, 999999999999)}"
        back_dict[new_key] = new_value
    return back_dict


def __do_filter_func(filter, renderer, log=False):
    """这里是过滤器主逻辑控制的地方"""
    first = True    # 判断是否第一次给默认值
    ok = False
    for rule in filter:
        if first:
            ok = True
            first = False
        try:
            flag = __handle_calculation(rule, renderer)
        except Exception as err:
            if log is True:
                logger.error(f"类型错误 --> {err}")
                exit(0)
            return False
        if flag is True:
            ok = ok and True
        else:
            ok = ok and False
    return ok


def __handle_calculation(rule, renderer: dict) -> bool:
    """处理各种逻辑判断的  之前用的<-  -> 这种样式 发现<> 右边的 - 很容易和数字发生问题 现在改成#"""
    if '==' in rule:
        rule.replace('==', '=')  # 避免有的人写了==来判断
    if "!=" in rule:
        return __do_not_equal(rule, renderer)
    elif "<#" in rule:   # 这个是 key value  ==>  value 在 key的值中
        return __do_in(rule, renderer)
    elif "#>" in rule:   # 这个是 key value  ==>  key的值 在value中 这个只支持value是 list、tuple、set、frozenset
        return __do_in_re(rule, renderer)
    elif ">#" in rule:   # 这个是 key value  ==>  value 不在 key的值中
        return __do_not_in(rule, renderer)
    elif "#<" in rule:   # 这个是 key value  ==>  key的值 不在value中 这个只支持value是 list、tuple、set、frozenset
        return __do_not_in_re(rule, renderer) 
    elif "<=" in rule:
        return __do_less_than_equal(rule, renderer)
    elif ">=" in rule:
        return __do_more_than_equal(rule, renderer)
    elif "=" in rule:  
        return __do_equal(rule, renderer)
    elif ">" in rule:
        return __do_more_than(rule, renderer)
    elif "<" in rule:
        return __do_less_than(rule, renderer)

    return False


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


def __get_dict_data(renderer: dict, filter_key):
    """这里第一个返回值是判断键是否在字典里面 第二个是返回结果 --> 这里是处理扁平化后的结果"""
    for key, value in renderer.items():
        if re.sub(r"#_#\d+", "", key) == filter_key:
            return True, value
    return False, None


def __do_not_equal(rule, renderer):
    filter_rule = rule.split('!=')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1].replace('true', "True").replace('false', 'False').replace('null', "None"))  # eval在json串中会报错的地方的处理
    flag, result = __get_dict_data(renderer, filter_key)
    if flag and result != filter_value:
        return True
    return False


def __do_equal(rule, renderer):
    filter_rule = rule.split('=')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1].replace('true', "True").replace('false', 'False').replace('null', "None"))
    flag, result = __get_dict_data(renderer, filter_key)
    if flag and result == filter_value:
        return True
    return False


def __do_in(rule, renderer):
    # 这个过滤结果 --> 在键的 值 中
    filter_rule = rule.split('<#')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1].replace('true', "True").replace('false', 'False').replace('null', "None"))
    flag, result = __get_dict_data(renderer, filter_key)   # result == renderer[filter_key] 这个
    if flag and isinstance(filter_value, str) and \
        isinstance(result, (str, list, tuple, set, frozenset)) and filter_value in result:
        return True
    elif flag and isinstance(filter_value, (int, float)) and \
        isinstance(result, (list, tuple, set, frozenset)) and filter_value in result:
        return True
    return False


def __do_in_re(rule, renderer):
    # 这个是键的值 在 过滤条件中
    filter_rule = rule.split('#>')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1].replace('true', "True").replace('false', 'False').replace('null', "None"))
    if isinstance(filter_value, (list, tuple, set, frozenset)):
        flag, result = __get_dict_data(renderer, filter_key)
        if flag and result is None and result in filter_value:
            return True
        elif flag and isinstance(result, (bool, str, int, float)) and result in filter_value:
            return True
    return False


def __do_not_in(rule, renderer):
    filter_rule = rule.split('>#')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1].replace('true', "True").replace('false', 'False').replace('null', "None"))
    flag, result = __get_dict_data(renderer, filter_key)
    if flag and isinstance(filter_value, str) and \
        isinstance(result, (str, list, tuple, set, frozenset)) and filter_value not in result:
        return True
    elif flag and isinstance(filter_value, (int, float)) and \
        isinstance(result, (list, tuple, set, frozenset)) and filter_value not in result:
        return True
    return False


def __do_not_in_re(rule, renderer):
    # 这个是键的值 在 过滤条件中
    filter_rule = rule.split('#<')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1].replace('true', "True").replace('false', 'False').replace('null', "None"))
    if isinstance(filter_value, (list, tuple, set, frozenset)):
        flag, result = __get_dict_data(renderer, filter_key)
        if flag and result is None and result not in filter_value:
            return True
        elif flag and isinstance(result, (bool, str, int, float)) and result not in filter_value:
            return True
    return False


def __do_less_than_equal(rule, renderer):
    filter_rule = rule.split('<=')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1])
    flag, result = __get_dict_data(renderer, filter_key)
    if flag and isinstance(filter_value, (int, float)) and result <= filter_value:
        return True
    return False


def __do_more_than_equal(rule, renderer):
    filter_rule = rule.split('>=')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1])
    flag, result = __get_dict_data(renderer, filter_key)
    if flag and isinstance(filter_value, (int, float)) and result >= filter_value:
        return True
    return False


def __do_more_than(rule, renderer):
    filter_rule = rule.split('>')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1])
    flag, result = __get_dict_data(renderer, filter_key)
    if flag and isinstance(filter_value, (int, float)) and result > filter_value:
        return True
    return False


def __do_less_than(rule, renderer):
    filter_rule = rule.split('<')
    filter_key = str(filter_rule[0])
    filter_value = eval(filter_rule[1])
    flag, result = __get_dict_data(renderer, filter_key)
    if flag and isinstance(filter_value, (int, float)) and result < filter_value:
        return True
    return False
