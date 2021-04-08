# -*- coding: utf-8 -*-
# @Time   : 2021-04-07 12:23
# @Author : Lodge
from hashlib import (
    md5, sha1, sha224, sha256, sha384, sha512,
    sha3_224, sha3_256, sha3_384, sha3_512
)


def get_md5(s: str, upper: bool = False, encoding='utf-8', to_bin: bool = False) -> str:
    """
    利用md5加密内容
    :param s: 加密前字符串
    :param upper: 是否返回大写的字符串 默认 False --> 返回小写
    :param encoding: 字符串的编码方式 默认 utf-8
    :param to_bin: 是否返回二进制串   默认 False --> 返回十六进制
    :return: 加密后字符串
    """
    md5_obj = md5()
    try:
        md5_obj.update(s.encode(encoding))
        if to_bin is True:
            result = md5_obj.digest()
        else:
            result = md5_obj.hexdigest()
        if upper is True:
            result = result.upper()
        return result
    except Exception as e:
        return f"数据异常: {e}"


def get_sha(s: str, mode: int = 256, encoding='utf-8', to_bin: bool = False) -> str:
    """
    获取shaX的加密内容
    :param s: 加密前字符串
    :param mode: 可以加密的模式: sha1 sha224 sha256 sha384 sha512 只需要传入数字即可 默认: 256
    :param encoding: 字符串的编码方式 默认 utf-8
    :param to_bin: 是否返回二进制串   默认 False --> 返回十六进制
    :return: 加密后字符串
    """
    if mode in [1, 224, 256, 384, 512]:
        sha_obj = eval(f"sha{mode}()")
        try:
            sha_obj.update(s.encode(encoding))
        except Exception as e:
            return f"数据异常: {e}"
        if to_bin is True:
            result = sha_obj.digest()
        else:
            result = sha_obj.hexdigest()
    else:
        print('SUPPORT: sha1 sha224 sha256 sha384 sha512// only need inputting: 1 224 256 384 512')
        result = ""
    return result


def get_sha3(s: str = "", mode=256, encoding='utf-8', to_bin: bool = False) -> str:
    """
    获取sha3_X的加密内容
    :param s: 加密前字符串
    :param mode: 可以加密的模式: sha3_224 sha3_256 sha3_384 sha3_512 只需要传入数字即可 默认: 256
    :param encoding:
    :param to_bin:
    :return:
    """
    if mode in [224, 256, 384, 512]:
        sha_obj = eval(f"sha3_{mode}()")
        try:
            sha_obj.update(s.encode(encoding))
        except Exception as e:
            return f"数据异常: {e}"
        if to_bin is True:
            result = sha_obj.digest()
        else:
            result = sha_obj.hexdigest()
    else:
        print('SUPPORT: sha3_224 sha3_256 sha3_384 sha3_512// only need inputting: 224 256 384 512')
        result = ""
    return result
