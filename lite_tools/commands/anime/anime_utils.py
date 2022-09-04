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
import sys


def get_base_dir() -> str:
    """目前兼容win/linux、、、mac不确定"""
    if sys.platform == "win32":
        return "C:\\Users\\Administrator"
    elif sys.platform == "linux":
        user_name = os.environ['USER']
        if user_name == "root":
            return "/root"
        else:
            return "/home/" + user_name
    elif sys.platform == "darwin":
        # mac的适配不一定正确
        return "/Users/" + os.environ['USER']
    else:
        raise Exception("不支持的平台")


def check_cache_dir() -> str:
    """
    检查缓存目录 如果不存在就需要创建
    :return str: 返回缓存的目录路径
    """
    base_path = get_base_dir()
    lite_animate_path: str = os.path.join(base_path, '.lite-tools')
    if not os.path.exists(lite_animate_path):
        os.makedirs(lite_animate_path)
    return lite_animate_path


def input_data(msg: str = "") -> str:
    while True:
        try:
            info = input(f"{msg + ' ' if msg else ''}>> ").strip()
            if not info and '[*]' in msg and "名称" not in msg:  # 如果标题带了[*]就是必填参数
                continue
            return info
        except KeyboardInterrupt:
            break
