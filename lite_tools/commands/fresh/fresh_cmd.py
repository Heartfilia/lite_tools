import sys

from loguru import logger


def _print_fresh_base():
    """
    打印关于天气的一些操作
    """
    base_info = "lite_tools fresh <options>\n\n"
    base_info += "基于联网更新本地缓存操作:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help      展示帮助并退出，目前只有如下操作\n  "
    base_info += "ua, useragent   更新ua库资源,属于联网更新我在维护ua库\n  "
    base_info += "dict            更新dict库的资源,这里是手动更新,方便lite-tools dict使用\n  "
    print(base_info)


def fresh_cmdline(args: tuple):
    if len(args) == 1 or args[1] in ["-h", "--help"]:
        _print_fresh_base()
    elif isinstance(args[1], str) and args[1].lower() in ["ua", "useragent"]:
        try:
            from lite_tools.commands.fresh.useragent import fresh_useragent
        except ImportError:
            logger.warning("fresh 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
            sys.exit(0)
        else:
            fresh_useragent()
    elif isinstance(args[1], str) and args[1].lower() in ["dict"]:
        try:
            from lite_tools.commands.fresh.dictionary import fresh_dictionary
        except ImportError:
            logger.warning("fresh 需要安装额外的包 <bash>>> pip install --upgrade lite-tools[net]")
            sys.exit(0)
        else:
            fresh_dictionary()
