"""Opt-in MySQL/MariaDB integration tests against a disposable table.

Set LITE_TOOLS_MYSQL_TEST_CONFIG to a JSON connection configuration for a TEST
database (e.g. {"database":"lite_test","host":"127.0.0.1","user":"...",
"password":"..."}). The account needs CREATE/DROP/SELECT/INSERT/UPDATE/DELETE.
Never point this at a production database. No server is contacted by default.
"""
import json
import os
import unittest
import uuid

try:
    import pymysql
except ModuleNotFoundError:
    pymysql = None

from lite_tools.tools.sql.lib_mysql_string import SqlString


@unittest.skipUnless(pymysql is not None and os.environ.get("LITE_TOOLS_MYSQL_TEST_CONFIG"), "未配置 MySQL 测试库或缺少 PyMySQL")
class TestMySqlIntegration(unittest.TestCase):
    def test_generated_statements_under_both_escape_modes(self):
        config = json.loads(os.environ["LITE_TOOLS_MYSQL_TEST_CONFIG"])
        config.setdefault("charset", "utf8mb4")
        conn = pymysql.connect(**config)
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT @@SESSION.sql_mode")
                original_mode = cursor.fetchone()[0]
                modes = [mode for mode in original_mode.split(",") if mode != "NO_BACKSLASH_ESCAPES"]
                base_mode = ",".join(modes)
                for mode in (base_mode, ",".join(modes + ["NO_BACKSLASH_ESCAPES"])):
                    with self.subTest(mode=mode):
                        cursor.execute("SET SESSION sql_mode=%s", (mode,))
                        table = "lite_tools_test_" + uuid.uuid4().hex
                        builder = SqlString(table)
                        cursor.execute(builder.create_table({
                            "id": "BIGINT PRIMARY KEY",
                            "note": "VARCHAR(255)",
                            "status": "ENUM('a','b') DEFAULT 'a'",
                            "odd`field": "INT DEFAULT 0",
                        }))
                        try:
                            text = "O'Reilly\\a=True; None 中文\x00"
                            sql, rows = builder.insert([{"id": 1, "note": text}, {"note": "unlimited", "id": 2}])
                            cursor.executemany(sql, rows)
                            cursor.execute(builder.count({"note": text}))
                            self.assertEqual(cursor.fetchone()[0], 1)
                            cursor.execute(builder.exists({"note": "unlimited"}))
                            self.assertEqual(cursor.fetchone()[0], 1)
                            sql, rows = builder.update({"note": "new"}, {"id": 1})
                            cursor.executemany(sql, rows)
                            sql, rows = builder.insert({"id": 1, "note": text}, duplicate_except=["id"])
                            cursor.executemany(sql, rows)
                            cursor.execute(builder.count({"note": text}))
                            self.assertEqual(cursor.fetchone()[0], 1)
                            cursor.execute(builder.delete({"note": text}))
                            self.assertEqual(cursor.rowcount, 1)
                            cursor.execute(builder.count())
                            self.assertEqual(cursor.fetchone()[0], 1)
                            clause, params = builder._where_parameters({"note": "unlimited"})
                            cursor.execute("SELECT COUNT(*) FROM {} WHERE {}".format(builder._table(), clause), params)
                            self.assertEqual(cursor.fetchone()[0], 1)
                        finally:
                            cursor.execute("DROP TABLE {}".format(builder._table()))
        finally:
            conn.close()
