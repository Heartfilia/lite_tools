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
from typing import Iterator, Union, Mapping, List
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import pymysql
from dbutils.pooled_db import PooledDB

from lite_tools.tools.utils.logs import logger
from lite_tools.tools.sql.config import MySqlConfig
from lite_tools.tools.sql.SqlLog import log_level
from lite_tools.tools.core.lite_cache import Buffer
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
                        cursor: str = 'tuple',
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
                self.config.host, self.config.port, self.config.user, self.config.password, self.config.charset,
                self.config.cursor
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
        self.row_count = {
            "total": 0,
            "run": 0
        }   # 总行数  surplus
        self.lock = RLock()
        self.start_time = time.time()
        self.log_rule = log_rule

    def _init_mysql(self, database, maxconnections, host, port, user, password, charset, cursor):
        if self.pool is None:
            if cursor == "dict":
                cursor_type = pymysql.cursors.DictCursor
            else:
                cursor_type = pymysql.cursors.Cursor
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
                charset=charset,
                cursorclass=cursor_type   # 调整返回结果的样式
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
                    if mode == 'update':
                        self.row_count["run"] += 1

            self._print_rate(mode, end_time, start_time, result)
            return result
        except Exception as err:
            if str(err).find("Duplicate entry") != -1 and log is False:
                return 0
            end_time = time.time()
            # 只要不是主键重复的错误 那么都需要打印出来
            if str(err).find("Duplicate entry") == -1:
                self.sql_log(f"Cost: {end_time-start_time:.3f}s Exception: [{err}]", sql, "error", output=True)

            conn.rollback()
            if str(err).find("Duplicate entry") != -1 and batch is True:
                logger.warning(f"批量操作的数据有重复,现在转入单条操作,重复的字段内容日志将不会再打印:{err}")
                raise DuplicateEntryException

            if mode in ['insert', 'update']:
                with self.lock:
                    self.not_change_line[mode] += 1
                self._print_rate(mode, end_time, start_time, 0, flag="info")
            return -1
        finally:
            conn.close()

    def execute_many(self, sql: str, values: list, mode: str, options: str = None) -> int:
        if not sql:
            logger.warning(f"传入了空sql语句--> sql:[ {sql} ]")
            return 0
        start_time = time.time()
        conn = self.connection()
        try:
            with conn.cursor() as cursor:    # 这里是返回影响的行数
                result = cursor.executemany(sql, values)
            conn.commit()
            end_time = time.time()
            if mode == "update_batch":
                log_mode = "update"
            else:
                log_mode = "insert"
            with self.lock:
                if result == 0:
                    self.not_change_line[log_mode] += 1
                else:
                    if log_mode == "insert" and options == "update":
                        # 如果重复了主键 并且设置了更新模式为update的话 实际行操作会有双倍 尝试插入+修改 所以我们这里统计数据需要除去一半
                        self.change_line[log_mode] += result // 2
                    else:
                        self.change_line[log_mode] += result
                if mode == 'update_batch':
                    self.row_count["run"] += 1
            self._print_rate(log_mode, end_time, start_time, result)
            return result
        except Exception as err:
            logger.error(f"批量操作报错为: {err}")
            conn.rollback()
            return -1
        finally:
            conn.close()

    def select(self, sql: str, count: bool = False, *, query_log: bool = True, fetch: Literal['all', 'one'] = 'all',
               **kwargs) -> Iterator:
        """
        一次性查询全部数据
        :param sql: 传入的查询sql语句
        :param count: 是否需要统计剩余的行数 如果传入count=True 那么第一个参数是行数,第二个参数是剩余行数
        :param query_log: 是否把query的查询日志打印出来,默认就是打印出来
        :param fetch: 获取数据模式 默认 fetchall 设置 one 就是 fetchone
        :return:
        """
        start_time = time.time()
        conn = self.connection()
        with conn.cursor() as cursor:  # 这里是有结果返回的
            cursor.execute(sql)
        conn.commit()
        if fetch == 'one':
            item = cursor.fetchone()
            items = [item]
        else:
            items = cursor.fetchall()
        conn.close()
        end_time = time.time()
        all_num = len(items)
        if query_log is True:
            self.sql_log(f"SELECT[{fetch}]-耗时: {end_time-start_time:.3f}s 获取到内容行数有: [ {all_num} ]", sql, "success")
        if all_num == 0:  # 如果这次结果是 0 那就是没有数据了
            if kwargs.get("_function_use") is True:
                raise IterNotNeedRun
            return

        with self.lock:
            if "_first" not in kwargs or kwargs.get("_first") is True:
                self.row_count['total'] = all_num
            else:
                if kwargs.get("_first") is False:
                    self.row_count['total'] += all_num

        for row in items:
            if count is False:
                yield row[0] if len(row) == 1 and isinstance(row, tuple) else row
            else:
                yield all_num, row[0] if len(row) == 1 and isinstance(row, tuple) else row
                all_num -= 1

        if all_num < kwargs.get("_limit_num", 0):   # 如果本次数据小于限制的数据 就终止继续迭代 当时获得了的数据还是要继续抛的
            raise IterNotNeedRun

    def select_iter(
        self, sql: str, pk: Union[str, int], limit: int = Buffer.max_cache, mode: Literal['Iter', 'Last'] = 'Iter'
    ) -> Iterator:
        """
        通过批量的迭代获取数据 有点问题 后面再优化: 目前只能支持一个表的操作，如果是多个表关联之类的 还有别名啥的 就不行了
        :param sql   : 只需要传入主要的逻辑 limit 部分用参数管理
        :param pk    : 主键，只需要告诉我主键的名字就好了
        :param limit : 这里交给我来自动管理 默认我给了 1000, Buffer的大小 方便buffer使用
        :param mode  :
                |_____模式: 默认 Iter: 迭代，从头到尾;
                >可能有bug,我还没测试出来 Last:每次都从最开始位置开始,记得调整过滤条件保证从最开始拿到的是正常的, 这个模式只能结合我的Buffer使用,不支持自己添加 ORDER BY 和 GROUP BY
        return: 如果传入count=True 那么第一个参数是行数,第二个参数是剩余行数w2  Q12
        """
        origin_sql = sql.rstrip('; ')  # 剔除右边的符号
        if "limit" in origin_sql.lower():
            origin_sql = re.sub(r' limit \d+, *\d+| limit +\d+', '', origin_sql, re.I)  # 剔除原先句子中的
        first = True
        if mode == "Last":
            if re.search("GROUP BY|ORDER BY", origin_sql, re.I):
                logger.error("这个模式需要结合Buffer使用,并且语句中不能包含 ORDER BY 和 GROUP BY 语句")
                return

            while True:
                if Buffer.size() > 0:
                    time.sleep(.5)
                    continue
                _sql = f"{origin_sql} ORDER BY {pk} asc LIMIT {limit};"
                try:
                    yield from self.select(_sql, _function_use=True, _limit_num=limit, _first=first)
                except IterNotNeedRun:
                    break
                first = False

        else:
            # 替换掉源sql里面的小写的关键词
            origin_sql = re.sub(" where ", " WHERE ", origin_sql, flags=re.I, count=1)
            origin_sql = re.sub(" from ", " FROM ", origin_sql, flags=re.I, count=1)

            cursor = 0
            while True:
                if "WHERE" in origin_sql:
                    _by_rule = re.search(r"(ORDER BY|GROUP BY)", origin_sql, re.I)
                    _sql = re.sub(
                        r" WHERE\s+(.+?)(?:ORDER BY|GROUP BY|$)",
                        rf" WHERE {pk} > (SELECT {pk} FROM {self.table_name} WHERE \1 ORDER BY {pk} LIMIT {cursor}, 1) AND \1{_by_rule.group(1) if _by_rule else ''}",
                        origin_sql
                    )
                else:
                    _sql = re.sub(
                        r" FROM\s+(\S+)",
                        rf" FROM \1 WHERE {pk} > (SELECT {pk} FROM {self.table_name} ORDER BY {pk} LIMIT {cursor}, 1)",
                        origin_sql
                    )

                new_sql = f"{_sql} LIMIT {limit};"
                try:
                    yield from self.select(new_sql, _function_use=True, _limit_num=limit, _first=first)
                except IterNotNeedRun:
                    break
                cursor += limit
                first = False

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

    def insert_batch(
            self,
            items: Union[Mapping[str, list], List[dict]],
            duplicate: Literal['ignore', 'update', None] = None,
            *,
            update_field: List[str] = None
    ) -> None:
        """
        批量插入, 一次传入一批列表 格式如下items
        # 下面就和pandas的dataframe格式一样的 所以也可以顺道插入mysql就很方便
        :param items :
                {"A_field": [1, 2, 3], "B_field": ["A", "B", "C"]} 长度得一致
                或者
                [{"A_field": 1, "B_field": "A"}, {"A_field": 2, "B_field": "B"}, {"A_field": 3, "B_field": "C"}] 每个字典里面的键名称得一致，字典的长度得一致，位置无所谓
        :param duplicate : 内容重复模式 ignore: 忽略重复内容,跳过; update:重复内容更新->需要指定更新的字段需要单独参数控制并且在items的key里面
        :param update_field: 重复了内容并且模式为update的时候使用,填入重复了需要更新的字段名称
        """
        self._check_table()
        sql, values = self.sql_base.insert_batch(items, duplicate, update_field=update_field)
        self.execute_many(sql, values, 'insert_batch', options=duplicate)

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

    def update_batch(self, items: Mapping[str, list], where: Mapping[str, list]):
        """
        批量更新操作
        :param items : {"A_field": [1, 2, 3], "B_field": ["A", "B", "C"]} 长度得一致
        :param where : {"C_field": [1, 2, 3]} 后面where数组的长度得和前面items的长度一致
        """
        self._check_table()
        sql, values = self.sql_base.update_batch(items, where)
        self.execute_many(sql, values, mode='update_batch')

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

    def _print_rate(self, mode: str, end_time, start_time, result, flag: str = "success"):
        all_line = self.change_line[mode] + self.not_change_line[mode]
        cost_time = time.time() - self.start_time
        if mode == 'update':
            cost_row = self.row_count['total'] - self.row_count['run']
            other_log = f"【Surplus/AllTask: {cost_row}/{self.row_count['total']} Time:{cost_time:.3f}s】 "
            rate = round(self.row_count['run'] / cost_time, 3)
            rate_str = f" TaskRate={rate} tasks/s;"    # 剩余的行效率
        elif mode == "insert":
            other_log = f"【Time:{cost_time:.3f}s】 "
            rate = round(all_line / cost_time, 3)  # 平均每秒改变行
            rate_str = f" LineRate={rate} line/s;"       # 插入的行效率
        else:
            other_log = " "
            rate_str = ""
        other_log += f"Affect={self.change_line[mode]}; NotAffect={self.not_change_line[mode]};{rate_str}"
        self.sql_log(
            f"[{mode}]{other_log} lineCost:{end_time - start_time:.3f}s AffectLine={result}", "", flag, True
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
