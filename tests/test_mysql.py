import asyncio
import inspect
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

try:
    import pymysql
    from lite_tools.tools.sql.config import MySqlConfig
    from lite_tools.tools.sql.lib_mysql_string import SqlString
    from lite_tools.tools.sql.lite_mysql import AioMySql, MySql
except ModuleNotFoundError as err:
    if err.name not in ("pymysql", "aiomysql", "dbutils", "dbutils.pooled_db"):
        raise
    MYSQL_AVAILABLE = False
else:
    MYSQL_AVAILABLE = True


@unittest.skipUnless(MYSQL_AVAILABLE, "需要安装 MySQL 可选依赖 lite-tools[net]")
class TestMySql(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cursor = self.conn.cursor.return_value.__enter__.return_value
        self.cursor.description = None
        self.cursor.rowcount = 3
        self.pool = MagicMock()
        self.pool.connection.return_value = self.conn
        self.db = MySql(pool=self.pool, table_name="users")
        self.db.log = False
        self.log_patch = patch("lite_tools.tools.sql.lite_mysql._sql_log")
        self.log_patch.start()
        self.addCleanup(self.log_patch.stop)

    def test_write_with_logging_disabled(self):
        self.assertEqual(self.db.execute("UPDATE users SET v=%s WHERE id=1", [2]), 3)
        self.conn.commit.assert_called_once()
        self.conn.rollback.assert_not_called()
        self.conn.close.assert_called_once()

    def test_upsert_rowcount_not_halved(self):
        self.db.log = True
        self.assertEqual(self.db.insert({"id": 1, "v": 2}, duplicate_except=[]), 3)

    def test_logging_failure_does_not_change_committed_result(self):
        self.db.log = True
        with patch("lite_tools.tools.sql.lite_mysql._sql_log", side_effect=RuntimeError("log failure")):
            self.assertEqual(self.db.update({"v": 2}, {"id": 1}), 3)
        self.conn.rollback.assert_not_called()

    def test_exception_propagates_and_connection_closes(self):
        failure = pymysql.OperationalError(2006, "server gone")
        self.cursor.execute.side_effect = failure
        self.conn.rollback.side_effect = RuntimeError("rollback failed")
        with self.assertRaises(pymysql.OperationalError) as caught:
            self.db.execute("UPDATE users SET v=1 WHERE id=1")
        self.assertIs(caught.exception, failure)
        self.conn.rollback.assert_called_once()
        self.conn.close.assert_called_once()
        self.conn.commit.assert_not_called()

    def test_result_description_not_statement_prefix_controls_fetch(self):
        self.cursor.description = (("n",),)
        self.cursor.fetchall.return_value = ((1,),)
        self.assertEqual(self.db.execute("WITH x AS (SELECT 1 AS n) SELECT n FROM x"), ((1,),))
        self.conn.commit.assert_not_called()

    def test_empty_args_do_not_execute_raw_sql(self):
        self.assertEqual(self.db.execute("DELETE FROM users", []), 0)
        self.pool.connection.assert_not_called()

    def test_parameter_mapping_supported(self):
        self.db.execute("UPDATE users SET v=%(v)s WHERE id=1", {"v": 3})
        self.cursor.execute.assert_called_once_with("UPDATE users SET v=%(v)s WHERE id=1", {"v": 3})

    def test_crud_passes_parameters_and_returns_count(self):
        self.assertEqual(self.db.insert({"name": "O'Reilly"}), 3)
        self.cursor.executemany.assert_called_with("INSERT INTO `users` (`name`) VALUES (%s);", [["O'Reilly"]])
        self.assertEqual(self.db.update({"name": "A"}, {"id": None}), 3)
        self.cursor.executemany.assert_called_with("UPDATE `users` SET `name` = %s WHERE `id` <=> %s;", [["A", None]])
        self.assertEqual(self.db.delete({"name": "x' OR 1=1 --"}), 3)
        self.cursor.execute.assert_called_with("DELETE FROM `users` WHERE `name` <=> %s;", ["x' OR 1=1 --"])

    def test_count_and_exists_with_dict_cursor(self):
        self.cursor.description = (("n",),)
        self.cursor.fetchone.return_value = {"COUNT(*)": 0}
        self.assertEqual(self.db.count({"name": "a"}), 0)
        self.cursor.execute.assert_called_with("SELECT COUNT(*) FROM `users` WHERE `name` <=> %s;", ["a"])
        self.cursor.fetchone.return_value = None
        self.assertFalse(self.db.exists({"id": 99}))
        self.cursor.fetchone.return_value = {"1": 1}
        self.assertTrue(self.db.exists({"id": 1}))

    def test_empty_read_conditions_and_raw_percent_conditions(self):
        self.cursor.description = (("n",),)
        self.cursor.fetchone.return_value = (2,)
        self.assertEqual(self.db.count({}), 2)
        self.cursor.execute.assert_called_with("SELECT COUNT(*) FROM `users`;")
        self.db.count("name LIKE 'a%'")
        self.cursor.execute.assert_called_with("SELECT COUNT(*) FROM `users` WHERE name LIKE 'a%';")

    def test_percent_names_interpolate_correctly(self):
        self.db.delete({"v%": 1}, table_name="t%")
        sql, params = self.cursor.execute.call_args.args
        self.assertEqual(sql % tuple(params), "DELETE FROM `t%` WHERE `v%` <=> 1;")

    def test_select_binds_args_and_preserves_single_column_flattening(self):
        self.cursor.fetchall.return_value = ((1,), (2,))
        self.assertEqual(list(self.db.select("SELECT id FROM users WHERE v=%s", args=[3], query_log=False)), [1, 2])
        self.cursor.execute.assert_called_with("SELECT id FROM users WHERE v=%s", [3])
        self.conn.close.assert_called_once()

    def test_select_many_and_count(self):
        self.cursor.fetchmany.side_effect = [((1,), (2,)), ((3,),), ()]
        self.assertEqual(list(self.db.select("SELECT id FROM users", fetch="many", buffer=2)), [1, 2, 3])
        self.cursor.fetchall.return_value = ((1,), (2,))
        self.assertEqual(list(self.db.select("SELECT id FROM users", count=True, query_log=False, _limit_num=2)), [(2, 1), (1, 2)])

    def test_stream_uses_unbuffered_cursor_and_propagates_errors(self):
        self.cursor.fetchone.side_effect = [(1,), RuntimeError("stream failed")]
        iterator = self.db.select_iter("SELECT id FROM users")
        self.assertEqual(next(iterator), 1)
        with self.assertRaisesRegex(RuntimeError, "stream failed"):
            next(iterator)
        self.conn.cursor.assert_called_with(pymysql.cursors.SSCursor)
        self.conn.close.assert_called_once()

    def test_closing_stream_releases_connection(self):
        self.cursor.fetchone.side_effect = [(1,), (2,), None]
        iterator = self.db.select_iter("SELECT id FROM users")
        next(iterator)
        iterator.close()
        self.conn.close.assert_called_once()

    def test_stream_zero_limit_no_connection(self):
        self.assertEqual(list(self.db.select_iter("SELECT id FROM users", max_num=0)), [])
        self.pool.connection.assert_not_called()

    def test_invalid_fetch_and_buffer_before_connecting(self):
        for kwargs in ({"fetch": "bad"}, {"fetch": "many", "buffer": 0}, {"fetch": "many", "buffer": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.db.execute("SELECT 1", **kwargs)
        self.pool.connection.assert_not_called()

    def test_drop_guard_no_interactive_prompt(self):
        for sql in ("DROP TABLE users", "  drop table users", "/* comment */ DROP TABLE users", "-- comment\nDROP TABLE users"):
            with self.subTest(sql=sql), self.assertRaises(PermissionError):
                self.db.execute(sql)
        self.pool.connection.assert_not_called()

    def test_sync_config_forwards_ssl_timeout_and_converters(self):
        config = MySqlConfig(database="db", host="localhost", user="u", password="", ssl={"ca": "ca.pem"}, connect_timeout=7)
        with patch("lite_tools.tools.sql.lite_mysql.PooledDB") as pool:
            MySql(config=config)
        forwarded = pool.call_args.kwargs
        self.assertEqual(forwarded["ssl"], {"ca": "ca.pem"})
        self.assertEqual(forwarded["connect_timeout"], 7)
        self.assertIs(forwarded["use_unicode"], True)
        # Bind against the real installed driver signature, without connecting.
        driver_kwargs = {key: value for key, value in forwarded.items()
                         if key in inspect.signature(pymysql.Connection).parameters}
        # SSL forwarding was asserted above; this offline constructor has no
        # CA file and must not try to load the illustrative path.
        driver_kwargs.pop("ssl")
        connection = pymysql.Connection(defer_connect=True, **driver_kwargs)
        connection.server_status = 0
        self.assertEqual(connection.escape("O'Reilly"), "'O\\'Reilly'")

    def test_empty_password_in_dict_config(self):
        config = MySqlConfig.new({"db": "db", "host": "localhost", "user": "u", "password": ""})
        self.assertEqual(config.password, "")

    def test_config_export_preserves_later_edits(self):
        source = {"database": "db", "host": "localhost", "user": "u", "password": "p", "port": 3306}
        config = MySqlConfig.new(source)
        source["port"] = 9999
        config.port = 3307
        self.assertEqual(config.to_dict()["port"], 3307)

    def test_real_driver_mogrify_for_generated_statements(self):
        conn = pymysql.Connection(defer_connect=True, charset="utf8mb4")
        conn.server_status = 0
        cursor = conn.cursor()
        sql, rows = SqlString("t%").insert({"v%": "a'\\b", "n": None}, duplicate_except=[])
        rendered = cursor.mogrify(sql, rows[0])
        self.assertIn("`t%`", rendered)
        self.assertIn("NULL", rendered)
        self.assertNotIn("%s", rendered)
        sql, rows = SqlString("t%").update({"v%": "a"}, "note LIKE 'a%' AND n % 2=0")
        rendered = cursor.mogrify(sql, rows[0])
        self.assertIn("LIKE 'a%' AND n % 2=0", rendered)


@unittest.skipUnless(MYSQL_AVAILABLE, "需要安装 MySQL 可选依赖 lite-tools[net]")
class TestAioMySql(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.events = []
        self.cursor = MagicMock()
        self.cursor.description = None
        self.cursor.execute = AsyncMock(return_value=3)
        self.cursor.executemany = AsyncMock(return_value=3)
        self.cursor.fetchone = AsyncMock(return_value=(1,))
        self.cursor.fetchall = AsyncMock(return_value=((1,),))
        cursor_context = MagicMock()
        cursor_context.__aenter__ = AsyncMock(return_value=self.cursor)
        cursor_context.__aexit__ = AsyncMock(return_value=False)
        self.conn = MagicMock()
        self.conn.cursor.return_value = cursor_context
        self.conn.commit = AsyncMock()
        self.conn.rollback = AsyncMock(side_effect=lambda: self.events.append("rollback"))
        acquire = MagicMock()
        acquire.__aenter__ = AsyncMock(return_value=self.conn)
        acquire.__aexit__ = AsyncMock(side_effect=lambda *args: self.events.append("release"))
        self.pool = MagicMock()
        self.pool.acquire.return_value = acquire
        self.pool.wait_closed = AsyncMock()
        self.db = AioMySql(pool=self.pool)

    async def test_write_and_batch(self):
        self.assertEqual(await self.db.execute("UPDATE users SET v=%s WHERE id=1", [2]), 3)
        self.conn.commit.assert_awaited_once()
        self.assertEqual(await self.db.execute("INSERT INTO users (id) VALUES (%s)", [[1], [2]]), 3)
        self.cursor.executemany.assert_awaited_once()

    async def test_rollback_before_release_and_preserve_error(self):
        self.cursor.execute.side_effect = ValueError("database failed")
        with self.assertRaisesRegex(ValueError, "database failed"):
            await self.db.execute("UPDATE users SET v=1 WHERE id=1")
        self.assertEqual(self.events, ["rollback", "release"])

    async def test_cancellation_rolls_back(self):
        self.cursor.execute.side_effect = asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await self.db.execute("UPDATE users SET v=1 WHERE id=1")
        self.assertEqual(self.events, ["rollback", "release"])

    async def test_concurrent_initialization_creates_one_pool(self):
        db = AioMySql(config={"db": "db", "host": "localhost", "user": "u", "password": "p"})
        async def create_pool(**kwargs):
            await asyncio.sleep(0)
            return self.pool
        with patch("lite_tools.tools.sql.lite_mysql.aiomysql.create_pool", side_effect=create_pool) as create:
            await asyncio.gather(*(db.execute("UPDATE users SET v=1 WHERE id=1") for _ in range(5)))
        self.assertEqual(create.call_count, 1)

    async def test_result_set_description_controls_fetch(self):
        self.cursor.description = (("n",),)
        self.assertEqual(await self.db.execute("SHOW TABLES"), ((1,),))
        self.conn.commit.assert_not_awaited()

    async def test_empty_args_and_invalid_fetch_do_not_acquire(self):
        self.assertEqual(await self.db.execute("DELETE FROM users", []), 0)
        with self.assertRaises(ValueError):
            await self.db.execute("SELECT 1", fetch="bad")
        self.pool.acquire.assert_not_called()

    async def test_close_pool(self):
        self.assertTrue(await self.db.close_pool())
        self.pool.close.assert_called_once()
        self.pool.wait_closed.assert_awaited_once()
        self.assertIsNone(self.db._pool)


if __name__ == "__main__":
    unittest.main()
