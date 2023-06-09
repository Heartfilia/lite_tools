# -*- coding: utf-8 -*-
# @Author  : Lodge
import os
import sys
import time

# 获取本机有哪些磁盘分区 (windows 专用)
DIST_PART_windows = []
dir_path = None


def get_base_root() -> str:
    """目前兼容win/linux、、、mac不确定"""
    global dir_path
    if dir_path:
        # windows 专属缓存
        return dir_path
    if sys.platform == "win32":
        user_name = os.environ['username']
        temp_path = f"C:\\Users\\{user_name}"
        if not os.access(temp_path, os.W_OK | os.R_OK):
            # 这里还是尝试在C盘目录下尝试其它用户目录
            temp_path = "C:\\Users\\Administrator"
            if not os.access(temp_path, os.W_OK | os.R_OK):
                temp_path = ""
        if not temp_path:
            # 如果尝试了两个基本目录都不行就尝试其它盘符
            disks = get_windows_partial()
            if len(disks) >= 2:
                for check_path in disks[1:]:
                    if os.access(check_path, os.W_OK | os.R_OK):
                        temp_path = check_path
                        break
            else:
                temp_path = "."  # 实在不行就在当前目录创建缓存
        dir_path = temp_path
        return temp_path
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


def _scan_partial():
    """扫描windows电脑磁盘有哪些分区"""
    if sys.platform != "win32":
        return
    for num in range(67, 91):
        partial = f"{chr(num)}:"
        if os.path.isdir(partial):
            DIST_PART_windows.append(partial)


def get_windows_partial():
    """获取电脑盘符"""
    if sys.platform == "win32" and not DIST_PART_windows:
        _scan_partial()
    return DIST_PART_windows
