# -*- coding: utf-8 -*-
"""Small MySQL statement builder; values and identifiers are never SQL expressions.

The public return shapes are kept for compatibility: insert/update/replace return
(sql, rows), while delete/exists/count/create_table/select return SQL strings.
Raw WHERE, JOIN and DDL fragments must come from trusted application code.
"""
import math
import re
from collections.abc import Mapping
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, List, Optional, Tuple, Union


__all__ = ["SqlString"]
__ALL__ = __all__


class SqlString(object):
    def __init__(self, table_name: str = None) -> None:
        self.table_name = table_name

    def check_table_name(self, table_name: str = None):
        self._table(table_name)

    def _table(self, table_name=None):
        name = self.table_name if table_name is None or table_name == "" else table_name
        if name is None or name == "":
            raise ValueError("缺少表名")
        return self._quote_identifier(name)

    @staticmethod
    def _normalize_param_value(value: Any):
        if value is None:
            return None
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("SQL 数值不能是 NaN 或 Infinity")
        if isinstance(value, Decimal) and not value.is_finite():
            raise ValueError("SQL 数值不能是 NaN 或 Infinity")
        if isinstance(value, (str, bytes, int, float, Decimal, date, time, timedelta)):
            return value
        if isinstance(value, (bytearray, memoryview)):
            return bytes(value)
        raise TypeError("不支持的 SQL 值类型: {}".format(type(value).__name__))

    @classmethod
    def _quote_identifier(cls, identifier: str) -> str:
        if not isinstance(identifier, str):
            raise TypeError("表名和字段名必须是字符串")
        # Read qualified identifiers without splitting dots inside quoted parts.
        parts = []
        index = 0
        while index < len(identifier):
            if identifier[index] == "`":
                index += 1
                part = ""
                while index < len(identifier):
                    char = identifier[index]
                    index += 1
                    if char == "`":
                        if index < len(identifier) and identifier[index] == "`":
                            part += "`"
                            index += 1
                        else:
                            break
                    else:
                        part += char
                else:
                    raise ValueError("标识符反引号未闭合")
                if index < len(identifier) and identifier[index] != ".":
                    raise ValueError("反引号标识符后只能接限定名称分隔符")
            else:
                end = identifier.find(".", index)
                end = len(identifier) if end == -1 else end
                part = identifier[index:end]
                index = end
            if not part or not part.strip() or any(ord(char) < 32 for char in part):
                raise ValueError("表名和字段名不能为空或含控制字符")
            if part == "*":
                raise ValueError("此处不接受通配符")
            parts.append("`{}`".format(part.replace("`", "``")))
            if index < len(identifier):
                index += 1
                if index == len(identifier):
                    raise ValueError("标识符不能以点结束")
        if not parts:
            raise ValueError("表名和字段名不能为空")
        return ".".join(parts)

    @classmethod
    def _build_where_clause(cls, keys: List[str]) -> str:
        return " AND ".join("{} <=> %s".format(cls._quote_identifier(key).replace("%", "%%")) for key in keys)

    @classmethod
    def _format_direct_value(cls, value: Any) -> str:
        """Render standalone SQL independently of NO_BACKSLASH_ESCAPES.

        Text is represented as UTF-8 hex plus an explicit character conversion;
        bytes stay binary. Driver-backed operations use parameters instead.
        """
        value = cls._normalize_param_value(value)
        if value is None:
            return "NULL"
        if isinstance(value, (int, float, Decimal)):
            return str(value)
        if isinstance(value, bytes):
            return "X'{}'".format(value.hex())
        if isinstance(value, datetime):
            value = value.isoformat(sep=" ")
        elif isinstance(value, (date, time)):
            value = value.isoformat()
        elif isinstance(value, timedelta):
            total_us = ((value.days * 86400 + value.seconds) * 1000000 + value.microseconds)
            sign = "-" if total_us < 0 else ""
            seconds, micros = divmod(abs(total_us), 1000000)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            value = "{}{:02d}:{:02d}:{:02d}.{:06d}".format(sign, hours, minutes, seconds, micros)
        return "CONVERT(X'{}' USING utf8mb4)".format(value.encode("utf-8").hex())

    @classmethod
    def _parse_dict(cls, item, origin_keys=None, mode="key"):
        if not isinstance(item, Mapping):
            raise TypeError("每条数据和字典条件必须是 Mapping")
        if not item:
            raise ValueError("数据和写入条件不能为空")
        keys = list(item) if origin_keys is None else list(origin_keys)
        if set(item) != set(keys):
            raise ValueError("批量数据的字段集合必须完全一致")
        for key in keys:
            cls._quote_identifier(key)
        return keys, [cls._normalize_param_value(item[key]) for key in keys]

    def _handle_items(self, item, mode="key"):
        rows = [item] if isinstance(item, Mapping) else item
        if not isinstance(rows, list):
            raise TypeError("数据必须是 Mapping 或 Mapping 列表")
        if not rows:
            raise ValueError("批量数据不能为空")
        keys = None
        values = []
        for row in rows:
            keys, row_values = self._parse_dict(row, keys, mode)
            values.append(row_values)
        return keys, values

    @staticmethod
    def _raw_fragment(fragment):
        """Validate one trusted SQL fragment, returning SQL and a literal mask.

        This is not an SQL sanitizer. Reject statement separators/comments, but
        leave quoted content untouched (including percent signs and semicolons).
        The mask is only used for recognizing trailing LIMIT syntax.
        """
        if not isinstance(fragment, str):
            raise TypeError("SQL 条件必须是字符串")
        text = fragment.strip()
        if text.endswith(";"):
            text = text[:-1].rstrip()
        if not text:
            raise ValueError("SQL 条件不能为空")
        mask = []
        quote = None
        index = 0
        while index < len(text):
            char = text[index]
            if quote is not None:
                mask.append(" ")
                if char == "\\" and quote != "`":
                    index += 1
                    if index < len(text):
                        mask.append(" ")
                elif char == quote:
                    if index + 1 < len(text) and text[index + 1] == quote:
                        index += 1
                        mask.append(" ")
                    else:
                        quote = None
            elif char in ("'", '"', "`"):
                quote = char
                mask.append(" ")
            elif char == ";" or char == "#" or text[index:index + 2] in ("--", "/*", "*/"):
                raise ValueError("SQL 片段不能含多语句或注释；请直接使用 execute 执行可信 SQL")
            else:
                mask.append(char)
            index += 1
        if quote is not None:
            raise ValueError("SQL 片段中的引号未闭合")
        return text, "".join(mask)

    def _where_parameters(self, where, allow_empty=False):
        """Internal parameterized counterpart of the public string methods."""
        if where is None or (isinstance(where, Mapping) and not where):
            if allow_empty:
                return "", []
            raise ValueError("更新和删除必须提供非空条件；整表操作请显式使用可信 SQL")
        if isinstance(where, Mapping):
            keys, values = self._parse_dict(where)
            return self._build_where_clause(keys), values
        text, _ = self._raw_fragment(where)
        return text, []

    def _direct_where(self, where, allow_empty=False):
        if where is None or (isinstance(where, Mapping) and not where):
            if allow_empty:
                return ""
            raise ValueError("删除必须提供非空条件；整表操作请显式使用可信 SQL")
        if isinstance(where, Mapping):
            return self._handle_where_dict(where).rstrip(";")
        return self._raw_fragment(where)[0]

    def insert(self, item: Union[Mapping, List[Mapping]], table_name: str = "", duplicate_except: list = None,
               ignore: bool = False) -> Tuple[str, List[Any]]:
        """Build INSERT and parameter rows. None disables upsert; [] updates all fields.

        INSERT IGNORE takes precedence over duplicate_except. All batch rows must
        have exactly the same fields, but their insertion order may differ.
        """
        table = self._table(table_name)
        keys, values = self._handle_items(item)
        if not isinstance(ignore, bool):
            raise TypeError("ignore 必须是 bool")
        duplicate = ""
        if not ignore and duplicate_except is not None:
            if not isinstance(duplicate_except, list):
                raise TypeError("duplicate_except 必须是字段名列表或 None")
            if any(not isinstance(key, str) for key in duplicate_except):
                raise TypeError("duplicate_except 必须只包含字段名")
            unknown = set(duplicate_except) - set(keys)
            if unknown:
                raise ValueError("duplicate_except 包含未插入的字段: {}".format(sorted(unknown)))
            update_keys = [key for key in keys if key not in duplicate_except]
            if not update_keys:
                raise ValueError("duplicate_except 排除了全部字段；如需忽略冲突请使用 ignore=True")
            duplicate = " ON DUPLICATE KEY UPDATE " + ", ".join(
                "{0}=VALUES({0})".format(self._quote_identifier(key)) for key in update_keys)
        return (
            "INSERT{} INTO {} ({}) VALUES ({}){};".format(
                " IGNORE" if ignore else "", table.replace("%", "%%"),
                ", ".join(self._quote_identifier(key).replace("%", "%%") for key in keys),
                ", ".join("%s" for _ in keys), duplicate.replace("%", "%%")),
            values,
        )

    def update(self, item: Union[List[Mapping], Mapping],
               where: Union[str, List[str], Mapping, List[Mapping]], table_name: str = ""):
        """Build UPDATE and parameter rows; batch conditions must be dicts.

        A string list for a single item means parenthesized AND conditions.
        Raw SQL conditions are trusted code, not user-supplied values.
        """
        table = self._table(table_name)
        keys, values = self._handle_items(item)
        if isinstance(item, list):
            if not isinstance(where, list) or len(where) != len(values):
                raise ValueError("批量更新的数据和条件列表必须等长")
            if not all(isinstance(condition, Mapping) for condition in where):
                raise TypeError("批量更新的每条条件必须是非空 Mapping")
            where_keys, where_rows = self._handle_items(where, mode="where")
            clause = self._build_where_clause(where_keys)
            rows = [value + condition for value, condition in zip(values, where_rows)]
        elif isinstance(where, list):
            if not where or not all(isinstance(condition, str) for condition in where):
                raise ValueError("单条更新的条件列表必须是非空字符串列表")
            clause = " AND ".join("({})".format(self._raw_fragment(condition)[0]) for condition in where)
            clause = clause.replace("%", "%%")
            rows = values
        else:
            clause, params = self._where_parameters(where)
            if isinstance(where, str):
                clause = clause.replace("%", "%%")
            rows = [values[0] + params]
        # Escape literal percents for the driver's parameter interpolation.
        set_clause = ", ".join("{} = %s".format(self._quote_identifier(key).replace("%", "%%")) for key in keys)
        return "UPDATE {} SET {} WHERE {};".format(table.replace("%", "%%"), set_clause, clause), rows

    def create_table(self, keys: Union[dict, list], engine: str = 'InnoDB', charset: str = 'utf8mb4',
                     table_name: str = None) -> str:
        """Build DDL from {column: trusted_definition} or trusted definition strings.

        Column types/defaults/constraints are application SQL, not data values.
        A list must contain full definitions (e.g. ['`id` BIGINT PRIMARY KEY']).
        """
        table = self._table(table_name)
        for name, value in (("engine", engine), ("charset", charset)):
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
                raise ValueError("{} 必须是有效的 MySQL 名称".format(name))
        if isinstance(keys, Mapping):
            if not keys:
                raise ValueError("建表字段不能为空")
            definitions = ["{} {}".format(self._quote_identifier(key), self._raw_fragment(value)[0])
                           for key, value in keys.items()]
        elif isinstance(keys, (list, tuple)) and keys:
            definitions = [self._raw_fragment(value)[0] for value in keys]
        else:
            raise ValueError("keys 必须是非空字段字典或完整字段定义列表")
        return "CREATE TABLE {} ({}) ENGINE={} DEFAULT CHARSET={};".format(
            table, ", ".join(definitions), engine, charset)

    def replace(self, keys: Union[Mapping, List[Mapping]], values: list = None,
                table_name: str = None) -> Tuple[str, List[Any]]:
        """Build REPLACE (delete/insert semantics, not UPDATE).

        Accept a mapping/batch of mappings, or column names plus one/batch of
        value rows. Supplying values alongside a mapping is an error.
        """
        if values is None:
            statement, rows = self.insert(keys, table_name=table_name)
        else:
            if not isinstance(keys, (list, tuple)) or not keys or not all(isinstance(key, str) for key in keys):
                raise TypeError("传入 values 时，keys 必须是字段名列表")
            if len(set(keys)) != len(keys):
                raise ValueError("字段名不能重复")
            if not isinstance(values, (list, tuple)) or not values:
                raise ValueError("values 必须是非空值列表或行列表")
            value_rows = values if isinstance(values[0], (list, tuple)) else [values]
            items = []
            for row in value_rows:
                if not isinstance(row, (list, tuple)) or len(row) != len(keys):
                    raise ValueError("values 的每一行必须与字段名等长")
                items.append(dict(zip(keys, row)))
            statement, rows = self.insert(items, table_name=table_name)
        return statement.replace("INSERT", "REPLACE", 1), rows

    def delete(self, where: Union[dict, str] = None, table_name: str = None) -> str:
        """Build DELETE. Empty conditions are rejected; '1=1' is explicit opt-in."""
        return "DELETE FROM {} WHERE {};".format(self._table(table_name), self._direct_where(where))

    def exists(self, where: Union[dict, str], table_name: str = None) -> str:
        clause = self._direct_where(where, allow_empty=True)
        statement = "SELECT 1 FROM {}{}".format(self._table(table_name), " WHERE " + clause if clause else "")
        # Only recognize a numeric LIMIT at the end, never inside quoted values.
        mask = self._raw_fragment(clause)[1] if clause and isinstance(where, str) else ""
        if not re.search(r"\bLIMIT\s+\d+(?:\s*,\s*\d+|\s+OFFSET\s+\d+)?\s*$", mask, re.I):
            statement += " LIMIT 1"
        return statement + ";"

    def count(self, where: Union[dict, str] = None, table_name: str = None) -> str:
        clause = self._direct_where(where, allow_empty=True)
        return "SELECT COUNT(*) FROM {}{};".format(self._table(table_name), " WHERE " + clause if clause else "")

    def truncate(self) -> Optional[str]:
        raise NotImplementedError("不提供 TRUNCATE 构造；请显式执行可信 SQL")

    def drop(self) -> Optional[str]:
        raise NotImplementedError("不提供 DROP 构造")

    def select(self, condition="*", join_group="", where="", group_by="", distinct=False) -> str:
        """Build a basic SELECT. Projection/JOIN/GROUP BY strings are trusted SQL."""
        if not isinstance(distinct, bool):
            raise TypeError("distinct 必须是 bool")
        projection = self._raw_fragment(condition)[0]
        statement = "SELECT {}{} FROM {}".format("DISTINCT " if distinct else "", projection, self._table())
        if join_group:
            statement += " " + self._raw_fragment(join_group)[0]
        if where != "":
            clause = self._direct_where(where, allow_empty=True)
            if clause:
                statement += " WHERE " + clause
        if group_by:
            statement += " GROUP BY " + self._raw_fragment(group_by)[0]
        return statement + ";"

    @staticmethod
    def _handle_key(key_string: str) -> str:
        # Kept for older callers; never strip SQL quotes or rewrite data.
        return key_string

    @classmethod
    def _handle_value(cls, item, *, decorate: bool = True):
        if not decorate:
            raise ValueError("不支持生成未加保护的 SQL 值")
        return cls._format_direct_value(item)

    def _handle_where_dict(self, where: dict) -> str:
        keys, values = self._parse_dict(where)
        return " AND ".join(
            "{} IS NULL".format(self._quote_identifier(key)) if value is None else
            "{} = {}".format(self._quote_identifier(key), self._format_direct_value(value))
            for key, value in zip(keys, values)) + ";"
