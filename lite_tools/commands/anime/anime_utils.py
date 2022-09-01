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

from loguru import logger


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
    else:
        logger.warning("mac 还不适配")
        return ""


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
