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
from lite_tools.commands.anime.anime_store import show_data_tables, insert_data


base_sql = SqlString("video")


@match_case
def today_information(_):
    """
    这里是输出数据流程(直接展示今天的数据) 也是默认流程
    """
    show_data_tables()  # 展示今天的数据


@today_information.register("insert")
def insert_log(_):
    insert_data()


@today_information.register("fresh")
def fresh_cache(_):
    """
    这里是刷新缓存文件 可以手动更新缓存和数据对齐  一般在 insert和update后会自动执行
    """


@today_information.register_all(["update", "update_all"])
def update_log(tag):
    """
    默认只对当星期(就是每个星期二这个意思)的内容进行管理
    可以传入update_all对所有数据进行管理
    """
    if tag == "update_all":
        show_data_tables(show_all=True)
    else:
        show_data_tables()


@today_information.register("delete")
def delete_log(_):
    pass


@today_information.register_all(["-h", "help"])
def print_tags(_):
    """
    这里是打印这里的帮助信息
    """
    base_help = "lite-tools anime 管理番剧助手~\n\n"
    base_help += "Usage: lite-tools anime <command>\n"
    base_help += "Available commands:\n"
    base_help += "  -h help         获取当前信息啦\n"
    base_help += "  insert          插入一条信息啦\n"
    base_help += "  update          展示今天的信息并修改今天的信息\n"
    base_help += "  update_all      展示全部信息并可以修改\n"
    base_help += "  delete          直接移除某一条数据\n"
    base_help += "  fresh           手动刷新库中资源缓存和本地缓存文件,默认每次update/insert都会自动执行\n\n"
    print(base_help)


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
    if len(args) > 1 and args[1] in ["insert", "update", "update_all", "delete", "-h", "help", "fresh"]:
        today_information(args[1])
    else:
        today_information(0)


if __name__ == "__main__":
    main_animation(1)
