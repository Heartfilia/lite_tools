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

from lite_tools.tools.core.lib_base64 import get_b64e as btoa
from lite_tools.tools.core.lib_base64 import get_b64d as atob


_base_num_str = '0123456789abcdefghijklmnopqrstuvwxyz'


def to_string_36(number: int) -> str:
    """将数字转为36进制字符串"""
    if number == 0 or not isinstance(number, int):
        return '0'
    base36 = []
    while number != 0:
        number, i = divmod(number, 36)
        base36.append(_base_num_str[i])
    return ''.join(reversed(base36))


"""
以下板块由 小小白 提供
"""

def xor(x, y):
    x, y = ctypes.c_int32(x).value, ctypes.c_int32(y).value
    return ctypes.c_int(x ^ y).value


def unsigned_right_shift(x, y):
    x, y = ctypes.c_uint32(x).value, y % 32
    return ctypes.c_uint32(x >> y).value


def left_shift(x, y):
    x, y = ctypes.c_int32(x).value, y % 32
    return ctypes.c_int32(x << y).value


# 十进制浮点数转二进制
def dectbin(num):
    # 判断是否为浮点数
    if num == int(num):
        # 若为整数
        integer = '{:b}'.format(int(num))
        return integer
    else:
        # 若为浮点数
        # 取整数部分
        integer_part = int(num)
        # 取小数部分
        decimal_part = num - integer_part
        # 整数部分进制转换
        integercom = '{:b}'.format(integer_part)  # {:b}.foemat中b是二进制
        # 小数部分进制转换
        tem = decimal_part
        tmpflo = []
        # for i in range(accuracy):
        A = True
        while A:
            tem *= 2
            tmpflo += str(int(tem))  # 若整数部分为0则二进制部分为0，若整数部分为1则二进制部分为1 #将1或0放入列表
            if tem > 1:   # 若乘以2后为大于1的小数，则要减去整数部分
                tem -= int(tem)
            elif tem < 1:  # 乘以2后若仍为小于1的小数，则继续使用这个数乘2变换进制
                pass
            else:    # 当乘以2后正好为1，则进制变换停止
                break
        flocom = tmpflo
        return integercom + '.' + ''.join(flocom)


if __name__ == '__main__':
    number = 2.8
    result = dectbin(number)
    print(f'{number}的二进制数为：{result}')
