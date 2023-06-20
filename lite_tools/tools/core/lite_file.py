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
import os
import subprocess
from itertools import takewhile, repeat

from lite_tools.utils.lite_dir import lite_tools_dir
from lite_tools.tools.time.lite_time import get_time


_buffer = 1024 * 1024


def count_lines(file_path: str, encoding: str = None) -> int:
    """
    获取文件的行数
    :param file_path: 传入文件的路径
    :param encoding: 文件打开格式 默认根据系统格式
    """
    if not encoding:
        encoding = 'gb2312' if os.name == "nt" else 'utf-8'

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            buf_gen = takewhile(lambda x: x, (f.read(_buffer) for _ in repeat(None)))
            return sum(buf.count('\n') for buf in buf_gen)
    except (FileNotFoundError, FileExistsError):
        return 0


class LiteLogFile(object):
    """
    这个记录日志给**不频繁**输入**日志的文件用** 频繁的请用 loguru 这个包
    我这个是为了记录一些关键节点的日志...
    """
    def __init__(self, folder_name: str, file_name: str, encoding: str = None):
        self.encoding = encoding
        self.log_path = self._create_new_file(folder_name, file_name)

    def dump(self, message: str):
        """
        传入要记录的信息就好了 不用记录时间点 我这里有记录
        """
        tag = self._get_echo_tag()
        if os.name == "nt":
            trans_message = message.replace('^', '^^').replace(
                '>', '^>').replace(' ', '^ ').replace('|', '^|').replace('&', '^&').replace(
                '"', '^"').replace("'", "^'")
        else:
            trans_message = message.replace("'", "`")   # 单引号有问题我给换成这个符号了其它的暂时没啥大问题
        win_flag = '^' if os.name == 'nt' else ''
        string = f'[{get_time(fmt=True)}]{win_flag} {trans_message}'
        subprocess.call(
            f"echo {string if os.name == 'nt' else repr(string)} {tag} {self.log_path}",
            shell=True,
        )

    def _create_new_file(self, folder_name: str, file_name: str):
        """创建文件位置"""
        file_path = self._get_file_path(folder_name, file_name)
        if not os.path.exists(file_path):
            if not self.encoding:
                encoding = 'gb2312' if os.name == "nt" else 'utf-8'
            else:
                encoding = self.encoding
            with open(file_path, 'w', encoding=encoding) as f:  # 不调用其它的创建方案 为了兼容...
                f.write("")
        return file_path

    def _get_echo_tag(self):
        """echo命令用 文件超长要调整输出模式"""
        line_num = count_lines(self.log_path, encoding=self.encoding)
        return ">" if line_num > 9999 else ">>"   # 第10000行调整模式

    @staticmethod
    def _get_file_path(folder_name: str, file_name: str):
        """
        获取文件路径拉
        """
        base_path = lite_tools_dir()

        folder_path_dir = os.path.join(base_path, 'logs')
        if not os.path.exists(folder_path_dir):
            os.makedirs(folder_path_dir)

        folder_path = os.path.join(folder_path_dir, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if not file_name.lower().endswith('.log'):
            file_name += '.log'
        return os.path.join(folder_path, file_name)
