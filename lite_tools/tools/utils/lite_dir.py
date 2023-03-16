# -*- coding: utf-8 -*-
# @Author  : Lodge
import os
import sys
import time


def get_base_root() -> str:
    """目前兼容win/linux、、、mac不确定"""
    if sys.platform == "win32":
        user_name = os.environ['username']
        return f"C:\\Users\\{user_name}"
    elif sys.platform == "linux":
        user_name = os.environ.get('USER')
        if user_name:
            if user_name == "root":
                return "/root"
            else:
                return "/home/" + user_name
        else:
            return "/root"
    elif sys.platform == "darwin":
        # mac的适配不一定正确
        return "/Users/" + os.environ['USER']
    else:
        raise Exception("不支持的平台")


def lite_tools_dir() -> str:
    """
    检查缓存目录 如果不存在就需要创建
    :return str: 返回缓存的目录路径
    """
    base_path = get_base_root()
    lite_path: str = os.path.join(base_path, '.lite-tools')
    if not os.path.exists(lite_path):
        os.makedirs(lite_path)
    return lite_path


def get_file_modify_time(file_path: str) -> str:
    """
    获取文件的修改时间
    :param file_path: 文件路径
    :return : 返回格式化的时间
    """
    t = os.path.getmtime(file_path)
    return _time_stamp_to_time(t)


def _time_stamp_to_time(timestamp: float) -> str:
    """因为太底层的包我们不建议引用已经实现的get_time方法"""
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
