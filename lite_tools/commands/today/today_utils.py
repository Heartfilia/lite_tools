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
import json
from typing import Literal

from lite_tools.tools.time.lite_time import get_time
from lite_tools.utils.lite_dir import lite_tools_dir


def today_cache_dir(file_name: Literal['oil', 'almanac', 'history']) -> str:
    """获取today的文件夹路径里面的缓存处理会在下面操作"""
    today_root = os.path.join(lite_tools_dir(), 'today')
    if not os.path.exists(today_root):
        os.makedirs(today_root)

    cache_dir = os.path.join(today_root, file_name)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    return cache_dir


def check_cache(function):
    """
    这里会校验路径里面是否有缓存 然后没有会保存缓存 有会读取缓存 顺道还会清理非今日的缓存
    """
    def wrapper(mode: Literal['oil', 'almanac', 'history'], *args):
        root = today_cache_dir(mode)
        if not os.path.exists(root):
            os.makedirs(root)
        today_time = get_time(fmt="%Y%m%d")
        today_path = os.path.join(root, today_time)
        if not os.path.exists(today_path) or not os.path.getsize(today_path):
            html = function(mode, *args)
            with open(today_path, 'w', encoding='utf-8') as fp:
                if mode == 'history':
                    json.dump(html, fp)
                else:
                    fp.write(html)
        else:
            with open(today_path, 'r', encoding='utf-8') as fp:
                if mode == 'history':
                    html = json.load(fp)
                else:
                    html = fp.read()
            clear_not_today(root, today_time)
        return html
    return wrapper


def clear_not_today(path: str, name: str):
    """
    这里可以设置是否保留 或者 保留几天的数据
    """
    for file in os.listdir(path):
        if file != name:
            os.remove(os.path.join(path, file))
