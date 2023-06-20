import os

from loguru import logger

from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_string import color_string
from lite_tools.utils.lite_dir import lite_tools_dir


def _print_flush_base():
    """
    打印关于天气的一些操作
    """
    base_info = "lite_tools flush <options>\n\n"
    base_info += "删除指定目录的缓存信息 因为涉及删除 所以一定要跟指定目录才会操作删除:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help      展示帮助并退出，目前只有如下操作\n  "
    base_info += "ua, useragent   删除ua库资源信息\n  "
    base_info += "log, logs       删除LiteLogFile运行产生的缓存\n  "
    base_info += "today           删除today运行产生的缓存\n  "
    base_info += "acg             删除acg相关缓存记录\n  "
    print(base_info)


def flush_cmdline(args: tuple):
    if len(args) == 1 or args[1] in ["-h", "--help"]:
        _print_flush_base()
    elif isinstance(args[1], str):
        key = args[1].lower()
        if key in ["ua", "useragent"]:
            clear_lite_cache("browser")
        elif key in ["log", "logs"]:
            clear_lite_cache("logs")
        elif key in ["today"]:
            clear_lite_cache("today")
        elif key in ["acg"]:
            clear_lite_cache("acg")


def sure_check(function):
    def check(dir_name):
        print(f"您现在正在执行移除[ {color_string(dir_name, 'red')} ]目录下的缓存资源操作.内容将直接移除,是否确定操作！")
        flag = input("[y/n]>>> ")
        # 确保是yes 并且是我的缓存目录文件
        if flag.strip().lower() in ["y", "yes"] and dir_name in ["browser", "logs", "today", "acg"]:
            return function(dir_name)
    return check


@sure_check
def clear_lite_cache(dir_name):
    cache_dir = os.path.join(lite_tools_dir(), dir_name)
    if not os.path.exists(cache_dir):
        logger.debug(f"不存在该目录或已经移除")
        return
    remove_now(cache_dir)


@try_catch
def remove_now(root_path):
    """
    移除操作
    """
    for root, dirs, files in os.walk(root_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    if os.path.exists(root_path):
        os.rmdir(root_path)
        logger.success(f"已经清理了由> lite-tools <产生的缓存目录: {root_path}")
