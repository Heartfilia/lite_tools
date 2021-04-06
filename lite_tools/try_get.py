# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:26
# @Author : Lodge
from loguru import logger


def try_get(renderer: dict, getters, expected_type=None):
    """
    获取字典键值
    params renderer: 传入的需要解析的字典
    params getters : 获取途径 --> 示例: lambda x: x["detail"]["age"]  --> 取不到得到None  新增属性==>支持链式取值 如 a.b.c.d
    params expected_type: 期望获得的值类型 不是则为None  可多传如：  expected_type=(list, str)
    return : 如果取到则为值，否则为None
    """
    if isinstance(getters, str):
        origin_x = "x"
        if '.' in getters:
            getters = getters.split('.')
            for x in getters:
                origin_x += f"['{x}']"
        else:
            origin_x += f"['{getters}']"
        getters = lambda x: eval(origin_x)
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
            logger.error(f"try_get: {e} --line: {e.__traceback__.tb_lineno}")
    else:
        return None


def try_get_by_name(renderer: dict, getter: str, depth: int = 20) -> list:
    """
    通过名称获取字典里面的字符  这里做底层就是避免有的人乱调用
    :param renderer : 传入的字典
    :param getter : 需要获取的键的名称
    :param depth : 遍历深度,默认20层
    """
    try:
        result_list = []
        result = _try_get_by_name(renderer=renderer, getter=getter, depth=depth)
        return result
    except Exception as e:
        logger.error(f"try_get_by_name: {e} --line: {e.__traceback__.tb_lineno}")
        return []


def _try_get_by_name(renderer, getter, result=[], depth=20, is_first=True) -> list:
    """
    通过名称获取字典里面的字符  这里做底层就是避免有的人乱调用
    :param renderer : 传入的字典
    :param getter : 需要获取的键的名称
    :param result : 外面不需要传这个参数 这个作内部参数校验
    :param depth : 遍历深度,默认20层
    :param is_first : 是否是第一次传入,外面不需要传这个数据
    """
    if is_first is True:
        result = []
    if depth <= 0:
        return result
    if not renderer or not isinstance(renderer, dict):
        return result
    need_parse_dict_list = []
    for key, value in renderer.items():
        if key == getter:
            result.append(value)
        if isinstance(value, dict):
            need_parse_dict_list.append(value)

    if not need_parse_dict_list:
        return result
    depth -= 1
    for value in need_parse_dict_list:
        return _try_get_by_name(value, getter, result, depth, is_first=False)
    else:
        return result
