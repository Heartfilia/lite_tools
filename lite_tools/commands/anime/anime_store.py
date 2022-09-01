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
import os
import sqlite3
from typing import Optional

from loguru import logger


def create_table(conn: sqlite3.connect):
    """
    创建表...注意 这里只记录一周一更的内容  一月一更/两更  一周多更这种后续兼容
    id         : text --> name的md5值 去重用的(*)
    platform   : text --> 视频的播放的平台(*)
    name       : text --> 视频的名称(*)
    date       : text --> 视频开播日子(后续做记录加减会根据这个,如果不到开播日子,不会做记录,不写默认已经开播) YYYY-mm-dd 格式
    hour       : integer --> 视频每天播放的小时 如 14点更新
    updateTime : integer --> 这条数据的更新时间 只记录到天的 00:00:00
    nowEpisode : integer --> 当前视频集数和本周即将更新的集数 (按周更新记录表)
    allEpisode : integer --> 视频的总集数 不写不管 只是读取时候看
    done       : real    --> 这个视频是否完结或者不再关注了 true则不再每天输出记录
    week       : integer --> 视频是每个星期几播放  取值 1->7 对应星期一 -> 星期天
    nowWeek    : integer --> 当前周在全年是第几个周
    """

    cu = conn.cursor()
    cu.execute("""CREATE TABLE IF NOT EXISTS video(
        id text NOT NULL,
        platform text NOT NULL,
        name text NOT NULL,
        date text,
        hour integer,
        updateTime integer NOT NULL,
        nowEpisode integer,
        allEpisode integer,
        done real,
        week integer,
        nowWeek integer,
       PRIMARY KEY (id)
    );""")
    logger.debug("创建了一个数据记录数据库[video].")


def connection(file_dir: str) -> sqlite3.connect:
    global conn_obj
    if not conn_obj:
        conn_obj = sqlite3.connect(file_dir)
    return conn_obj


def whether_create_sql_base(store_path: str) -> Optional[sqlite3.connect]:
    """
    判断是否有store文件,如果没有 或者 有但是表结构不是我要的,删除重建
    """
    file_dir = os.path.join(store_path, "store.db")

    if not os.path.exists(file_dir):
        # 这里为啥要把这个同样的东西写在不同的方法里面呢 因为在上面创建了 这里就会判断错误
        conn = connection(file_dir)
        create_table(conn)
    else:
        # 这里需要判断数据库结构是否是我要的 如果不是重建
        conn = connection(file_dir)
    return conn


conn_obj = None
