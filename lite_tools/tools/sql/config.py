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

from lite_tools.tools.core.lite_parser import try_get
from lite_tools.exceptions.SqlExceptions import EmptyConfigException, KeyFieldNeedError


class MySqlConfig:
    def __init__(
        self,
        database: str,
        host: str,
        user: str,
        password: str,
        port: int = 3306,
        charset: str = "utf8mb4",
        cursor: Literal['tuple', 'dict', 'stream', 'dict_stream'] = "tuple",
        max_connections: int = 20,
        table_name: str = None,
        log: bool = True
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

    @classmethod
    def new(cls, config: dict):
        if not config:
            raise EmptyConfigException
        database = try_get(config, "database|db")
        if not database:
            raise KeyFieldNeedError("database or db")

        host = try_get(config, "host")
        if not host:
            raise KeyFieldNeedError("host")

        user = try_get(config, "user")
        if not user:
            raise KeyFieldNeedError("user")

        password = try_get(config, "password")
        if not password:
            raise KeyFieldNeedError("password")

        this = cls(
            database=database,
            host=host,
            user=user,
            password=password
        )

        port = try_get(config, "port")
        if port:
            this.port = port

        charset = try_get(config, "charset")
        if charset:
            this.charset = charset

        max_connections = try_get(config, "max_connections")
        if max_connections:
            this.max_connections = max_connections

        table_name = try_get(config, "table_name")
        if table_name:
            this.table_name = table_name

        cursor = try_get(config, "cursor")
        if cursor:
            this.cursor = cursor

        log = try_get(config, "log")
        if log:
            this.log = log

        return this


_base_field = {
    "line": 0,     # 操作了多少行
    "change": 0,   # 操作行的时候改变了多少行
    "time": 0,     # 操作行的时间累积
}


class CountConfig:
    def __init__(self):
        self.log_jar = {}
        self.lock = RLock()

    def init(self, table: str, mode: str):
        """初始化模板数据字段"""
        if table not in self.log_jar:
            self.log_jar[table] = {}
        if mode not in self.log_jar[table]:
            self.log_jar[table][mode] = copy.deepcopy(_base_field)

    def add_line(self, table: str, mode: str, num: int = 0) -> int:
        self.init(table, mode)
        with self.lock:
            self.log_jar[table][mode]["line"] += num
        return self.log_jar[table][mode]["line"]

    def add_change(self, table: str, mode: str, num: int = 0) -> int:
        self.init(table, mode)
        with self.lock:
            self.log_jar[table][mode]["change"] += num
        return self.log_jar[table][mode]["change"]

    def add_time(self, table: str, mode: str, ts: float = 0) -> float:
        self.init(table, mode)
        with self.lock:
            self.log_jar[table][mode]["time"] += ts
        return self.log_jar[table][mode]["time"]

    def get_rate(self, table: str, mode: str):
        self.init(table, mode)
        this_round = self.log_jar[table][mode]
        return f"{this_round['line']/(this_round['time'] or 1):.2f} line/s"

    def get_change(self, table: str, mode: str):
        self.init(table, mode)
        return self.log_jar[table][mode]["change"]

    def get_line(self, table: str, mode: str):
        self.init(table, mode)
        return self.log_jar[table][mode]["line"]
