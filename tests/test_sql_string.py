import unittest
from collections import UserDict
from datetime import datetime, timedelta
from decimal import Decimal

from lite_tools.tools.sql.lib_mysql_string import SqlString


class TestSqlString(unittest.TestCase):
    def setUp(self):
        self.sql = SqlString("users")

    def test_insert_keeps_return_shape_and_parameterizes_values(self):
        payload = "x' OR 1=1 -- a=True"
        sql, rows = self.sql.insert({"name": payload, "active": True, "note": None})
        self.assertEqual(sql, "INSERT INTO `users` (`name`, `active`, `note`) VALUES (%s, %s, %s);")
        self.assertEqual(rows, [[payload, 1, None]])

    def test_mapping_and_reordered_batch(self):
        sql, rows = self.sql.insert([UserDict(a=1, b=2), UserDict(b=4, a=3)])
        self.assertEqual(rows, [[1, 2], [3, 4]])

    def test_invalid_rows_rejected(self):
        for item in ([], {}, [{}], [{}, {"a": 1}], [{"a": 1}, {"a": 2, "b": 3}],
                     [{"a": 1}, {"b": 2}], ["a"], "a", {"a": [1]}, {"a": object()}):
            with self.subTest(item=item), self.assertRaises((ValueError, TypeError)):
                self.sql.insert(item)

    def test_nonfinite_values_rejected(self):
        for value in (float("nan"), float("inf"), Decimal("NaN"), Decimal("Infinity")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.sql.insert({"v": value})
            with self.assertRaises(ValueError):
                self.sql.count({"v": value})

    def test_identifiers_escaped(self):
        sql, rows = self.sql.update({"name": "x"}, {"id` <=> 1 OR 1=1 -- ": 2})
        self.assertIn("`id`` <=> 1 OR 1=1 -- ` <=> %s", sql)
        self.assertEqual(rows, [["x", 2]])
        self.assertEqual(SqlString._quote_identifier("`db`.`a.b`"), "`db`.`a.b`")
        self.assertEqual(SqlString._quote_identifier("`a``b`"), "`a``b`")

    def test_invalid_identifiers_rejected(self):
        for name in (None, 0, False, "", "a..b", "a.", "*", "`abc", "`a` extra", "a\x00b"):
            with self.subTest(name=name), self.assertRaises((ValueError, TypeError)):
                SqlString(name).insert({"id": 1})

    def test_upsert_and_ignore(self):
        self.assertNotIn("DUPLICATE", self.sql.insert({"id": 1})[0])
        self.assertIn("`id`=VALUES(`id`)", self.sql.insert({"id": 1}, duplicate_except=[])[0])
        self.assertNotIn("`id`=VALUES", self.sql.insert({"id": 1, "v": 2}, duplicate_except=["id"])[0])
        self.assertIn("INSERT IGNORE", self.sql.insert({"id": 1}, duplicate_except=["id"], ignore=True)[0])
        for excluded in (["id"], ["typo"], "id", [1]):
            with self.subTest(excluded=excluded), self.assertRaises((ValueError, TypeError)):
                self.sql.insert({"id": 1}, duplicate_except=excluded)

    def test_empty_write_conditions_rejected(self):
        for where in (None, {}, [], "", " ", ";", False, 0):
            with self.subTest(where=where):
                with self.assertRaises((ValueError, TypeError)):
                    self.sql.delete(where)
                with self.assertRaises((ValueError, TypeError)):
                    self.sql.update({"v": 1}, where)
        self.assertEqual(self.sql.delete("1=1"), "DELETE FROM `users` WHERE 1=1;")

    def test_update_null_and_bool(self):
        sql, rows = self.sql.update({"v": False}, {"id": None})
        self.assertEqual(sql, "UPDATE `users` SET `v` = %s WHERE `id` <=> %s;")
        self.assertEqual(rows, [[0, None]])

    def test_update_batch_alignment(self):
        sql, rows = self.sql.update([{"a": 1, "b": 2}, {"b": 4, "a": 3}],
                                    [{"id": 5, "v": 6}, {"v": 8, "id": 7}])
        self.assertEqual(rows, [[1, 2, 5, 6], [3, 4, 7, 8]])
        for where in ([{}, {}], [{"id": 1}], [{"id": 1}, {"id": 2}, {"id": 3}],
                      ["id=1", "id=2"], [{"id": 1}, {"v": 2}]):
            with self.subTest(where=where), self.assertRaises((ValueError, TypeError)):
                self.sql.update([{"a": 1}, {"a": 2}], where)

    def test_condition_list_preserves_precedence(self):
        sql, rows = self.sql.update({"v": 1}, ["role=1 OR role=2", "tenant_id=7"])
        self.assertIn("WHERE (role=1 OR role=2) AND (tenant_id=7)", sql)

    def test_percent_interpolation_in_identifiers_and_raw_conditions(self):
        sql, rows = SqlString("t%name").update({"v%": 1}, "name LIKE 'a%' AND n % 2=0")
        rendered = sql % tuple(rows[0])
        self.assertIn("`t%name`", rendered)
        self.assertIn("LIKE 'a%' AND n % 2=0", rendered)
        sql, rows = SqlString("t%").insert({"v%": 1}, duplicate_except=[])
        self.assertEqual(sql % tuple(rows[0]), "INSERT INTO `t%` (`v%`) VALUES (1) ON DUPLICATE KEY UPDATE `v%`=VALUES(`v%`);")

    def test_direct_values_preserve_content_without_mode_dependent_escaping(self):
        text = "a=Trueblue, b=NoneSuch; quote' backslash\\ 中文\x00"
        sql = self.sql.delete({"note": text})
        self.assertIsInstance(sql, str)
        self.assertIn("CONVERT(X'{}' USING utf8mb4)".format(text.encode().hex()), sql)
        self.assertNotIn(text, sql)
        self.assertIn("`v` IS NULL", self.sql.count({"v": None}))
        self.assertIn("`v` = X'00616263'", self.sql.count({"v": b"\x00abc"}))
        self.assertIn("`v` = 1", self.sql.count({"v": True}))

    def test_supported_temporal_and_decimal_values(self):
        self.assertIn("12.30", self.sql.count({"v": Decimal("12.30")}))
        for value in (datetime(2026, 11, 10, 12, 30), timedelta(hours=-25, microseconds=5)):
            self.assertIn("CONVERT(X'", self.sql.count({"v": value}))

    def test_read_empty_conditions(self):
        for where in (None, {}):
            self.assertEqual(self.sql.count(where), "SELECT COUNT(*) FROM `users`;")
            self.assertEqual(self.sql.exists(where), "SELECT 1 FROM `users` LIMIT 1;")

    def test_limit_detection(self):
        self.assertTrue(self.sql.exists({"note": "unlimited"}).endswith(" LIMIT 1;"))
        self.assertTrue(self.sql.exists("note='limit 5'").endswith(" LIMIT 1;"))
        self.assertEqual(self.sql.exists("id>1 LIMIT 2;"), "SELECT 1 FROM `users` WHERE id>1 LIMIT 2;")
        self.assertTrue(self.sql.exists("id IN (SELECT id FROM t LIMIT 2)").endswith(" LIMIT 1;"))

    def test_backslash_in_quoted_identifier(self):
        sql = self.sql.exists({"path\\": "value"})
        self.assertTrue(sql.endswith(" LIMIT 1;"))
        self.assertIn("`path\\`", sql)
        self.assertTrue(self.sql.exists("`path\\`=1").endswith(" LIMIT 1;"))

    def test_raw_fragments_reject_multiple_statements(self):
        for fragment in ("1; DELETE FROM t", "1 -- comment", "1 /* comment */", "name='broken"):
            with self.subTest(fragment=fragment), self.assertRaises(ValueError):
                self.sql.delete(fragment)
        self.assertIn("name='a;b--c'", self.sql.delete("name='a;b--c';"))

    def test_create_table_preserves_sql_literals_and_quotes_columns(self):
        sql = self.sql.create_table({"select": "ENUM('a','b') DEFAULT 'a'", "name": "VARCHAR(20) DEFAULT 'new'"})
        self.assertIn("`select` ENUM('a','b') DEFAULT 'a'", sql)
        self.assertIn("DEFAULT 'new'", sql)
        self.assertIn("PRIMARY KEY (`id`)", self.sql.create_table(["`id` INT", "PRIMARY KEY (`id`)"]))
        for kwargs in ({"keys": {}}, {"keys": {"id": "INT"}, "engine": "InnoDB; DROP"},
                       {"keys": {"id": "INT"}, "charset": "utf8mb4 --"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.sql.create_table(**kwargs)

    def test_replace(self):
        sql, rows = self.sql.replace({"id": 1})
        self.assertTrue(sql.startswith("REPLACE INTO"))
        self.assertEqual(rows, [[1]])
        self.assertEqual(self.sql.replace(["id", "v"], [1, 2])[1], [[1, 2]])
        self.assertEqual(self.sql.replace(["id"], [[1], [2]])[1], [[1], [2]])
        with self.assertRaises(TypeError):
            self.sql.replace({"id": 1}, [99])
        with self.assertRaises(ValueError):
            self.sql.replace(["id", "v"], [[1]])

    def test_select_and_unsupported_operations(self):
        self.assertEqual(self.sql.select(), "SELECT * FROM `users`;")
        sql = self.sql.select("role, COUNT(*)", where={"active": True}, group_by="role", distinct=True)
        self.assertEqual(sql, "SELECT DISTINCT role, COUNT(*) FROM `users` WHERE `active` = 1 GROUP BY role;")
        for method in (self.sql.drop, self.sql.truncate):
            with self.assertRaises(NotImplementedError):
                method()


if __name__ == "__main__":
    unittest.main()
