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
import sqlite3

from lite_tools.tools.core.lite_match import match_case
from lite_tools.tools.sql.lib_mysql_string import SqlString
from lite_tools.commands.anime.anime_utils import check_cache_dir
from lite_tools.commands.anime.anime_store import whether_create_sql_base


base_sql = SqlString("video")


@match_case
def today_information(_, conn: sqlite3.connect = None, *args):
    """
    这里是输出数据流程 也是默认流程
    """
    ...


@today_information.register("insert")
def insert_log(_, conn: sqlite3.connect, *args):
    pass


@today_information.register("update")
def update_log(_, conn: sqlite3.connect, store_path: str):
    pass


@today_information.register("delete")
def delete_log(_, conn: sqlite3.connect, store_path: str):
    pass


@today_information.register_all(["-h", "help"])
def print_tags(_):
    """
    这里是打印这里的帮助信息
    """


"""
这里还有一些其它操作需要弄 比如 资源导出 一键导入啥的 以后再弄
"""


def main_animation(*args):
    """这里是主入口
    输出数据流程:
    获取路径 --> 校验缓存 -- ---- 正确 --- --- --> 输出数据(默认输出当天数据)
                    ↓ 时间不是今天               ↑  更新缓存
                    读表调整表数据后重新获取  ——--|
    输入数据流程:
    获取路径 --> 判断是否有表 ---有---> 判断是否是标准表 --是---> 添加数据(表会有一个是否追过)
                    ↓ 否                  ↓ 否                ↑
                    |-------> 创建表 <-----删除表              |
                               |————————————————————-------->|
    更新数据流程:
    获取路径 --> 输出表数据 --> 指定id --> 修改字段 --> 更新缓存文件
    """
    store_file = check_cache_dir()
    conn = whether_create_sql_base(store_file)
    if len(args) >= 1 and args[1] in ["insert", "update", "delete", "-h", "help"]:
        today_information(args[1], conn)
    else:
        today_information()


if __name__ == "__main__":
    main_animation(1, "insert")
