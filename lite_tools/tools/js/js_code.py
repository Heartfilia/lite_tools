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
