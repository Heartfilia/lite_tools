# -*- coding: utf-8 -*-
import re
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from typing import Union, Optional, Mapping, List, Dict, Tuple

from lite_tools.utils.u_sql_base_string import MysqlKeywordsList
from lite_tools.exceptions.SqlExceptions import NotSupportType, LengthError


__ALL__ = ["SqlString"]


class SqlString(object):
    """
    这里只负责拼接sql语句 不负责处理sql事务
    这个功能主要是配合Mysql使用，当然单独使用也可以，后续拿到sql语句自己操作也可以
    大部分键值操作推荐用字典，当然其它格式也有些许兼容，处理的语法都是最基础的 进阶的操作自己实现
    """

    def __init__(self, table_name: str = None) -> None:
        """这里和实际调用的地方二选一 都写的话 优先级是代码位置更高 优先取用"""
        self.table_name = table_name

    def check_table_name(self, table_name: str = None):
        if not table_name and not self.table_name:
            raise ValueError("缺少表名")

    @staticmethod
    def _parse_dict(item: Union[dict, str], origin_keys: list = None, mode: str = "key"):
        keys = []
        now_value = []
        if isinstance(item, dict):
            if origin_keys:   # 如果有明确的key的顺序提取值传入
                for key in origin_keys:
                    value = item[key]
                    if isinstance(value, bool):
                        value = 1 if value else 0
                    elif value is None and mode == "key":
                        value = ""
                    elif value is None and mode == "where":
                        value = " IS NULL "
                    now_value.append(value)
                return origin_keys, now_value
            else:
                for key, value in item.items():
                    keys.append(key)
                    if isinstance(value, bool):
                        value = 1 if value else 0
                    elif value is None and mode == "key":
                        value = ""
                    elif value is None and mode == "where":
                        value = " IS NULL "

                    now_value.append(value)
        else:
            keys.append(item)

        return keys, now_value

    def _handle_items(
            self,
            item: Union[dict, Mapping[str, any], str],
            mode: str = "key"
    ) -> Tuple[List[str], List[any]]:
        keys = []
        values = []

        if isinstance(item, dict):
            keys, value = self._parse_dict(item, mode=mode)
            values.append(value)
        elif isinstance(item, list):  # 如果这种情况的话 里面每个值的顺序必须得一致
            origin_keys = []
            for row in item:
                key, value = self._parse_dict(row, origin_keys, mode=mode)
                if not keys:
                    keys = key
                    origin_keys = key
                values.append(value)
        return keys, values

    def insert(
            self,
            item: Union[Mapping[str, any], List[Mapping[str, any]]],
            table_name: str = "",
            duplicate_except: list = None,
            ignore: bool = False
    ) -> Tuple[str, List[any]]:
        """
        创建数据模板 和对应的数据结果
        :param item  : -> dict模式 直接处理为单条 {"a": 1, "b": False} -> a=1,b=0
                       -> list模式 传入的是多组[{"a": 1, "b": False}, {"a": 1, "b": False}]
        :param table_name      : 表名,这里优先级高于全局
        :param duplicate_except: 这里是排除法一般这里建议把你不需要替换的字段名称写上去 None的话就不 insert... on duplicate
        :param ignore          : 一般这里是忽略表里已经存在的时候 这里优先级高于上面 这个和上面都写了的话 是直接忽略重复异常
        """
        assert table_name or self.table_name, "请至少在一个入口位置传入table_name"
        keys, values = self._handle_items(item)

        key_string = ", ".join(map(lambda x: f"`{x}`", keys))
        value_string = ", ".join("%s" for _ in keys)
        if ignore:
            ignore = " IGNORE"
            dup = ""
        else:
            if duplicate_except and isinstance(duplicate_except, list):
                up = ", ".join(f"`{key}`=VALUES(`{key}`)" for key in keys if key not in duplicate_except)
                dup = f" ON DUPLICATE KEY UPDATE {up}"
            else:
                dup = ""
            ignore = ""

        return (
            f"INSERT{ignore} INTO `{table_name or self.table_name}` ({key_string}) VALUES ({value_string}){dup};",
            values
        )

    def update(
            self,
            item: Union[List[Mapping[str, any]], Mapping[str, any]],
            where: Union[str, List[str], Mapping[str, any], List[Mapping[str, any]]],
            table_name: str = ""
    ):
        """
        :param item      : 需要更新的字段
        :param where     : 条件，如果不是dict，那么这里就是直接用了拼接上 不需要构造模板 | 如果是批量更新 只能用等的情况 要不然批量没意义
        :param table_name: 表名,这里优先级高于全局
        """
        assert table_name or self.table_name, "请至少在一个入口位置传入table_name"
        if isinstance(item, list) and isinstance(where, (dict, str)):
            raise Exception("批量更新,where位置需要传入列表,里面的每一个元素对应更新值的位置")

        keys, values = self._handle_items(item)
        where_values = []

        if isinstance(where, dict):
            where_keys, where_values = self._handle_items(where, mode="where")
            where_string = " AND ".join(map(lambda x: f"`{x}` = %s", where_keys))
        elif isinstance(item, dict) and isinstance(where, dict):   # 如果前面是单个条件的情况
            where_string = " AND ".join(where)
        elif isinstance(item, list) and isinstance(where, list) and where and isinstance(where[0], dict):   # 前后都是列表
            # 批量更新 不能用其它情况 只能用 xxx=xxx  多个条件也得，但是一定是等值
            assert len(set(map(lambda x: len(x), where))) == 1, "批量更新,where位置的元素长度不一致"
            other_keys = []
            for each_where in where:
                round_key, round_value = self._parse_dict(each_where, other_keys, "where")
                if not other_keys:
                    other_keys = round_key
                where_values.append(round_value)
            where_string = " AND ".join(map(lambda x: f"`{x}` = %s", other_keys))
        elif isinstance(where, str):
            where_string = where
        else:
            raise Exception(f"错误的参数值类型: item{type(item)} where{type(where)}")

        file_string = ", ".join(map(lambda x: f"`{x}` = %s", keys))
        base_update = "UPDATE"

        new_values = []
        if where_values:
            for ind, value in enumerate(values):
                new_values.append(value + where_values[ind])
        else:
            new_values = values
        result_where = "" if not where_string else f" WHERE {where_string}"
        return f"{base_update} {table_name or self.table_name} SET {file_string}{result_where};", new_values

    @staticmethod
    def __clear_string(string: str) -> str:
        string = re.sub("= ?[Nn]one|is ?[Nn]one", "IS NULL", string)
        string = re.sub("= ?[Tt]rue", "= 1", string)
        string = re.sub("= ?[Ff]alse", "= 0", string)
        return string.replace(",) VALUES", ") VALUES").replace(',);', ');')

    def __handle_create_data(self, keys):
        """
        K神专用函数 <<<<<<<<<<
        """
        dddd = list(keys.items())
        field_str = ""

        for i in range(len(dddd)):
            if i == len(dddd) - 1:
                field_str += dddd[i][0] + " " + dddd[i][1]
            else:
                field_str += dddd[i][0] + " " + dddd[i][1] + " ,"

        return field_str

    def create_table(self, keys: Union[dict, list], engine: str = 'InnoDB', charset: str = 'utf8mb4',
                     table_name: str = None) -> Optional[str]:
        """
        K神专用函数 <<<<<<<<<<
        如果是拼接单条sql: keys传入字典 自动提取键值
        如果是多值拼接   : keys传入需要插入的字段命 可以列表 可以元组
        :param keys
        :param engine
        :param charset
        :param table_name
        """
        self.check_table_name(table_name)
        if not keys:
            return None
        base_create = f"CREATE TABLE `{table_name or self.table_name}`"
        # key_string, value_string = self.__handle_create_data(keys, values)
        key_string = self.__handle_create_data(keys)
        if key_string == "":
            return None
        insert_string = f"{base_create} ({self._handle_key(key_string)}) ENGINE={engine} DEFAULT CHARSET={charset};"
        return self.__clear_string(insert_string)

    def replace(self, keys: Union[dict, list, tuple], values: list = None, table_name: str = None) -> Optional[str]:
        """
        不确定是否可以用 <<<
        """
        self.check_table_name(table_name)
        string = self.insert(keys, values, table_name=table_name)
        string = string.replace('INSERT', 'REPLACE')
        return string

    def delete(self, where: Union[dict, str] = None, table_name: str = None) -> Optional[str]:
        """
        这里不推荐用list,tuple数据类型 如果有多个等值条件就写dict  否则自己写字符串
        :param where: 当然是删除条件啦 不写的话就是全部删除
        :param table_name: 表名 优先级高于全局那个
        """
        self.check_table_name(table_name)
        base_delete = f"DELETE FROM {table_name or self.table_name}"
        if not where:
            return base_delete + ";"
        base_delete += " WHERE "
        if isinstance(where, dict):
            for key, value in where.items():
                base_delete += (f'{key if key.upper() not in MysqlKeywordsList else f"`{key}`"} = '
                                f'{value if isinstance(value, (int, float, bool)) or value is None else self._handle_value(value)} '
                                f'AND ')
            base_delete = base_delete.rstrip(' AND ') + ";"
        elif isinstance(where, str):
            base_delete += where + ";"
        else:
            raise NotSupportType
        return self.__clear_string(base_delete)

    def exists(self, where: Union[dict, str], table_name: str = None) -> Optional[str]:
        """
        这个是查询键值在不在mysql中,一般推荐用**主键** 如果用其它键就需要加索引了
        """
        self.check_table_name(table_name)
        base_sql = f"SELECT 1 FROM {table_name or self.table_name} WHERE "
        if isinstance(where, dict):
            base_sql = base_sql + self._handle_where_dict(where)
        elif isinstance(where, str):
            base_sql += where
        else:
            raise NotSupportType
        if not re.search("where.*?limit", base_sql, re.I):
            base_sql = base_sql.strip(";") + " LIMIT 1;"
        elif not base_sql.strip().endswith(";"):
            base_sql += ";"
        return self.__clear_string(base_sql)

    def count(self, where: Union[dict, str] = None, table_name: str = None) -> Optional[str]:
        """
        只适用于全局统计 可以加条件 但是不适合 查询条件group 之类的统计
        """
        self.check_table_name(table_name)
        base_sql = f"SELECT COUNT(*) FROM {table_name or self.table_name}"
        if where is None:
            return f"{base_sql};"

        base_sql += " WHERE "
        if isinstance(where, dict):
            base_sql = base_sql + self._handle_where_dict(where)
        elif isinstance(where, str):
            base_sql += where
            if not base_sql.endswith(';'):
                base_sql += ";"
        else:
            raise NotSupportType
        return self.__clear_string(base_sql)

    def truncate(self) -> Optional[str]:
        """
        不提供这个功能 navicat 永远的神
        """

    def drop(self) -> Optional[str]:
        """
        不提供这个功能 删了还玩啥 还得create表 麻烦 用navicat多好
        """

    def select(self, condition="*", join_group="", where="", group_by="", distinct=False) -> Optional[str]:
        """
        #(^_^)这东西太复杂了 不想写
        """

    @staticmethod
    def _handle_key(key_string: str) -> str:
        key_string = re.sub(r"'`|`'", "`", key_string)
        key_string = re.sub(r"'", '', key_string)
        return key_string

    @staticmethod
    def _handle_value(item: Union[str, list, tuple, dict, set], *, decorate: bool = True):
        if not isinstance(item, str):
            item = str(item)

        base_string = ""
        last_word = ""
        for word in item:
            if word == "'" and last_word == "\\":
                word = "\\\\'"
            elif word == "'":
                word = "\\'"
            base_string += word
            last_word = word

        if not decorate:
            return base_string
        else:
            return repr(base_string)  # 这里好像是sqlite需要的格式

    def _handle_where_dict(self, where: dict) -> str:
        base_string = ""
        for key, value in where.items():
            base_string += f'{key if key.upper() not in MysqlKeywordsList else f"`{key}`"} = ' \
                           f'{value if isinstance(value, (int, float, bool)) or value is None else self._handle_value(value)} ' \
                           f'AND '
        base_string = base_string.rstrip(' AND ') + ";"
        return base_string


if __name__ == "__main__":
    base = SqlString("t_talent")
    # print(base.insert({"a": 1, "b": False, "c": "xxx"}))
    # print(base.insert([{"a": 1, "b": False, "c": "xxx"}, {"a": 2, "b": True, "c": "yyy"}], duplicate_except=['a']))
    # print(base.update({"a": 1, "b": 2}, {"c": 5}))
    # print(base.update({"a": 1, "b": 2}, "c IS NULL AND d > 50"))
    # print(base.update({"a": 1, "b": 2}, ["c IS NULL", "d > 50"]))
    # print(base.update([{"a": 1}, {"a": 2}, {"a": 3}], [{"d": 5}, {"d": 1}, {"d": 10}]))

