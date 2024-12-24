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
import time

from lite_tools.logs import logger
from lite_tools.tools.core.lite_match import match_case
from lite_tools.tools.core.lite_string import color_string
from lite_tools.tools.sql.lib_mysql_string import SqlString
from lite_tools.commands.acg.anime_utils import input_data
from lite_tools.commands.acg.anime_store import (
    show_data_tables, insert_data, check_video_exists,  delete_table_log, update_store_data, fresh_table_store
)


base_sql = SqlString("video")


@match_case
def today_information(_):
    """
    这里是输出数据流程(直接展示今天的数据) 也是默认流程
    需要先读取缓存 --> 判断缓存时间 --> 展示数据  --> 否则从新查表 --> 从新生成缓存文件 --> 展示数据
    """
    show_data_tables()  # 展示今天的数据


@today_information.register("all")
def all_information(_):
    """
    展示库中全部数据信息
    """
    show_data_tables(show_all=True)


@today_information.register("insert")
def insert_log(_):
    """
    进入插入数据模式
    """
    insert_data()


@today_information.register("fresh")
def fresh_cache(_):
    """
    这里是刷新缓存文件 --> 只给日常查询数据使用意思就是把当天数据缓存下来
    这里其实也是**更新操作** 只不过是自动更新 主要更新字段为 --> updateTime  nowEpisode  nowWeek
    可以手动更新缓存和数据对齐  一般在 insert和update后会自动执行
    # 这里是校准数据的 因为数据库里面的数据不会自动变 这里是调整上面三个的字段数据的
    """
    fresh_table_store()


@today_information.register_all(["update", "update_all"])
def update_log(tag):
    """
    默认只对当星期(就是每个星期二这个意思)的内容进行管理
    可以传入update_all对所有数据进行管理
    """
    # 返回的hash_table 是用户可以选择的id对应的table里面的主键
    if tag == "update_all":
        hash_table = show_data_tables(show_all=True)
    else:
        hash_table = show_data_tables()

    if not hash_table:
        return

    while True:
        _id = input_data("需要更新的id")
        if not _id or not _id.isdigit():
            logger.debug("已经推出了更新操作 蟹蟹您 因为有你~")
            break
        if _id.isdigit() and int(_id) not in hash_table:
            logger.warning(f"您选择的id不在可以操作的范围,您可以选择的id有: {list(hash_table.keys())}")
            time.sleep(0.1)
            continue
        flag = check_video_exists(hash_table[int(_id)])
        if flag:
            update_store_data(hash_table[int(_id)])
        else:
            logger.debug("你是不是写错了啊,这里可不可以操作呢~")


@today_information.register("delete")
def delete_log(_):
    # 对全部数据进行处理
    hash_table = show_data_tables(show_all=True)
    if not hash_table:
        return
    while True:
        _id = input_data("需要删除的id")
        if not _id or not _id.isdigit():
            logger.debug("已经推出了删除操作 蟹蟹您 因为有你~")
            break
        if _id.isdigit() and int(_id) not in hash_table:
            logger.warning(f"您选择的id不在可以操作的范围,您可以选择的id有: {list(hash_table.keys())}")
            time.sleep(0.1)
            continue
        flag = check_video_exists(hash_table[int(_id)])
        if flag:
            delete_table_log(hash_table[int(_id)])
            logger.success(f"已经移除了id为: {_id} 的内容")
            del hash_table[int(_id)]
        else:
            logger.debug("改内容已经不在数据库存在 请重新尝试选择.")


@today_information.register_all(["-h", "help"])
def print_tags(_):
    """
    这里是打印这里的帮助信息
    """
    base_help = f"{color_string('lite-tools 管理番剧助手~', 'green')}\n\n"
    base_help += "Usage: lite-tools acg <command>\n\n"
    base_help += "Available commands:\n"
    base_help += "  -h help         获取当前信息啦\n"
    base_help += "  all             获取全部记录\n"
    base_help += "  <什么都不加>     获取当天记录\n"
    base_help += "  insert          插入一条信息啦\n"
    base_help += "  update          展示今天的信息并修改今天的信息\n"
    base_help += "  update_all      展示全部信息并可以修改\n"
    base_help += "  delete          直接移除某一条数据\n"
    base_help += "  fresh           手动刷新库中资源缓存和本地缓存文件,默认每次update/insert都会自动执行"
    print(base_help)


"""
这里还有一些其它操作需要弄 比如 资源导出 一键导入啥的 以后再弄
"""


def main_animation(args: list):
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
    main_animation([0, "insert"])
