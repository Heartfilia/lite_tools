# -*- coding: utf-8 -*-
# @Author  : Lodge
"""
JS 常见数值与位运算兼容工具。
"""
import ctypes
import math
from typing import Union

from lite_tools.tools.core.lib_base64 import get_b64d as atob
from lite_tools.tools.core.lib_base64 import get_b64e as btoa

Number = Union[float, int]
_DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz'
_MAX_FRACTION_DIGITS = 16


def _ensure_base(base: int) -> int:
    if not 2 <= base <= 36:
        raise ValueError('base must be between 2 and 36')
    return base


def _is_integer(number: Number) -> bool:
    return isinstance(number, int) or (isinstance(number, float) and number.is_integer())


def to_int32(number: Number) -> int:
    """
    对齐 JS ToInt32 的 32 位有符号整数结果。
    """
    return ctypes.c_int32(int(number)).value


def to_uint32(number: Number) -> int:
    """
    对齐 JS ToUint32 的 32 位无符号整数结果。
    """
    return ctypes.c_uint32(int(number)).value


def _integer_to_base(number: int, base: int) -> str:
    _ensure_base(base)
    if number == 0:
        return '0'

    sign = '-' if number < 0 else ''
    number = abs(number)
    chars = []
    while number:
        number, remainder = divmod(number, base)
        chars.append(_DIGITS[remainder])
    return sign + ''.join(reversed(chars))


def _fraction_to_base(fraction: float, base: int, precision: int) -> str:
    if fraction <= 0 or precision <= 0:
        return ''

    chars = []
    for _ in range(precision):
        fraction *= base
        digit = int(fraction)
        chars.append(_DIGITS[digit])
        fraction -= digit
        if math.isclose(fraction, 0.0, abs_tol=1e-15):
            break
    return ''.join(chars).rstrip('0')


def to_string(number: Number, base: int = 10, precision: int = _MAX_FRACTION_DIGITS) -> str:
    """
    将数字转成指定进制字符串，覆盖常见 JS toString(radix) 场景。
    """
    _ensure_base(base)

    if not isinstance(number, (int, float)):
        raise TypeError('number must be int or float')

    if isinstance(number, float):
        if math.isnan(number):
            return 'NaN'
        if math.isinf(number):
            return 'Infinity' if number > 0 else '-Infinity'

    if base == 10:
        if _is_integer(number):
            return str(int(number))
        return format(float(number), '.15g')

    if _is_integer(number):
        return _integer_to_base(int(number), base)

    sign = '-' if number < 0 else ''
    number = abs(float(number))
    integer_part = int(number)
    fraction_part = number - integer_part

    integer_text = _integer_to_base(integer_part, base)
    fraction_text = _fraction_to_base(fraction_part, base, precision)
    if not fraction_text:
        return sign + integer_text
    return f'{sign}{integer_text}.{fraction_text}'


def to_string_36(number: Number) -> str:
    """
    将数字转为 36 进制字符串。
    """
    return to_string(number, 36)


def to_string_16(number: Number) -> str:
    """
    将数字转为 16 进制字符串。
    """
    return to_string(number, 16)


def xor(num_1: int, num_2: int) -> int:
    """
    异或，结果保持 32 位有符号整数语义。
    """
    return to_int32(to_int32(num_1) ^ to_int32(num_2))


def and_(num_1: int, num_2: int) -> int:
    """
    按位与，结果保持 32 位有符号整数语义。
    """
    return to_int32(to_int32(num_1) & to_int32(num_2))


def or_(num_1: int, num_2: int) -> int:
    """
    按位或，结果保持 32 位有符号整数语义。
    """
    return to_int32(to_int32(num_1) | to_int32(num_2))


def bit_not(num: int) -> int:
    """
    按位取反，结果保持 32 位有符号整数语义。
    """
    return to_int32(~to_int32(num))


def unsigned_right_shift(num: int, step: int) -> int:
    """
    JS 的 `num >>> step` 无符号右移。
    """
    return to_uint32(to_uint32(num) >> (step % 32))


def left_shift(num: int, step: int) -> int:
    """
    JS 的 `num << step` 左移。
    """
    return to_int32(to_int32(num) << (step % 32))


def dec_to_bin(num: Number) -> str:
    """
    十进制转二进制字符串，对齐常见 `toString(2)` 场景。
    """
    return to_string(num, 2)


to_string_2 = dec_to_bin


if __name__ == '__main__':
    samples = [35.51, 35, -12, 0.625]
    for value in samples:
        print(f'{value} -> bin: {to_string_2(value)}, hex: {to_string_16(value)}, base36: {to_string_36(value)}')
