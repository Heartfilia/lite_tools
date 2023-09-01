# -*- coding: utf-8 -*-
# @Time   : 2021-04-07 12:23
# @Author : Lodge
import re
from hashlib import (
    md5, sha1, sha224, sha256, sha384, sha512,
    sha3_224, sha3_256, sha3_384, sha3_512
)

from typing import Union, List
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from lite_tools.exceptions.StringExceptions import BadModeException


__ALL__ = ["get_md5", "get_sha", "get_sha3"]


def get_md5(s: Union[str, bytes, int, float, List[int]], mode: Literal[16, 32] = 32, up: bool = False, encoding='utf-8',
            **kwargs) -> str:
    """
    利用md5加密内容
    :param s: 加密前字符串(兼容直接操作数字和浮点数转成字符串再获取md5)
    :param mode: 返回32位还是16位md5 默认32位
    :param up: 是否返回大写的字符串 默认 False --> 返回小写
    :param encoding: 字符串的编码方式 默认 utf-8
    :return: 加密后字符串
    """
    if mode not in [16, 32]:
        raise BadModeException

    md5_obj = md5()
    try:
        if isinstance(s, (str, int, float)):
            md5_obj.update(str(s).encode(encoding))
        elif isinstance(s, list):
            md5_obj.update(bytearray(s))
        elif isinstance(s, bytes):
            md5_obj.update(s)

        result = md5_obj.hexdigest()

        if up is True:
            result = result.upper()

        if mode == 16:
            result = result[8:-8]
        return result
    except Exception:
        raise TypeError


def get_sha(s: Union[str, bytes, int, float], mode: Literal[1, 224, 256, 384, 512] = 256, encoding='utf-8') -> str:
    """
    获取shaX的加密内容
    :param s: 加密前字符串
    :param mode: 可以加密的模式: sha1 sha224 sha256 sha384 sha512 只需要传入数字即可 默认: 256
    :param encoding: 字符串的编码方式 默认 utf-8
    :return: 加密后字符串
    """
    if mode not in [1, 224, 256, 384, 512]:
        raise BadModeException

    sha_obj = eval(f"sha{mode}()")
    try:
        if isinstance(s, (str, int, float)):
            sha_obj.update(str(s).encode(encoding))
        elif isinstance(s, bytes):
            sha_obj.update(s)
    except Exception:
        raise TypeError
    return sha_obj.hexdigest()


def get_sha3(s: Union[str, bytes, int, float], mode: Literal[224, 256, 384, 512] = 256, encoding='utf-8') -> str:
    """
    获取sha3_X的加密内容
    :param s: 加密前字符串
    :param mode: 可以加密的模式: sha3_224 sha3_256 sha3_384 sha3_512 只需要传入数字即可 默认: 256
    :param encoding:
    :return:
    """
    if mode not in [224, 256, 384, 512]:
        raise BadModeException

    sha3_obj = eval(f"sha3_{mode}()")
    try:
        if isinstance(s, (str, int, float)):
            sha3_obj.update(str(s).encode(encoding))
        elif isinstance(s, bytes):
            sha3_obj.update(s)
    except Exception:
        raise TypeError
    return sha3_obj.hexdigest()


def get_5dm(s: str) -> str:
    """
    这个是给我自己用的 别人用没啥用 主要是对md5操作
    :param s: md5
    """
    if len(s) != 32 or re.search("[^0-9a-z]", s):
        s = get_md5(s)   # 如果长对不对 先加密成md5

    new_array = [s[ind:ind + 4] for ind in range(0, 32, 4)]
    array_1 = new_array[:4][::-1]
    array_2 = new_array[4:][::-1]  # 我这里颗粒度比较低
    return "".join(array_1 + array_2)
