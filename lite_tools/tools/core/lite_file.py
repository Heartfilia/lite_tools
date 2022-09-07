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
下面对外放出的方法是性能最高的方法 还有以下N种 性能由高到低(耗时由低到高) 还有其它很多方法 太慢了就不写了
from functools import partial
with open(file_path) as f:
    return sum(x.count('\n') for x in iter(partial(f.read, _buffer), ''))
-------------------------------------------------------------------------
import subprocess
out = subprocess.getoutput("wc -l %s" % file_path)
return int(out.split()[0])
-------------------------------------------------------------------------
"""
from itertools import takewhile, repeat


_buffer = 1024 * 1024


def count_lines(file_path: str, encoding: str = 'utf-8') -> int:
    """
    获取文件的行数
    :param file_path: 传入文件的路径
    :param encoding: 文件打开格式 默认utf-8
    """
    with open(file_path, 'r', encoding=encoding) as f:
        buf_gen = takewhile(lambda x: x, (f.read(_buffer) for _ in repeat(None)))
        return sum(buf.count('\n') for buf in buf_gen)
