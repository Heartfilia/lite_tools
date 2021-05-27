# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:26
# @Author : Lodge
import re
import random
from sys import flags
from loguru import logger


def try_get(renderer: dict, getters, default=None, expected_type=None, log=False):
    """
    获取字典键值
    params renderer: 传入的需要解析的字典
    params getters : 获取途径 --> 示例: lambda x: x["detail"]["age"]  --> 取不到得到None  新增属性==>支持链式取值 如 a.b.c.d
    params expected_type: 期望获得的值类型 不是则为None  可多传如：  expected_type=(list, str)
    params default: 默认的返回值, 默认返回None, 可以自定义返回值
    return : 如果取到则为值，否则为None
    """
    if isinstance(getters, str):
        getters = getters.strip('.|" "|\n|\r')  # 去掉首位特殊字符
        origin_getter = "_"
        if '.' in getters:
            getters = getters.split('.')
            for getter in getters:
                origin_getter += f"['{getter}']"
        else:
            origin_getter += f"['{getters}']"
        getters = lambda _: eval(origin_getter)
    if not isinstance(getters, (list, tuple)):
        getters = [getters]
    for getter in getters:
        try:
            result = getter(renderer)
            if expected_type is None:
                return result
            elif isinstance(result, expected_type):
                return result
        except (AttributeError, KeyError, TypeError, IndexError) as e:
            if log is True:
                logger.error(f"try_get: {e} --line: {e.__traceback__.tb_lineno}")
    else:
        return default


def try_get_by_name(renderer: dict, getter: str, depth: int = 50, in_list: bool = True, expected_type=None, filter: list = None, log: bool = False) -> list:
    """
    通过名称获取字典里面的字符  这里做底层就是避免有的人乱调用
    :param renderer : 传入的字典
    :param getter : 需要获取的键的名称
    :param depth : 遍历深度,默认50层
    :param expected_type : 期望获得的值类型 不是则为None  可多传如：  expected_type=(list, str)
    :param log: 是否打印报错的提示日志 默认不打印
    :param in_list: 如果结果在一个列表里面的`字典`里面是否获取 默认获取 只判断列表里面的`字典`的值
    :param filter: 过滤器 -- 目前这个版本更新的是兄弟关系获取 如: [key=value]  key=value 键值关系 目前取值范围只有一个关系 兄弟关系 只会处理同一级字典内容的判断
                                                            示例: ["status>=200", "name='lodge'"]  表示获取的getter里面同一级关系为status>=200 和 name='lodge' 
    """
    try:
        _ = __try_get_by_name(renderer=renderer, getter=getter, depth=depth, expected_type=expected_type, filter=filter, in_list=in_list)
    except (AttributeError, KeyError, TypeError, IndexError) as e:
        if log is True:
            logger.error(f"try_get_by_name: {e} -- {type(e)} --line: {e.__traceback__.tb_lineno}")
        return []
    except Exception as res:
        return res.args[0] if res.args else []


def __try_get_by_name(renderer: dict, getter: str, expected_type, in_list, result: list = None, filter=None, depth: int = 50, is_first=True) -> list:
    """
    通过名称获取字典里面的字符  这里做底层就是避免有的人乱调用
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
                ok = __do_filter_func(filter, renderer)
                if ok:
                    result.append(value)
            else:
                result.append(value)

        if isinstance(value, dict):
            need_parse_next_renderer.update(__do_dict_sample(value))
        if isinstance(value, list) and in_list is True:
            for item in value:
                if isinstance(item, dict):
                    res, need_dict = __handle_to_dict(item, getter, filter, expected_type)
                    result += res
                    need_parse_next_renderer.update(need_dict)

    depth -= 1
    return __try_get_by_name(need_parse_next_renderer, getter, expected_type, in_list, result, filter=filter, depth=depth, is_first=False)


def __handle_to_dict(data: dict, getter, filter, expected_type):
    back_dict = dict()
    back_result = list()
    for key, value in data.items():
        if re.sub(r"#_#\d+", "", key) == getter:
            if expected_type is not None and not isinstance(value, expected_type):
                if isinstance(value, dict):
                    back_dict.update(__do_dict_sample(value))
                continue
            if filter is not None:
                ok = __do_filter_func(filter, data)
                if ok:
                    back_result.append(value)
            else:
                back_result.append(value)

        if isinstance(value, dict):
            back_dict.update(__do_dict_sample(value))
        
        if isinstance(value, list):
            back_dict.update({f"need_parse_next#_#{random.randint(1, 9999999999)}": value})
        
    return back_result, back_dict 


def __do_dict_sample(data: dict):
    back_dict = dict()
    for new_key, new_value in data.items():
        new_key = f"{new_key}#_#{random.randint(1, 9999999999)}"
        back_dict[new_key] = new_value
    return back_dict


def __do_filter_func(filter, renderer):
    first = True    # 判断是否第一次给默认值
    ok = False
    for rule in filter:
        if first:
            ok = True
            first = False
        flag = __handle_calculation(rule, renderer)
        if flag is True:
            ok = ok and True
        else:
            ok = ok and False
    return ok


def __handle_calculation(rule, renderer) -> bool:
    if '==' in rule:
        rule.replace('==', '=')
    if "=" in rule:  
        filter_rule = rule.split('=')
        filter_key = str(filter_rule[0])
        filter_value = filter_rule[1]
        if renderer[filter_key] == eval(filter_value):
            return True
    elif ">" in rule:
        filter_rule = rule.split('>')
        filter_key = str(filter_rule[0])
        filter_value = filter_rule[1]
        if renderer[filter_key] > eval(filter_value):
            return True
    elif ">=" in rule:
        filter_rule = rule.split('>=')
        filter_key = str(filter_rule[0])
        filter_value = filter_rule[1]
        if renderer[filter_key] >= eval(filter_value):
            return True
    elif "<" in rule:
        filter_rule = rule.split('<')
        filter_key = str(filter_rule[0])
        filter_value = filter_rule[1]
        if renderer[filter_key] < eval(filter_value):
            return True
    elif "<=" in rule:
        filter_rule = rule.split('<=')
        filter_key = str(filter_rule[0])
        filter_value = filter_rule[1]
        if renderer[filter_key] <= eval(filter_value):
            return True
    elif "!=" in rule:
        filter_rule = rule.split('!=')
        filter_key = str(filter_rule[0])
        filter_value = filter_rule[1]
        if renderer[filter_key] != eval(filter_value):
            return True
    return False
