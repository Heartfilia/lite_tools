# -*- coding: utf-8 -*-
import re
from typing import Union, Optional

from lite_tools.utils_jar.u_sql_base_string import MysqlKeywordsList


__ALL__ = ["SqlString"]


class SqlString(object):
    """
    这里只负责拼接sql语句 不负责处理sql事务 // 还没有测试好
    这个功能主要是配合Mysql使用，当然单独使用也可以，后续拿到sql语句自己操作也可以
    """

    def __init__(self, table_name: str) -> None:
        self.table_name = table_name

    def insert(self, keys: Union[dict, list, tuple], values: list = None, ignore: bool = False) -> Optional[str]:
        """
        如果是拼接单条sql: keys传入字典 自动提取键值  values不需要传
        如果是多值拼接   : keys传入需要插入的字段命 可以列表 可以元组
                        : values传入对应的值得列表 里面放元组 如: [(1, "a"), (99, "test")]  / 也可以[1, "a"] 这样就是单条插入
        :param keys
        :param values
        :param ignore   : 是否忽略插入中的重复值之类的
        """
        if not keys:
            return None
        whether_ignore = "IGNORE " if ignore is True else ""
        base_insert = f"INSERT {whether_ignore}INTO {self.table_name}"
        key_string, value_string = self.__handle_insert_data(keys, values)
        if key_string == "":
            return None
        insert_string = f"{base_insert} {self._handle_key(key_string)} VALUES {self._handle_value(value_string)};"
        return self.__clear_string(insert_string)

    @staticmethod
    def __clear_string(string: str) -> str:
        string = re.sub("=.?[Nn]one|is.?[Nn]one", "IS NULL", string)
        string = re.sub("=.?[Tt]rue", "= 1", string)
        string = re.sub("=.?[Ff]alse", "= 0", string)
        return string.replace(",) VALUES", ") VALUES").replace(',);', ');')

    @staticmethod
    def __handle_insert_data(key, value):
        if isinstance(key, dict) and value is None:
            keys = []
            values = []
            for key, name in key.items():
                keys.append(key if key.upper() not in MysqlKeywordsList else f"`{key}`")
                values.append(name)
            return f"{tuple(keys)}", f"{tuple(values)}"
        elif isinstance(key, (list, tuple)) and not value and isinstance(key[0], dict):
            result_dict = {}
            # 第一步构造键值对
            for item in key:
                for k, v in item.items():
                    if k not in result_dict:
                        result_dict[k] = [v]
                    else:
                        result_dict[k].append(v)
            # 第二步校验值的长度是否一致
            assert len(set(map(lambda x: len(x), result_dict.values()))) == 1, f"传入的键个数为: {len(result_dict)}, 而传入的值个数不等;"
            keys = [k if k.upper() not in MysqlKeywordsList else f"`{k}`" for k in result_dict.keys()]
            # 开始拼接
            return f"{tuple(keys)}", \
                   f"{list(zip(*result_dict.values()))}"[1:-1]
        elif isinstance(key, (list, tuple)) and isinstance(value, list):
            keys = [k if k.upper() not in MysqlKeywordsList else f"`{k}`" for k in key]
            if value and isinstance(value[0], (list, tuple)):
                # 这里是批量插入
                values = ""
                for v in value:
                    assert len(key) == len(value), f"传入的键个数为: {len(key)}, 而传入的值个数为: {len(value)};"
                    values += f"{tuple(v)}, "
                values = values.rstrip(', ')
            else:
                # 这里只是兼容另外一种格式而已 推荐的还是字典
                assert len(key) == len(value), f"传入的键个数为: {len(key)}, 而传入的值个数为: {len(value)};"
                values = f"{tuple(value)}"
            return f"{tuple(keys)}", values
        else:
            raise Exception("错误的数据类型")

    def update(self, keys: dict, where: Union[dict, list, tuple, str]) -> Optional[str]:
        """
        更新数据操作, 传入需要更新的字典即可
        :param keys :  传入的更新部分的键值对啦
        :param where: 当然是筛选条件 -->
            如果用字典传入-> 相当于 "=" , 多个值会AND拼接 : True 会被替换为1 False会被替换为0 None 会被替换为NULL
            # 想实现更加精准的条件就在下面自己写 推荐==>字符串的传入方式
            --> 如果是列表传入按照 ['test<5', 'hello=1', 'tt LIKES "%VV%"'] 这样传入
            --> 如果是字符串: 'test < 5 AND hello = 1'   这样传入
        """
        if not keys or not isinstance(keys, dict) or not where:
            raise ValueError

        base_update = f"UPDATE {self.table_name} SET "
        for key, value in keys.items():
            base_update += f'{key if key.upper() not in MysqlKeywordsList else f"`{key}`"} = ' \
                           f'{value if isinstance(value, (int, float, bool)) or value is None else self._handle_update_value(value)}, '
        base_update = base_update.rstrip(', ') + " WHERE "
        if isinstance(where, dict):
            for key, value in where.items():
                base_update += f'{key if key.upper() not in MysqlKeywordsList else f"`{key}`"} = ' \
                               f'{value if isinstance(value, (int, float, bool)) or value is None else self._handle_update_value(value)} ' \
                               f'AND '
        elif isinstance(where, (list, tuple)):
            for value in where:
                base_update += f"{value} AND "
        elif isinstance(where, str):
            base_update += where
        else:
            raise Exception("错误的 where 参数类型")
        base_update = base_update.rstrip(' AND ') + ";"
        return self.__clear_string(base_update)

    @staticmethod
    def _handle_update_value(string: str):
        return repr(string).replace('"', '\\"')

    def replace(self, keys: Union[dict, list, tuple], values: list = None) -> Optional[str]:
        """
        不确定是否可以用
        """
        string = self.insert(keys, values)
        string = string.replace('INSERT', 'REPLACE')
        return string

    def delete(self, where: Union[dict, str] = None) -> Optional[str]:
        """
        这里不推荐用list,tuple数据类型 如果有多个等值条件就写dict  否则自己写字符串
        :param where: 当然是删除条件啦 不写的话就是全部删除
        """
        base_delete = f"DELETE FROM {self.table_name}"
        if not where:
            return base_delete + ";"
        base_delete += " WHERE "
        if isinstance(where, dict):
            for key, value in where.items():
                base_delete += f'{key if key.upper() not in MysqlKeywordsList else f"`{key}`"} = ' \
                               f'{value if isinstance(value, (int, float, bool)) or value is None else self._handle_update_value(value)} ' \
                               f'AND '
            base_delete = base_delete.rstrip(' AND ') + ";"
        elif isinstance(where, str):
            base_delete += where + ";"
        else:
            raise Exception("错误的 where 数据类型")
        return self.__clear_string(base_delete)

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
    def _handle_value(key_string: str) -> str:
        return key_string.replace("'", "\'").replace('"', '\\"')


if __name__ == "__main__":
    sql = SqlString('test')

    sql.insert([
        {"string": "465sdf56sdf", "num": 111},
        {"string": "416546565", "num": 123},
    ])

