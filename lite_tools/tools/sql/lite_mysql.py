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
from threading import RLock
from typing import Iterator, Union, Literal

import pymysql
from dbutils.pooled_db import PooledDB

from lite_tools.tools.utils.logs import logger
from lite_tools.tools.sql.config import MySqlConfig
from lite_tools.tools.sql.SqlLog import log_level
from lite_tools.tools.sql.lib_mysql_string import SqlString
from lite_tools.exceptions.SqlExceptions import DuplicateEntryException, IterNotNeedRun


class MySql:
    def __init__(
            self,
            pool: PooledDB = None,
            *,
            config: MySqlConfig = None,
            table_name: str = None,
            log_rule: Literal['default', 'each'] = 'default'
    ):
        """
        pool: 如果用的自己构建的连接池 那么就传自己构建好了的进来，但是如果要用insert,update,delete等方法就还需要额外传入table_name
            | from dbutils.pooled_db import PooledDB 需要这个pool
        config: from lite_tools import MySqlConfig --> 然后构建一个 config 对象 传入即可,这个配置文件不需要传table_name
            |默认参数--> database: str,
                        host: str,
                        user: str,
                        password: str = "",
                        port: int = 3306,
                        charset: str = "utf8mb4",
                        maxconnections: int = 20,
                        table_name: str = None,
        table_name: 如果是自己传入pool 那么就需要传入这个参数
        log_rule  : 打印日志的模式，默认是每隔一段时间或者一定的量打印一下，可以设置为each 每条打印
        """
        if pool:
            self.log = True   # 默认肯定是要打印日志的啦
            self.pool = pool
            self.table_name = table_name
        elif not pool and config and isinstance(config, MySqlConfig):
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
        # 以下统计均是 统计一个实例运行周期的操作
        self.change_line = {
            "insert": 0,
            "update": 0,
            "delete": 0
        }   # 记录一下改变的行数
        self.not_change_line = {
            "insert": 0,
            "update": 0,
            "delete": 0
        }   # 操作了 但是没有改变的行数
        self.lock = RLock()
        self.start_time = time.time()
        self.log_rule = log_rule

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

    def execute(self, sql: str, batch: bool = False, log: bool = True, mode: str = None) -> int:
        """不走智能执行的时候走这里可以执行手动输入的sql语句 这里的log不与全局self.log共享"""
        if not sql:
            logger.warning(f"传入了空sql语句--> sql:[ {sql} ]")
            return 0
        assert self._secure_check(sql), '删除操作终止!!!'
        start_time = time.time()
        conn = self.connection()
        try:
            with conn.cursor() as cursor:    # 这里是返回影响的行数
                result = cursor.execute(sql)
            conn.commit()
            end_time = time.time()
            if mode is not None:
                with self.lock:
                    if result == 0:
                        self.not_change_line[mode] += 1
                    else:
                        self.change_line[mode] += result

            # 增删改查  这里mode不会碰到查的  # 如果总改动行数为50的倍数就可以打印一下
            change_line_all = sum(self.change_line.values(), sum(self.not_change_line.values()))
            # 改变行和时间都可作打印依据
            if self.log_rule == "each" or (
                    self.log == "all" or change_line_all % 50 == 0 or int(time.time() - self.start_time) % 60 == 0
            ):
                self._print_rate(mode, end_time, start_time, result)
            return result
        except Exception as err:
            if str(err).find("Duplicate entry") != -1 and log is False:
                return 0
            end_time = time.time()
            self.sql_log(f"耗时: {end_time-start_time:.3f}s 异常原因: [{err}]", sql, "error")
            conn.rollback()
            if str(err).find("Duplicate entry") != -1 and batch is True:
                logger.warning(f"批量操作的数据有重复,现在转入单条操作,重复的字段内容日志将不会再打印:{err}")
                raise DuplicateEntryException
            return -1
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
            self.sql_log(f"SELECT-耗时: {end_time-start_time:.3f}s 获取到内容行数有: [ {all_num} ]", sql, "success")
        if all_num == 0:  # 如果这次结果是 0 那就是没有数据了
            if kwargs.get("_function_use") is True:
                raise IterNotNeedRun
            return
        for row in items:
            if count is False:
                yield row[0] if len(row) == 1 else row
            else:
                yield all_num, row[0] if len(row) == 1 else row
                all_num -= 1

        if all_num < kwargs.get("_limit_num", 0):   # 如果本次数据小于限制的数据 就终止继续迭代 当时获得了的数据还是要继续抛的
            raise IterNotNeedRun

    def select_iter(self, sql: str, limit: int = 1000) -> Iterator:
        """
        通过批量的迭代获取数据
        :param sql   : 只需要传入主要的逻辑 limit 部分用参数管理
        :param limit : 这里交给我来自动管理 默认我给了1000
        return: 如果传入count=True 那么第一个参数是行数,第二个参数是剩余行数w2  Q12
        """
        sql = sql.rstrip('; ')  # 剔除右边的符号
        if "limit" in sql.lower():
            sql = re.sub(r' limit \d+, *\d+| limit +\d+', '', sql, re.I)  # 剔除原先句子中的
        cursor = 0
        while True:
            new_sql = f"{sql} LIMIT {cursor}, {limit};"
            try:
                yield from self.select(new_sql, _function_use=True, _limit_num=limit)
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
        return False

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
        这里目前只支持单条的 字典映射关系插入 当然你要多值传入我也兼容 这里的匹配比较迷，但是习惯就好 这里就不兼容存在更新不存在插入了
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
            self.execute(sql, batch, mode="insert")
        except DuplicateEntryException:
            if values is None and isinstance(items, (list, tuple)):
                for each_key in items:
                    new_sql = self.sql_base.insert(each_key, values, ignore)
                    self.execute(new_sql, log=False, mode="insert")
            elif values is not None and isinstance(values, (list, tuple)):
                for each_value in values:
                    new_sql = self.sql_base.insert(items, each_value, ignore)
                    self.execute(new_sql, log=False, mode="insert")

    def replace(self, items: Union[dict, list, tuple], values: list = None) -> None:
        """
        存在更新 不存在覆盖 但是没有写的的字段会置为null
        参数同insert 不过少了一个ignore判断
        """
        self._check_table()
        if isinstance(items, (list, tuple)):
            batch = True
        else:
            batch = False
        sql = self.sql_base.replace(items, values)
        try:
            self.execute(sql, batch, mode="insert")
        except Exception as err:
            logger.error(f"执行异常--> {sql} : {err}")

    def update(self, items: dict, where: Union[dict, str]) -> None:
        """
        更新数据
        :param items: 更新的结果 字典表示
        :param where: 需要更新数据的时候使用的条件
        """
        self._check_table()
        sql = self.sql_base.update(items, where)
        self.execute(sql, mode="update")

    def delete(self, where: Union[dict, str]) -> None:
        """
        删除数据操作
        :param where: 需要删除数据的时候使用的条件
        """
        self._check_table()
        sql = self.sql_base.delete(where)
        self.execute(sql, mode="delete")

    def connection(self):
        """获取链接对象"""
        conn = self.pool.connection()
        return conn

    def _check_table(self):
        if not self.table_name:
            self.sql_log("你现在执行的操作是需要传入 table 的名字 mysql = MySql(table_name='xxx')", "", "error")
            raise ValueError

    def _secure_check(self, string: str) -> bool:
        """
        安全检查-->程序里面不给你操作drop操作的
        """
        if string.upper().startswith("DROP"):
            self.sql_log(f"SQL: {string}  确定要删除操作吗? Y/N", "", "warning")
            flag = input(">>> ")
            if flag.upper() == "Y":
                self.sql_log(f"哈哈哈 这里是唬你的 程序里面不给你--DROP--操作的 我肯定直接报错啦 ( •̀ ω •́ )y", "", "success")
                return False
        return True

    def _print_rate(self, mode: str, end_time, start_time, result):
        all_line = self.change_line[mode] + self.not_change_line[mode]
        rate = round(all_line / (time.time() - self.start_time), 3)  # 平均每秒改变行
        other_log = f"-->总影响行数={self.change_line[mode]}; 总未影响行={self.not_change_line[mode]}; 效率={rate} line/s;"
        self.sql_log(
            f"模式:[{mode}]{other_log} 本条耗时:{end_time - start_time:.3f}s 本次影响行={result}", "", "success", True
        )

    def sql_log(self, string: str, sql_string: str, string_level: str, output: bool = False) -> None:
        """
        level: (error > warning > info > success > debug)  目前只管是否要打日志 没有弄等级处理
        :param string: 需要提示的信息
        :param sql_string: 执行的sql语句
        :param string_level: 传入过来的等级
        :param output      : 默认不打印 弄这个参数主要是控制什么时候打印内容 不要一直打印 要分块打印输出数据
        """
        if not self.log or not output:
            return

        level_rate, log_func = log_level.get(string_level.lower(), (0, None))
        if level_rate:
            log_func(f"{string}{'' if not sql_string else '  SQL --> '+sql_string}")
