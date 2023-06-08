# -*- coding: utf-8 -*-
# @Time   : 2021-04-07 12:23
# @Author : Lodge
from base64 import (
    b16encode, b32encode, b64encode, b85encode,
    b16decode, b32decode, b64decode, b85decode)
from typing import Union
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


__ALL__ = ['get_b64e', 'get_b64d']


def get_b64e(s: Union[str, bytes, int, float], mode: Literal[16, 32, 64, 85] = 64, encoding='utf-8', to_bin: bool = False) -> str:
    """
    用baseXX加密字符串
    :param s: 传入的字符串
    :param mode: 加密模式默认base64  可选参数: 16 32 64 85 .
    :param encoding: 字符串解析默认utf-8
    :param to_bin: 是否返回字节串 默认不转换 返回字符串内容
    :return: 加密后的值
    """
    if mode in [16, 32, 64, 85]:
        if isinstance(s, bytes):
            encoder = eval(f"b{mode}encode('{s}')")
        else:
            encoder = eval(f"b{mode}encode('{s}'.encode('{encoding}'))")
        if to_bin is False:
            try:
                encoder = encoder.decode(encoding)
            except Exception:
                raise TypeError
        return encoder
    else:
        raise Exception('SUPPORT: b16encode b32encode b64encode b85encode // only need inputting: 16 32 64 85')


def get_b64d(s: str, mode: Literal[16, 32, 64, 85] = 64, encoding='utf-8') -> str:
    """
    用baseXX进行解密对应的内容
    :param s: 传入的字符串
    :param mode: 解密模式默认base64  可选参数: 16 32 64 85 .
    :param encoding: 字符串解析默认utf-8
    :return: 解密后的字符串内容
    """
    if mode in [16, 32, 64, 85]:
        try:
            decoder = eval(f'b{mode}decode("{s}")')
            return decoder.decode(encoding)
        except Exception:
            raise TypeError
    else:
        raise Exception('SUPPORT: b16decode b32decode b64decode b85decode // only need inputting: 16 32 64 85')
