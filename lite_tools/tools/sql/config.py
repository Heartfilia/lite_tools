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

try:
    from pymysql.converters import decoders
except ImportError:
    decoders = None

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
        log: bool = True,

        unix_socket=None,
        conv=None,
        sql_mode=None,
        read_default_file=None,
        use_unicode=None,
        client_flag=0,
        init_command=None,
        connect_timeout=None,
        read_default_group=None,
        autocommit=False,
        echo=False,
        local_infile=False,
        loop=None,
        ssl=None,
        auth_plugin='',
        program_name='',
        server_public_key=None,
        **kwargs
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

        # 其它的虽然添加了 但是我目前还没用到 以后再说
        """
        if conv is None:
            self.conv = decoders
        else:
            self.conv = conv

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

        self.unix_socket = unix_socket
        self.sql_mode = sql_mode
        self.read_default_file = read_default_file
        self.use_unicode = use_unicode
        self.client_flag = client_flag
        self.init_command = init_command
        self.connect_timeout = connect_timeout
        self.read_default_group = read_default_group
        self.autocommit = autocommit
        self.echo = echo
        self.local_infile = local_infile
        self.loop = loop
        self.ssl = ssl
        self.auth_plugin = auth_plugin
        self.program_name = program_name
        self.server_public_key = server_public_key
        self._other = {}

    @classmethod
    def new(cls, config: dict):
        if not config:
            raise EmptyConfigException
        database = try_get(config, "database|db")
        if not database:
            raise KeyFieldNeedError("database or db")

        host = try_get(config, "host|hostname")
        if not host:
            raise KeyFieldNeedError("host or hostname")

        user = try_get(config, "user|username")
        if not user:
            raise KeyFieldNeedError("user or username")

        password = try_get(config, "password|pass")
        if not password:
            raise KeyFieldNeedError("password or pass")

        this = cls(
            database=database,
            host=host,
            user=user,
            password=password
        )

        port = try_get(config, "port")
        if port is not None:
            this.port = port

        charset = try_get(config, "charset")
        if charset is not None:
            this.charset = charset

        max_connections = try_get(config, "max_connections|maxsize")
        if max_connections is not None:
            this.max_connections = max_connections

        table_name = try_get(config, "table_name")
        if table_name is not None:
            this.table_name = table_name

        cursor = try_get(config, "cursor|cursorclass")
        if cursor is not None:
            this.cursor = cursor

        log = try_get(config, "log")
        if log is not None:
            this.log = log

        conv = try_get(config, "conv")
        if conv is not None:
            this.conv = conv

        unix_socket = try_get(config, "unix_socket")
        if unix_socket is not None:
            this.unix_socket = unix_socket

        sql_mode = try_get(config, "sql_mode")
        if sql_mode is not None:
            this.sql_mode = sql_mode

        read_default_file = try_get(config, "read_default_file")
        if read_default_file is not None:
            this.read_default_file = read_default_file

        use_unicode = try_get(config, "use_unicode")
        if use_unicode is not None:
            this.use_unicode = use_unicode

        client_flag = try_get(config, "client_flag")
        if client_flag is not None:
            this.client_flag = client_flag

        init_command = try_get(config, "init_command")
        if init_command is not None:
            this.init_command = init_command

        connect_timeout = try_get(config, "connect_timeout")
        if connect_timeout is not None:
            this.connect_timeout = connect_timeout

        read_default_group = try_get(config, "read_default_group")
        if read_default_group is not None:
            this.read_default_group = read_default_group

        autocommit = try_get(config, "autocommit")
        if autocommit is not None:
            this.autocommit = autocommit

        echo = try_get(config, "echo")
        if echo is not None:
            this.echo = echo

        local_infile = try_get(config, "local_infile")
        if local_infile is not None:
            this.local_infile = local_infile

        loop = try_get(config, "loop")
        if loop is not None:
            this.loop = loop

        ssl = try_get(config, "ssl")
        if ssl is not None:
            this.ssl = ssl

        auth_plugin = try_get(config, "auth_plugin")
        if auth_plugin is not None:
            this.auth_plugin = auth_plugin

        program_name = try_get(config, "program_name")
        if program_name is not None:
            this.program_name = program_name

        server_public_key = try_get(config, "server_public_key")
        if server_public_key is not None:
            this.server_public_key = server_public_key

        this._other = config or {}
        return this

    def to_dict(self):
        """
        获取字典部分
        """
        obj = copy.deepcopy(self.__dict__)

        other = obj['_other']
        del obj['_other']
        if other:
            obj.update(other)

        return obj


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
