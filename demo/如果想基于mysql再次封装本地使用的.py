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
from typing import Iterator, Union

from lite_tools import SqlString
from lite_tools import MySql as LiteMySql


class DuplicateEntryException(Exception):
    def __init__(self):
        pass


class MySql(LiteMySql):
    def __init__(
            self,
            database: str = "这里传入你要操作的数据库",
            maxconnections: int = 20,   # 这里设置你要的默认链接数
            host: str = "这里设置你mysql的host",
            port: int = 3306,   # 这里设置你mysql的端口
            user: str = "mysql的用户名",
            password: str = "mysql的密码",
            charset: str = "utf8mb4",
            *,
            table_name: str = None,   # 这个是给insert  update  delete 用的
            log: bool = True
    ):
        """
        只需要把上面的参数设置一下然后就可以放到你们自己的包里直接使用 不用每次都填入账号密码 或者自己写个连接池对象 或者 Config
        用我lite_tools里的MySql初始化传入封包也可以

        from xxx import MySql
        mysql = MySql(table_name="yyy")

        mysql.insert({})
        mysql.update({}, {})
        mysql.delete({})
        for row in mysql.select("SELECT * FROM xxxxxx;"):
            print(row)
        """
        self.log = log
        self.pool = None
        self.table_name = table_name
        if table_name is not None:
            self.sql_base = SqlString(table_name)
        else:
            self.sql_base = None
        self._init_mysql(database, maxconnections, host, port, user, password, charset)

    def select(self, sql: str, count: bool = False) -> Iterator:
        yield from super().select(sql, count)

    def insert(self, keys: Union[dict, list, tuple], values: list = None, ignore: bool = False):
        """这里目前只支持单条的 字典映射关系插入"""
        super(MySql, self).insert(keys, values, ignore)

    def update(self, items: dict, where: Union[dict, str]):
        """预留 """
        super().update(items, where)

    def delete(self, where: Union[dict, str]):
        """预留 """
        super().delete(where)
