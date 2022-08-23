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
import re
import time
from loguru import logger
from typing import Iterator, Union

import pymysql
from dbutils.pooled_db import PooledDB

from lite_tools.tools.sql.lib_mysql_string import SqlString
from lite_tools.tools.sql.config import Config
from lite_tools.tools.sql.SqlLog import log_level
from lite_tools.exceptions.SqlExceptions import DuplicateEntryException, IterNotNeedRun


class MySql:
    def __init__(
            self,
            pool: PooledDB = None,
            *,
            config: Config = None,
            table_name: str = None
    ):
        """
        这里打印的日志不可关闭  --->  除非你改我源码
        pool: 如果用的自己构建的连接池 那么就传自己构建好了的进来，但是如果要用insert,update,delete等方法就还需要额外传入table_name
            | from dbutils.pooled_db import PooledDB 需要这个pool
        config: from lite_tools import Config --> 然后构建一个 config 对象 传入即可,这个配置文件不需要传table_name,包含了的
            |默认参数--> database: str,
                        host: str,
                        user: str,
                        password: str = "",
                        port: int = 3306,
                        charset: str = "utf8mb4",
                        maxconnections: int = 20,
                        table_name: str = None,
        """
        if pool:
            self.log = True   # 默认肯定是要打印日志的啦
            self.pool = pool
            self.table_name = table_name
        elif not pool and config and isinstance(config, Config):
            self.pool = None
            self.config = config
            self.table_name = self.config.table_name
            self._init_mysql(
                self.config.database, self.config.maxconnections,
                self.config.host, self.config.port, self.config.user, self.config.password, self.config.charset
            )
            self.log = self.config.log
        else:
            raise ValueError

        if self.table_name is not None:
            self.sql_base = SqlString(self.table_name)
        else:
            self.sql_base = None

    def _init_mysql(self, database, maxconnections, host, port, user, password, charset):
        if self.pool is None:
            self.pool = PooledDB(
                creator=pymysql,  # 使用链接数据库的模块
                maxconnections=maxconnections,  # 连接池允许的最大连接数，0和None表示不限制连接数
                mincached=0,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxcached=0,  # 链接池中最多闲置的链接，0和None不限制
                maxshared=0,  # 链接池中最多共享的链接数量，0和None表示全部共享
                blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
                setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                ping=0,
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset=charset
            )

    def execute(self, sql: str, batch: bool = False, log: bool = True) -> None:
        """不走智能执行的时候走这里可以执行手动输入的sql语句 这里的log不与全局self.log共享"""
        assert self._secure_check(sql), '删除操作终止!!!'
        start_time = time.time()
        conn = self.connection()
        try:
            with conn.cursor() as cursor:    # 这里是返回影响的行数
                result = cursor.execute(sql)
            conn.commit()
            end_time = time.time()
            self._my_logger(f"耗时: {end_time-start_time:.3f}s 影响行数: [{result}]", "", "success")
        except Exception as err:
            if str(err).find("Duplicate entry") != -1 and log is False:
                return
            end_time = time.time()
            self._my_logger(f"耗时: {end_time-start_time:.3f}s 异常原因: [{err}]", sql, "error")
            conn.rollback()
            if str(err).find("Duplicate entry") != -1 and batch is True:
                logger.warning(f"批量操作异常 --> 现在转入单条操作... 重复的字段内容日志将不会再打印")
                raise DuplicateEntryException
        finally:
            conn.close()

    def select(self, sql: str, count: bool = False, *, query_log: bool = True, **kwargs) -> Iterator:
        """
        一次性查询全部数据
        :param sql: 传入的查询sql语句
        :param count: 是否需要统计剩余的行数 如果传入count=True 那么第一个参数是行数,第二个参数是剩余行数
        :param query_log: 是否把query的查询日志打印出来,默认就是打印出来
        :return:
        """
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
            self._my_logger(f"耗时: {end_time-start_time:.3f}s 获取到内容行数有: [ {all_num} ]", sql, "success")
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

    def select_iter(self, sql: str, limit: int) -> Iterator:
        """
        通过批量的迭代获取数据
        :param sql   : 只需要传入主要的逻辑 limit 部分用参数管理
        :param limit : 这里交给我来自动管理
        return: 如果传入count=True 那么第一个参数是行数,第二个参数是剩余行数
        """
        sql = sql.rstrip('; ')  # 剔除右边的符号
        if "limit" in sql.lower():
            sql = re.sub(r' limit \d+, *\d+| limit +\d+', '', sql, re.I)  # 剔除原先句子中的
        cursor = 0
        while True:
            new_sql = f"{sql} LIMIT {cursor}, {limit};"
            try:
                yield from self.select(new_sql, _function_use=True)
            except IterNotNeedRun:
                break
            cursor += limit

    def exists(self, where: Union[dict, str]) -> bool:
        """
        判断条件在不在该表中有数据
        :param where: 通过字典的方式传入条件(推荐) 或者字符串的条件
        """
        self._check_table()
        sql = self.sql_base.exists(where)
        for num in self.select(sql, query_log=False):
            if num == 0:
                return False
            else:
                return True
        return False   # 走不到这里来的(为了严谨)

    def count(self, where: Union[dict, str] = None) -> int:
        """
        判断有
        """
        self._check_table()
        sql = self.sql_base.count(where)
        for num in self.select(sql, query_log=False):
            return num

    def insert(self, items: Union[dict, list, tuple], values: list = None, ignore: bool = False) -> None:
        """
        这里目前只支持单条的 字典映射关系插入 当然你要多值传入我也兼容 这里的匹配比较迷，但是习惯就好
        :param items: 插入的值(单条的话只需要传这个 传字典就好了) (多条的话这里可以传列表里字典)
        :param values: 如果多条插入 值可以这里插入
        :param ignore: 是否忽略主键重复的警报
        """
        self._check_table()
        if isinstance(items, (list, tuple)):
            batch = True
        else:
            batch = False
        sql = self.sql_base.insert(items, values, ignore=ignore)
        try:
            self.execute(sql, batch)
        except DuplicateEntryException:
            if values is None:
                for each_key in items:
                    new_sql = self.sql_base.insert(each_key, values, ignore)
                    self.execute(new_sql, log=False)
            else:
                for each_value in values:
                    new_sql = self.sql_base.insert(items, each_value, ignore)
                    self.execute(new_sql, log=False)

    def update(self, items: dict, where: Union[dict, str]) -> None:
        """
        更新数据
        :param items: 更新的结果 字典表示
        :param where: 需要更新数据的时候使用的条件
        """
        self._check_table()
        sql = self.sql_base.update(items, where)
        self.execute(sql)

    def delete(self, where: Union[dict, str]) -> None:
        """
        删除数据操作
        :param where: 需要删除数据的时候使用的条件
        """
        self._check_table()
        sql = self.sql_base.delete(where)
        self.execute(sql)

    def connection(self):
        """获取链接对象"""
        conn = self.pool.connection()
        return conn

    def _check_table(self):
        if not self.table_name:
            self._my_logger("你现在执行的操作是需要传入 table 的名字 mysql = MySql(table_name='xxx')", "", "error")
            raise ValueError

    def _secure_check(self, string: str) -> bool:
        """
        安全检查-->程序里面不给你操作drop操作的
        """
        if string.upper().startswith("DROP"):
            self._my_logger(f"SQL: {string}  确定要删除操作吗? Y/N", "", "warning")
            flag = input(">>> ")
            if flag.upper() == "Y":
                self._my_logger(f"哈哈哈 这里是唬你的 程序里面不给你--DROP--操作的 我肯定直接报错啦 ( •̀ ω •́ )y", "", "success")
                return False
        return True

    def _my_logger(self, string: str, sql_string: str, string_level: str) -> None:
        """
        level: (error > warning > info > success > debug)  目前只管是否要打日志 没有弄等级处理
        :param string: 需要提示的信息
        :param sql_string: 执行的sql语句
        :param string_level: 传入过来的等级
        """
        if not self.log:
            return

        level_rate, log_func = log_level.get(string_level.lower(), (0, None))
        if level_rate:
            log_func(f"{string}{'' if not sql_string else '  SQL --> '+sql_string}")
