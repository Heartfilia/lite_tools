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
"""
import copy
from threading import RLock

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class MySqlConfig:
    def __init__(
        self,
        database: str,
        host: str,
        user: str,
        password: str = "",
        port: int = 3306,
        charset: str = "utf8mb4",
        cursor: Literal['tuple', 'dict', 'stream', 'dict_stream'] = "tuple",
        max_connections: int = 20,
        table_name: str = None,
        log: Literal[True, False, "all"] = True
    ):
        """
        mysql的配置文件 这里只有默认的配置 要改其他的可以自己传pool配置
        :param database (*): database的名字
        :param host     (*): 数据的host啦
        :param user     (*): 数据库的用户
        :param password (*): 数据库的密码
        :param port  (3306): 端口
        :param charset ('utf8mb4'): 默认的字符集格式
        :param max_connections (20): 默认的最大链接数
        :param cursor  (tuple): cursorclass 的参数 名字简化一下 默认返回数据样式就是元组，可以设置 dict 为字典样式返回 stream流式返回
        :param table_name (str)   : 这个是给insert  update  delete 用的
        :param log        (bool)   : 是否打印日志 不建议关闭 要不然成不成功都不知道 如果要每一条都打印输入 all
        """
        self.database = database
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.charset = charset
        self.max_connections = max_connections
        self.table_name = table_name
        self.cursor = cursor
        self.log = log


# 以下统计均是 统计一个实例运行周期的操作
BASE_TEMPLATE = {
    "change": {
        "insert": 0,
        "update": 0,
        "delete": 0,
    },   # 记录一下改变的行数
    "not_change": {
        "insert": 0,
        "update": 0,
        "delete": 0,
    },   # 操作了 但是没有改变的行数
    "count": {
        "total": 0,
        "run": 0
    }    # 总行数  surplus
}


class CountConfig:
    def __init__(self):
        self.log_jar = {}
        self.lock = RLock()

    def init(self, table):
        """初始化模板数据字段"""
        if table not in self.log_jar:
            self.log_jar[table] = copy.deepcopy(BASE_TEMPLATE)

    def set_change(self, table: str, mode: str, num: int = 0):
        self.init(table)
        with self.lock:
            self.log_jar[table]["change"][mode] += num

    def get_change(self, table: str, mode: str):
        return self.log_jar[table]["change"][mode]

    def set_not_change(self, table: str, mode: str, num: int = 0):
        self.init(table)
        with self.lock:
            self.log_jar[table]["not_change"][mode] += num

    def get_not_change(self, table: str, mode: str):
        return self.log_jar[table]["not_change"][mode]

    def set_count(self, table: str, mode: str, num: int = 0):
        self.init(table)
        with self.lock:
            self.log_jar[table]["count"][mode] += num

    def get_count(self, table: str, mode: str):
        return self.log_jar[table]["count"][mode]
