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
import time
from typing import Iterator, Union

from lite_tools import MySqlConfig
from lite_tools import MySql as LiteMySql
from lite_tools.exceptions.SqlExceptions import IterNotNeedRun


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
        super(MySql, self).__init__(pool=None, config=MySqlConfig(
            database=database,
            host=host,
            user=user,
            password=password,
            port=port,
            charset=charset,
            maxconnections=maxconnections,
            table_name=table_name,
            log=log))

    def select(self, sql: str, count: bool = False, *, query_log: bool = True, **kwargs) -> Iterator:
        start_time = time.time()
        conn = self.connection()
        with conn.cursor() as cursor:  # 这里是有结果返回的
            cursor.execute(sql)
        conn.commit()
        items = cursor.fetchall()
        conn.close()
        end_time = time.time()
        all_num = len(items)
        if query_log is True:
            self.sql_log(f"耗时: {end_time - start_time:.3f}s 获取到内容行数有: [ {all_num} ]", sql, "success")
        if all_num == 0:
            if kwargs.get("_function_use") is True:
                raise IterNotNeedRun
            return
        for row in items:
            if count is False:
                yield row[0] if len(row) == 1 else row
            else:
                yield all_num, row[0] if len(row) == 1 else row
                all_num -= 1

        if all_num < kwargs.get("_limit_num", 0):  # 如果本次数据小于限制的数据 就终止继续迭代 当时获得了的数据还是要继续抛的
            raise IterNotNeedRun

    def select_iter(self, sql: str, limit: int = 1000) -> Iterator:
        yield from super().select_iter(sql, limit)

    def count(self, where: Union[dict, str] = None) -> int:
        return super().count(where)

    def exists(self, where: Union[dict, str]) -> bool:
        return super().exists(where)

    def insert(self, keys: Union[dict, list, tuple], values: list = None, ignore: bool = False):
        """这里目前只支持单条的 字典映射关系插入"""
        super().insert(keys, values, ignore)

    def update(self, items: dict, where: Union[dict, str]):
        """预留 """
        super().update(items, where)

    def delete(self, where: Union[dict, str]):
        """预留 """
        super().delete(where)
