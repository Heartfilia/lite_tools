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
for db
"""
import os
import time
import sqlite3
from typing import Optional

from loguru import logger

from lite_tools.tools.time.lite_time import get_time
from lite_tools.tools.core.lib_hashlib import get_md5
from lite_tools.tools.sql.lib_mysql_string import SqlString
from lite_tools.exceptions.AnimeExceptions import QuitEarly
from lite_tools.commands.anime.anime_utils import input_data
from lite_tools.tools.utils.lite_dir import lite_tools_dir


base_sql = SqlString("video")
conn_obj: sqlite3.connect = None
file_dir: str = ""


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
        _id text NOT NULL,
        platform text NOT NULL,
        name text NOT NULL,
        date text,
        hour integer,
        updateTime integer NOT NULL,
        nowEpisode integer,
        allEpisode integer,
        done real,
        week integer NOT NULL,
        nowWeek integer,
       PRIMARY KEY (_id)
    );""")
    logger.debug("创建了一个数据记录数据库[video].")
    time.sleep(0.3)


def connection() -> sqlite3.connect:
    global conn_obj
    if not conn_obj:
        conn_obj = sqlite3.connect(file_dir)
    return conn_obj


def whether_create_sql_base() -> Optional[sqlite3.connect]:
    """
    判断是否有store文件,如果没有 或者 有但是表结构不是我要的,删除重建
    """
    global file_dir, file_dir

    if not file_dir:
        store_path = lite_tools_dir()
        file_dir = os.path.join(store_path, "store.db")

    if not os.path.exists(file_dir):
        # 这里为啥要把这个同样的东西写在不同的方法里面呢 因为在上面创建了 这里就会判断错误
        conn = connection()
        create_table(conn)
    else:
        # 这里需要判断数据库结构是否是我要的 如果不是重建
        conn = connection()
    return conn


def check_insert_param(input_string: str):
    if input_string in ["quit()", "exit()"]:
        raise QuitEarly


def check_video_exists(conn: sqlite3.connect, md5: str) -> bool:
    """
    校验视频是否在table中存在
    """
    sql = base_sql.exists({"_id": md5})
    cursor = conn.cursor()
    result = cursor.execute(sql)
    flag = result.fetchone()
    return bool(flag)


def insert_one_log(conn: sqlite3.connect, video: dict):
    """
    插入单条数据
    """
    sql = base_sql.insert(video)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    logger.success(f"插入了【{video.get('name')}】视频")


def insert_data():
    conn = whether_create_sql_base()
    logger.info("按条件输入需要录入的参数,带了[*]的是必填参数,可以在任意步骤输入(quit(), exit(),或者视频名称为空)退出录入模式")
    time.sleep(0.2)
    try:
        while True:
            name = input_data("视频名称[*]")  # 这里为空停止录入
            if not name:
                logger.debug("退出了录入数据模式.")
                break
            check_insert_param(name)

            _id = get_md5(name)

            in_flag = check_video_exists(conn, _id)
            if in_flag:
                logger.info(f"【{name}】视频已经存在现在跳过存储此条数据,如果需要修改请修改模式下改数据.")
                time.sleep(0.1)
                continue

            platform = input_data("播放平台[*]")
            check_insert_param(platform)

            date = input_data("开播日期(这里是给还未开播的视频用的,如果已经开播可以写-1)[*]")
            check_insert_param(date)

            hour = input_data("播放小时(24小时制 写0-23即可)")
            check_insert_param(hour)
            if hour.isdigit() and 0 <= int(hour) <= 23:  # 如果时间是正常的就显示
                hour = int(hour)
            else:
                hour = -1   # 不正常就统一到 -1 sql过滤的时候不显示今天播放的小时节点

            update_time = get_time(fmt="%Y-%m-%d", instance=int)  # 这里是校验今天是否有把数据库数据更新

            now_episode = input_data("当前集数(默认未开播)")
            check_insert_param(now_episode)
            if not now_episode or not now_episode.isdigit():
                now_episode = -1
            else:
                now_episode = int(now_episode)

            all_episode = input_data("总集数(默认持续更新)")
            check_insert_param(all_episode)
            if not all_episode:
                all_episode = -1

            done = False   # 是否看完或者不关注

            while True:
                week = input_data("每周几更新[1-7][*]")
                check_insert_param(all_episode)
                if week in ["1", "2", "3", "4", "5", "6", "7"]:
                    break
                logger.warning("week参数错误 只能从1-7里面选")

            week = int(week)

            now_week = int(get_time(fmt='%W'))   # 今天是本年第几周

            data = {
                "_id": _id, "platform": platform, "name": name, "date": date, "hour": hour,
                "updateTime": update_time, "nowEpisode": now_episode, "allEpisode": all_episode,
                "done": done, "week": week, "nowWeek": now_week
            }
            insert_one_log(conn, data)

    except QuitEarly:
        pass


if __name__ == "__main__":
    insert_data()
