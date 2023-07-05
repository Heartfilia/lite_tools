# -*- coding: utf-8 -*-
import re
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from typing import Union, Optional, Mapping, List, Dict

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

    def insert(self, keys: Union[dict, list, tuple], values: list = None, table_name: str = None, ignore: bool = False) -> Optional[str]:
        """
        如果是拼接单条sql: keys传入字典 自动提取键值  values不需要传
        如果是多值拼接   : keys传入需要插入的字段命 可以列表 可以元组
                        : values传入对应的值得列表 里面放元组 如: [(1, "a"), (99, "test")]  / 也可以[1, "a"] 这样就是单条插入
        :param keys
        :param values
        :param table_name
        :param ignore   : 是否忽略插入中的重复值之类的
        """
        self.check_table_name(table_name)
        if not keys:
            return None
        whether_ignore = "IGNORE " if ignore is True else ""
        base_insert = f"INSERT {whether_ignore}INTO {table_name or self.table_name}"
        key_string, value_string = self.__handle_insert_data(keys, values)
        if key_string == "":
            return None
        insert_string = f"{base_insert} {self._handle_key(key_string)} VALUES {value_string};"
        return self.__clear_string(insert_string)

    @staticmethod
    def __clear_string(string: str) -> str:
        string = re.sub("= ?[Nn]one|is ?[Nn]one", "IS NULL", string)
        string = re.sub("= ?[Tt]rue", "= 1", string)
        string = re.sub("= ?[Ff]alse", "= 0", string)
        return string.replace(",) VALUES", ") VALUES").replace(',);', ');')

    def __handle_insert_data(self, key, value):
        if isinstance(key, dict) and value is None:
            keys = []
            values = []
            for key, name in key.items():
                keys.append(key if key.upper() not in MysqlKeywordsList else f"`{key}`")
                values.append(name)
            values_string = '('
            for each_value in values:
                if isinstance(each_value, str):
                    each_value = self._handle_value(each_value)
                values_string += f'{each_value}, '
            values_string = values_string.rstrip(', ') + ')'
            return f"{tuple(keys)}", values_string
        elif isinstance(key, (list, tuple)) and not value and isinstance(key[0], dict):
            result_dict = {}
            # 第一步构造键值对
            for item in key:
                for k, v in item.items():
                    if isinstance(v, str):
                        v = self._handle_value(v, decorate=False)
                    if k not in result_dict:
                        result_dict[k] = [v]
                    else:
                        result_dict[k].append(v)
            # 第二步校验值的长度是否一致
            assert len(set(map(lambda x: len(x), result_dict.values()))) == 1, \
                f"传入的键个数为: {len(result_dict)}, 而传入的值个数不等;"
            keys = [k if k.upper() not in MysqlKeywordsList else f"`{k}`" for k in result_dict.keys()]
            # 开始拼接
            return f"{tuple(keys)}", \
                   f"{list(zip(*result_dict.values()))}"[1:-1]
        elif isinstance(key, (list, tuple)) and isinstance(value, list):
            keys = [k if k.upper() not in MysqlKeywordsList else f"`{k}`" for k in key]
            if value and isinstance(value[0], (list, tuple)):
                # 这里是批量插入
                values = '('
                for value_jar in value:
                    for each_value in value_jar:
                        each_value = self._handle_value(each_value)
                        values += each_value + ', '
                values = values.rstrip(', ') + ')'
            else:
                # 这里只是兼容另外一种格式而已 推荐的还是字典
                values = '('
                for each_value in value:
                    each_value = self._handle_value(each_value, decorate=False)
                    values += each_value + ', '
                values = values.rstrip(', ') + ')'
            return f"{tuple(keys)}", values
        else:
            raise NotSupportType

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

    def update(self, keys: dict, where: Union[dict, list, tuple, str], table_name: str = None) -> Optional[str]:
        """
        更新数据操作, 传入需要更新的字典即可
        :param keys :  传入的更新部分的键值对啦
        :param where: 当然是筛选条件 -->
            如果用字典传入-> 相当于 "=" , 多个值会AND拼接 : True 会被替换为1 False会被替换为0 None 会被替换为NULL
            # 想实现更加精准的条件就在下面自己写 推荐==>字符串的传入方式
            --> 如果是列表传入按照 ['test<5', 'hello=1', 'tt LIKES "%VV%"'] 这样传入
            --> 如果是字符串: 'test < 5 AND hello = 1'   这样传入
        :param table_name: 表名 优先级 高于全局那个
        """
        self.check_table_name(table_name)
        if not keys or not isinstance(keys, dict) or not where:
            raise NotSupportType

        base_update = f"UPDATE {table_name or self.table_name} SET "
        for key, value in keys.items():
            base_update += f'{key if key.upper() not in MysqlKeywordsList else f"`{key}`"} = ' \
                           f'{value if isinstance(value, (int, float, bool)) or value is None else self._handle_value(value)}, '
        base_update = base_update.rstrip(', ') + " WHERE "
        if isinstance(where, dict):
            base_update = base_update + self._handle_where_dict(where)
        elif isinstance(where, (list, tuple)):
            for value in where:
                if isinstance(value, dict):
                    for w_k, w_v in value.items():
                        base_update += f'{w_k if w_k.upper() not in MysqlKeywordsList else f"`{w_k}`"} = ' \
                                       f'{w_v if isinstance(w_v, (int, float, bool)) or w_v is None else self._handle_value(w_v)} AND '
                else:
                    base_update += f"{value} AND "
            base_update = base_update.rstrip(' AND ') + ";"
        elif isinstance(where, str):
            base_update += where + ";"
        else:
            raise NotSupportType
        return self.__clear_string(base_update)

    def update_batch(self, items: Union[Mapping[str, list], List[dict]], where: Union[Mapping[str, list], List[dict]],
                     table_name: str = None):
        """
        批量更新操作 支持两种不同格式混用 但是位置顺序得对应
        """
        if items and isinstance(items, list) and isinstance(items[0], dict):
            items = self._handle_items_type(items)
        if where and isinstance(where, list) and isinstance(where[0], dict):
            where = self._handle_items_type(where)

        self.check_table_name(table_name)
        set_field, where_field, value_field = self._handle_update_batch(items, where)
        return f"UPDATE {table_name or self.table_name} SET {set_field} WHERE {where_field}", value_field

    def insert_batch(self, items: Union[Mapping[str, list], List[dict]], duplicate: Literal['ignore', 'update', None] = None, *,
                     update_field: List[str] = None, table_name: str = None):
        self.check_table_name(table_name)
        if items and isinstance(items, list) and isinstance(items[0], dict):
            # 兼容 [{}, {}] 这个格式
            new_items = self._handle_items_type(items)
        else:
            new_items = items
        key, field, values = self._handle_batch(new_items)
        if duplicate == "ignore":
            ignore_field, duplicate_field, update_string = "IGNORE ", "", ""
        elif duplicate == "update":
            if not update_field:
                raise LengthError("更新模式需要补充 update_field 字段数据")
            else:
                if all([x in new_items.keys() for x in update_field]):
                    update_string = ", ".join([f"{name} = VALUES({name})" for name in update_field])
                else:
                    raise LengthError("可更新字段不在传入的数据表里面")
            ignore_field, duplicate_field = "", " ON DUPLICATE KEY UPDATE "
        else:
            ignore_field, duplicate_field, update_string = "", "", ""
        return f"INSERT {ignore_field}INTO {table_name or self.table_name} {key} VALUES {field}{duplicate_field}{update_string}", values

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
                base_delete += f'{key if key.upper() not in MysqlKeywordsList else f"`{key}`"} = ' \
                               f'{value if isinstance(value, (int, float, bool)) or value is None else self._handle_value(value)} ' \
                               f'AND '
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
    def _handle_update_batch(items: Mapping[str, list], where: Mapping[str, list]):
        if not items or not where:
            raise LengthError("错误的键长度")
        items_order = [key for key in items.keys()] + [value for value in where.keys()]   # 这里是后续键的顺序，避免顺序异常
        key_length = set(map(lambda x: len(x), items.values()))
        if len(key_length) != 1 or len(set(map(lambda x: len(x), where.values()))) != 1:
            raise LengthError("传入的数据长度不一致")
        set_field = ", ".join([f"{key}=%s" for key in items_order if key in items])
        where_field = " AND ".join([f"{key}=%s" for key in items_order if key in where])
        value_field = []
        for ind in range(key_length.pop()):  # 依次提取每个位置的数据
            value = []
            for key in items_order:
                if key in items:
                    value.append(items[key][ind])
                if key in where:
                    value.append(where[key][ind])
            value_field.append(tuple(value))
        return set_field, where_field, value_field

    @staticmethod
    def _handle_items_type(items: List[dict]) -> Dict[str, list]:
        base_dict = {}
        order_key = []  # 记录第一次条件的键 后续的条件都要用这个顺序 避免顺序异常对应不上
        first = True   # 第一次需要确定所有的键 后续要是对应不上或者缺少键则抛出异常
        for item in items:
            if first:
                for key, value in item.items():
                    base_dict[key] = [value]
                    order_key.append(key)
                first = False
            else:
                if len(base_dict) != len(item):
                    raise LengthError("字段长度及所占用的字符名得一致")
                # for key in base_dict.keys():
                for key in order_key:
                    base_dict[key].append(item[key])
        return base_dict

    @staticmethod
    def _handle_batch(items: Mapping[str, list]):
        """
        批量操作的拼接 格式为 {"A": [1, 2, 3], "B": [6, 7, 8]}
        --> A, B    (1, 6), (2, 7), (3, 8)
        """
        if not items:
            raise LengthError("没有输入有效数据,传入了空数据")
        # 第一步，校验value的长度是否一致
        key_length = set(map(lambda x: len(x), items.values()))
        if len(key_length) != 1:
            raise LengthError("传入的值长度不一致")
        key_order = items.keys()   # 后续将用这个的顺序保证后续值的顺序一致
        value_list = []
        for ind in range(key_length.pop()):  # 依次提取每个位置的数据
            value = []
            for key in key_order:
                value.append(items[key][ind])
            value_list.append(tuple(value))
        new_key = []
        value_field = []
        for key in key_order:
            new_key.append(key if key.upper() not in MysqlKeywordsList else f"`{key}`")
            value_field.append("%s")
        return f'({", ".join(new_key)})', f"({', '.join(value_field)})", value_list

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
    base = SqlString("b_longtail")
    # s, v = base.insert_batch({"comment": [1, 2, 3], "B": [2, 3, 4]})
    # print("s-->", s, '    v--->', v)
    # s, v = base.insert_batch({"comment": [1, 2, 3], "B": [2, 3, 4]}, duplicate='ignore')
    # print("s-->", s, '    v--->', v)
    # s, v = base.insert_batch({"comment": [1, 2, 3], "B": [2, 3, 4]}, duplicate='update', update_field=["comment"])
    # print("s-->", s, '    v--->', v)
    # s, v = base.update_batch({"comment": [1, 2, 3], "B": [2, 3, 4]}, {"C": ["a", "b", "c"]})
    # print("s-->", s, '    v--->', v)
    # s, v = base.update_batch({"comment": [1, 2, 3], "B": [2, 3, 4]}, {"C": ["a", "b", "c"], "D": ["x", "y", "z"]})
    # print("s-->", s, '    v--->', v)
