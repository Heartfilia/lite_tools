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
import asyncio
from typing import Iterator, Union, Mapping, List
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import pymysql
import aiomysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB

from lite_tools.logs.sql import x as sql_log
from lite_tools.tools.core.lite_string import pretty_indent
from lite_tools.tools.sql.lib_mysql_string import SqlString
from lite_tools.tools.sql.config import MySqlConfig, CountConfig
from lite_tools.exceptions.SqlExceptions import IterNotNeedRun, NeedPoolOrConfig


class MySql:
    def __init__(
            self,
            pool: PooledDB = None,
            *,
            config: Union[MySqlConfig, dict] = None,
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
                        max_connections: int = 20,
                        table_name: str = None,
            | 或者 --> {"database": "", "host": "", "user": "", "password": "" .....} 上面的参数这里面都能放
        table_name: 如果是自己传入pool 那么就需要传入这个参数
        log_rule  : 打印日志的模式，默认是每隔一段时间或者一定的量打印一下，可以设置为each 每条打印
        """
        self.cur = "tuple"
        if pool:
            self.log = True   # 默认肯定是要打印日志的啦
            self.pool = pool
            self.table_name = table_name
        elif not pool and config and isinstance(config, (MySqlConfig, dict)):
            self.pool = None
            if isinstance(config, dict):
                config = MySqlConfig.new(config)
            self.config = config
            self.table_name = table_name or self.config.table_name
            self.cur = self.config.cursor   # 记录这个 因为流式处理地方不太一样
            self._init_mysql()
            self.log = self.config.log
        else:
            raise ValueError

        self.sql_base = SqlString(self.table_name)
        self.count_conf = CountConfig()
        self.reg = re.compile(r"FROM\s+?`?(\S+)`?", re.I | re.S)  # 部分处理 还需要二次处理的
        self.start_time = time.time()
        self.log_rule = log_rule

    def _init_mysql(self):
        database = self.config.database
        max_connections = self.config.max_connections
        host = self.config.host
        port = self.config.port
        user = self.config.user
        password = self.config.password
        charset = self.config.charset
        cursor = self.config.cursor

        if self.pool is None:
            if cursor == "dict":
                cursor_type = pymysql.cursors.DictCursor
            elif cursor == "stream":
                cursor_type = pymysql.cursors.SSCursor  # 流式 建议单条处理
            elif cursor == "dict_stream":
                cursor_type = pymysql.cursors.SSDictCursor
            else:
                cursor_type = pymysql.cursors.Cursor
            self.pool = PooledDB(
                creator=pymysql,  # 使用链接数据库的模块
                maxconnections=max_connections,  # 连接池允许的最大连接数，0和None表示不限制连接数
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
                cursorclass=cursor_type,   # 调整返回结果的样式
            )

    def close_pool(self) -> bool:
        try:
            if self.pool:
                self.pool.close()
                self.pool = None
                return True
        except Exception as err:
            sql_log(f"关闭链接池失败:{err}", "error")
        return False

    def execute(
            self,
            sql: str,
            args: Union[list, tuple] = None,
            fetch: Literal["one", "all", "many", ""] = "",
            log: bool = False,
            table_name: str = None,
            **kwargs
    ) -> Union[int, tuple, dict]:
        """
        流式读取的话 不用这里操作
        sql -> 这里为可以直接执行的sql语句或者sql模板，推荐使用模板
        args -> 如果是单行 直接传入 list/tuple 对应模板
                如果是多行 [[], [], []] 里面的每一小条
        fetch-many 的时候需要配置  buffer=xxx 默认1000
        """
        assert sql, f"传入了空sql语句--> sql:[ {sql} ]"
        assert self._secure_check(sql), '删除操作终止!!!'
        mode = sql.upper()[0]   # 取第一个字母
        _start_time = time.perf_counter()
        conn = self.connection()
        try:
            with conn.cursor() as cursor:    # 这里是返回影响的行数
                if args:    # 批量操作的时候
                    if not isinstance(args[0], (list, tuple)):   # 判断内容里面 里面是否是列表或者元组，如果是的话那么就是批量的
                        cursor.execute(sql, args)    # 这里是单行操作套用模板的情况
                    else:
                        cursor.executemany(sql, args)   # 批量操作套用模板
                else:
                    cursor.execute(sql)

                _end_time = time.perf_counter()

                if not fetch and not sql.upper().startswith("SELECT"):
                    conn.commit()
                    if log or self.log:
                        effect_count = cursor.rowcount
                        if "ON DUPLICATE KEY UPDATE" in sql:
                            effect_count //= 2    # 这里是有问题的  所以这里只是看个大概
                        self.count_conf.add_time(table_name, mode, _end_time-_start_time)
                        _all_row = self.count_conf.add_line(table_name, mode, effect_count)
                        _rate = self.count_conf.get_rate(table_name, mode)
                        sql_log(
                            f"{mode}[{table_name} <{_all_row}:{time.time()-self.start_time:.2f}s>] "
                            f"this_ts={_end_time-_start_time:.3f}s avg_rate={_rate} -> {effect_count}",
                            "success"
                        )
                    return effect_count   # 如果是插入 更新操作的话 需要获得 影响的行数
                elif fetch == "one":
                    return cursor.fetchone()
                elif fetch == "many":
                    return cursor.fetchmany(kwargs.get('buffer', 1000))
                else:
                    return cursor.fetchall()
        except Exception as err:
            sql_log(f"[{err.__traceback__.tb_lineno}]"
                    f"\n-----------------< sql start >--------------------\n"
                    f"{pretty_indent(sql)}"
                    f"\n------------------< sql end >---------------------\n"
                    f">>> {err} ", "error")
            if not fetch:
                conn.rollback()
                return 0
        finally:
            conn.close()

    def _get_select_table_name(self, sql: str, **kwargs) -> str:
        if kwargs.get("table_name"):  # 第一步直接尝试提取 传入的参数是否有table
            return kwargs.get('table_name')

        items = self.reg.findall(sql)
        if not items:  # 第二步 通过正则提取
            return self.table_name or "default"   # 没有提取到并且 没有设置将默认一个参数值
        maybe_table = items[-1].split(".")[-1]    # 将可能是table的提取出来 然后切割一些
        return maybe_table.strip("`")   # 把特殊标志移除

    def select(self, sql: str, count: bool = False, *, query_log: bool = True,
               fetch: Literal['all', 'many', 'one'] = 'all', **kwargs) -> Iterator:
        """
        推荐查询量大的时候用 select_iter
        一次性查询全部数据
        :param sql: 传入的查询sql语句
        :param count: 是否需要统计剩余的行数 如果传入count=True 那么第一个参数是行数,第二个参数是剩余行数
        :param query_log: 是否把query的查询日志打印出来,默认就是打印出来
        :param fetch: 获取数据模式 默认 fetchall 设置 one 就是 fetchone 设置many的时候 需要设置 buffer >>> 直接buffer=数字 否则默认1000
                    ------> 设置 many 的时候有点类似批量读取 每次读取 buffer 的量 这里 count 无效 将不再打印日志
        :return:
        """
        if self.cur == "stream" or self.cur == "dict_stream":
            yield from self.select_iter(sql, log=query_log, **kwargs)
        start_time = time.time()
        conn = self.connection()
        table_name = self._get_select_table_name(sql, **kwargs)
        with conn.cursor() as cursor:  # 这里是有结果返回的
            cursor.execute(sql)
        if fetch == 'one':
            item = cursor.fetchone()
            items = [item]
        elif fetch == "many":
            if not isinstance(kwargs.get('buffer', 1000), int):
                sql_log("需要设置的 buffer 为数字....", "error")
                return
            items = cursor.fetchmany(kwargs.get("buffer", 1000))
            for item in items:
                yield item[0] if len(item) == 1 and isinstance(item, tuple) else item
            while items:
                items = cursor.fetchmany(kwargs.get("buffer", 1000))
                for item in items:
                    yield item[0] if len(item) == 1 and isinstance(item, tuple) else item
            return
        else:
            items = cursor.fetchall()
        conn.close()
        end_time = time.time()
        all_num = len(items)
        if query_log is True:
            sql_log(
                f"[{table_name} <{all_num}:{end_time-start_time:.3f}s>] - SELECT[{fetch}] SQL-> {sql}",
                "success",
            )
        if all_num == 0:  # 如果这次结果是 0 那就是没有数据了
            if kwargs.get("_function_use") is True:
                raise IterNotNeedRun
            return

        for item in items:
            if count is False:
                yield item[0] if len(item) == 1 and isinstance(item, tuple) else item
            else:
                yield all_num, item[0] if len(item) == 1 and isinstance(item, tuple) else item
                all_num -= 1

        if all_num < kwargs.get("_limit_num", 0):   # 如果本次数据小于限制的数据 就终止继续迭代 当时获得了的数据还是要继续抛的
            raise IterNotNeedRun

    def select_iter(self, sql: str, args: Union[list, tuple] = None, log: bool = False, **kwargs):
        """
        这里属于流式的读取位置 这里只能fetchone
        max_num  一般用于测试 就是获取的数据量到了这个值后 就停止继续遍历
        """
        assert sql, f"传入了空sql语句--> sql:[ {sql} ]"
        conn = self.connection()
        if self.cur not in ["stream", "dict_stream"]:
            cur = pymysql.cursors.SSCursor
        else:
            cur = pymysql.cursors.Cursor
        table_name = self.table_name or self._get_select_table_name(sql)
        _start_time = time.perf_counter()
        try:
            with conn.cursor(cur) as cursor:
                if args:    # 批量操作的时候
                    if not isinstance(args[0], (list, tuple)):   # 判断内容里面 里面是否是列表或者元组，如果是的话那么就是批量的
                        cursor.execute(sql, args)    # 这里是单行操作套用模板的情况
                    else:
                        cursor.executemany(sql, args)   # 批量操作套用模板
                else:
                    cursor.execute(sql)

                result = cursor.fetchone()
                while result is not None:
                    _duration_time = time.perf_counter() - _start_time
                    ok = self.count_conf.add_line(table_name, "S", 1)
                    yield result if len(result) > 1 else result[0]
                    if (log or self.log) and (ok % 500 == 0):
                        sql_log(
                            f"S[{table_name} <{_duration_time:.2f}s>] 程序运行 lines={ok} "
                            f"avg_rate={ok/_duration_time:.3f} line/s")
                    if ok >= kwargs.get("max_num", -1):
                        break
                    result = cursor.fetchone()
        except Exception as err:
            sql_log(f"[{err.__traceback__.tb_lineno}]{sql} : {err} ", "error")
        finally:
            conn.close()
            if log or self.log:
                all_line = self.count_conf.get_line(table_name, "S")
                _duration_time = time.perf_counter() - _start_time
                sql_log(
                    f"S[{table_name} <{_duration_time:.2f}s>] 运行结束 lines={all_line} "
                    f"avg_rate={all_line / _duration_time:.3f} line/s", "info")

    def exists(self, where: Union[dict, str], table_name: str = None) -> bool:
        """
        判断条件在不在该表中有数据
        :param where: 通过字典的方式传入条件(推荐) 或者字符串的条件
        :param table_name: 如果传入优先取这里的table名称 否则取全局的
        """
        table = self._check_table(table_name)
        sql = self.sql_base.exists(where, table_name=table)
        for num in self.select(sql, query_log=False):
            if num == 0:
                return False
            else:
                return True
        return False

    def count(self, where: Union[dict, str] = None, table_name: str = None) -> int:
        """
        只能提取全库量 可以加筛选条件 但是 不适合 groupBy 之类的统计
        """
        table = self._check_table(table_name)
        sql = self.sql_base.count(where, table_name=table)
        for num in self.select(sql, query_log=False):
            return num

    def insert(
            self,
            item: Union[Mapping[str, any], List[Mapping[str, any]]],
            table_name: str = "",
            duplicate_except: list = None,
            ignore: bool = False,
            log: bool = False,
    ) -> None:
        """
        创建数据模板 和对应的数据结果
        :param item  : -> dict模式 直接处理为单条 {"a": 1, "b": False} -> a=1,b=0
                       -> list模式 传入的是多组[{"a": 1, "b": False}, {"a": 1, "b": False}]
        :param table_name      : 表名,这里优先级高于全局
        :param duplicate_except: 这里是排除法一般这里建议把你不需要替换的字段名称写上去 None的话就不 insert... on duplicate
        :param ignore          : 一般这里是忽略表里已经存在的时候 这里优先级高于上面 这个和上面都写了的话 是直接忽略重复异常
        :param log             : 打印日志
        """
        table = self._check_table(table_name)
        _sql, values = self.sql_base.insert(item, table, duplicate_except, ignore)
        self.execute(_sql, values, log=log, table_name=table)

    def update(
            self,
            item: Union[List[Mapping[str, any]], Mapping[str, any]],
            where: Union[str, List[str], Mapping[str, any], List[Mapping[str, any]]],
            table_name: str = "",
            log: bool = False
    ) -> None:
        """
        更新数据
        :param item: 更新的结果 字典表示
        :param where: 需要更新数据的时候使用的条件
        :param table_name: 表名 这里和全局二选一 优先级这里最高
        :param log       : 打印日志
        """
        table = self._check_table(table_name)
        _sql, values = self.sql_base.update(item, where, table_name=table)
        self.execute(_sql, values, log=log, table_name=table)

    def delete(self, where: Union[dict, str], table_name: str = None) -> None:
        """
        删除数据操作
        :param where: 需要删除数据的时候使用的条件
        :param table_name: 表名 这里和全局二选一 优先级这里最高
        """
        table = self._check_table(table_name)
        sql = self.sql_base.delete(where, table_name=table)
        self.execute(sql, mode="delete", table_name=table)

    def connection(self):
        """获取链接对象"""
        conn = self.pool.connection()
        return conn

    def _check_table(self, table_name: str = None):
        """判断 table_name 是否有 全局和局部 必须有一个"""
        if not table_name and not self.table_name:
            raise ValueError(
                "你现在执行的操作是需要传入 table 的名字 "
                "mysql = MySql(table_name='xxx') "
                "或者在对应操作 "
                "xxx(其它参数, table_name='xx')"
            )
        return table_name or self.table_name

    @staticmethod
    def _secure_check(string: str) -> bool:
        """
        安全检查-->程序里面不给你操作drop操作的
        """
        if string.upper().startswith("DROP"):
            sql_log(f"SQL: {string}  确定要删除操作吗? Y/N", "warning")
            flag = input(">>> ")
            if flag.upper() == "Y":
                sql_log(
                    f"哈哈哈 这里是唬你的 程序里面不给你--DROP--操作的 我肯定直接报错啦 ( •̀ ω •́ )y",
                    "success")
                return False
        return True


class AioMySql:
    """
    这个支持的功能不多
    """
    def __init__(self, pool: aiomysql.pool = None, config: Union[MySqlConfig, dict] = None):
        if pool:
            self._pool = pool
        else:
            self._pool = None

        self._config = config

    async def __init(self):
        if not self._pool and (not self._config or not isinstance(self._config, (MySqlConfig, dict))):
            raise NeedPoolOrConfig

        if isinstance(self._config, dict):
            self._config = MySqlConfig.new(self._config)

        cursor = self._config.cursor

        if cursor == "dict":
            cursor_type = aiomysql.DictCursor
        elif cursor == "stream":
            cursor_type = aiomysql.SSCursor  # 流式 建议单条处理
        elif cursor == "dict_stream":
            cursor_type = aiomysql.SSDictCursor
        else:
            cursor_type = aiomysql.Cursor

        self._pool = await aiomysql.create_pool(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            db=self._config.database,
            minsize=1,
            maxsize=self._config.max_connections,
            cursorclass=cursor_type,

            unix_socket=self._config.unix_socket,
            charset=self._config.charset,
            sql_mode=self._config.sql_mode,
            read_default_file=self._config.read_default_file,
            conv=self._config.conv,
            use_unicode=self._config.use_unicode,
            client_flag=self._config.client_flag,
            init_command=self._config.init_command,
            connect_timeout=self._config.connect_timeout,
            read_default_group=self._config.read_default_group,
            autocommit=self._config.autocommit,
            echo=self._config.echo,
            local_infile=self._config.local_infile,
            loop=self._config.loop,
            ssl=self._config.ssl,
            auth_plugin=self._config.auth_plugin,
            program_name=self._config.program_name,
            server_public_key=self._config.server_public_key,
        )

    async def close_pool(self) -> bool:
        """
        这个地方在你用的地方最后位置调用 不要在服务里面用 如：在fastapi里面用 可以用lifespan
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def lifespan(app_tasker: FastAPI):
            # 启动时操作
            yield   # 不能丢
            # 关闭后操作
            if await async_mysql.close_pool():
                logger.warning("已经关闭mysql链接池")

        app = FastAPI(
            ...,
            lifespan=lifespan      # 其它参数忽略   这里加上就可以
        )
        """
        try:
            if self._pool:
                self._pool.close()
                await asyncio.sleep(1)
                await self._pool.wait_closed()
                self._pool = None
                return True
        except Exception as err:
            sql_log(f"关闭链接池异常:{err}", "warning")
        return False

    async def execute(
            self, sql: str, args: Union[list, tuple] = None, fetch: Literal['one', 'all', 'many', ''] = '',
            _log: bool = False, **kwargs
    ):
        if not self._pool:
            await self.__init()
        if _log:
            sql_log(f"{sql=}  {args=}", "debug")

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:   # 默认返回dict
                    if args:    # 批量操作的时候
                        if not isinstance(args[0], (list, tuple)):   # 判断内容里面 里面是否是列表或者元组，如果是的话那么就是批量的
                            cur = await cursor.execute(sql, args)    # 这里是单行操作套用模板的情况
                        else:
                            cur = await cursor.executemany(sql, args)   # 批量操作套用模板
                    else:
                        cur = await cursor.execute(sql)
                    if not fetch and not sql.upper().startswith("SELECT"):
                        await conn.commit()
                        return cur   # 如果是插入 更新操作的话 需要获得 影响的行数
                    elif fetch == "one":
                        return await cursor.fetchone()
                    elif fetch == "many":
                        return cursor.fetchmany(kwargs.get('buffer', 1000))
                    else:
                        return await cursor.fetchall()
        except Exception as err:
            sql_log(f"[{err.__traceback__.tb_lineno}]"
                    f"\n-----------------< sql start >--------------------\n"
                    f"{pretty_indent(sql)}"
                    f"\n------------------< sql end >---------------------\n"
                    f">>> {err} ", "error")
            if not fetch:
                await conn.rollback()
                return 0

