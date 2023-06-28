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
这个文件主要放一些 js转python的操作 比如 >>>   还有36进制等等 不过这里我还没有写 晚点弄
"""
import ctypes
from typing import Union

from lite_tools.tools.core.lib_base64 import get_b64e as btoa
from lite_tools.tools.core.lib_base64 import get_b64d as atob


def to_string_36(number: Union[float, int]) -> str:
    """
    将数字转为36进制字符串  TODO(浮点数处理还没有实现)
    """
    if number == 0 or not isinstance(number, int):
        return '0'
    base36 = []
    while number != 0:
        number, i = divmod(number, 36)
        base36.append('0123456789abcdefghijklmnopqrstuvwxyz'[i])
    return ''.join(reversed(base36))


def to_string_16(number: Union[float, int]) -> str:
    if number < 0:
        flag = "-"
        number = abs(number)
    else:
        flag = ""
    s = [flag + str(int(number)) + '.']
    number -= int(number)

    for _ in range(16):
        y = int(number * 16)
        s.append(f"{y:x}")
        number = number * 16 - y

    temp_ok = ''.join(s).rstrip('0')
    if "." in temp_ok:
        base, other = temp_ok.split('.')
        temp_ok = f"{int(base):x}.{other}"
    return temp_ok.strip(".")


"""
以下板块由 小小白 提供
"""


def xor(num_1: int, num_2: int):
    """
    异或 同 python ^ 主要是精度问题 所以这里放这里搞了一个
    """
    x, y = ctypes.c_int32(num_1).value, ctypes.c_int32(num_2).value
    return ctypes.c_int(x ^ y).value


def unsigned_right_shift(num: int,  step: int):
    """
    'num >>>  step' 无符号右移
    :param num: 需要移动的数
    :param  step: 移动的步数
    """
    x, y = ctypes.c_uint32(num).value,  step % 32
    return ctypes.c_uint32(x >> y).value


def left_shift(num: int,  step: int):
    """
    <<      num <<  step
    :param num: 需要移动的数据
    :param  step: 移动的步数
    """
    x, y = ctypes.c_int32(num).value,  step % 32
    return ctypes.c_int32(x << y).value


def dec_to_bin(num: Union[float, int]) -> str:
    """
    十进制浮点数转二进制 toString(2)
    """
    # 判断是否为浮点数
    if num == int(num):
        # 若为整数
        integer = '{:b}'.format(int(num))
        return integer
    else:
        # 若为浮点数
        if float(num) < 0:
            num = abs(num)
            flag = "-"
        else:
            flag = ""
        # 取整数部分
        integer_part = int(num)
        # 取小数部分
        decimal_part = num - integer_part
        # 整数部分进制转换
        integer_com = '{:b}'.format(integer_part)  # {:b}.format中b是二进制
        # 小数部分进制转换
        tem = decimal_part
        tmp_float = []
        while True:
            tem *= 2
            tmp_float += str(int(tem))  # 若整数部分为0则二进制部分为0，若整数部分为1则二进制部分为1 #将1或0放入列表
            if tem > 1:   # 若乘以2后为大于1的小数，则要减去整数部分
                tem -= int(tem)
            elif tem < 1:  # 乘以2后若仍为小于1的小数，则继续使用这个数乘2变换进制
                pass
            else:    # 当乘以2后正好为1，则进制变换停止
                break
        float_com = tmp_float
        return flag + integer_com + '.' + ''.join(float_com)


to_string_2 = dec_to_bin


if __name__ == '__main__':
    xx = 35.51
    result = to_string_36(xx)
    print(f'{xx} -->：{result}')
