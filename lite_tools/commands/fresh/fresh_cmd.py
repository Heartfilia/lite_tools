from lite_tools.commands.fresh.useragent import fresh_useragent


def _print_fresh_base():
    """
    打印关于天气的一些操作
    """
    base_info = "lite_tools fresh [options]\n\n"
    base_info += "基于联网更新本地缓存操作:\n"
    base_info += "optional arguments:\n  "
    base_info += "-h, --help      展示帮助并退出，目前只有如下操作\n  "
    base_info += "ua, useragent   更新ua库资源,属于联网更新我在维护ua库\n  "
    print(base_info)


def fresh_cmdline(args: tuple):
    if len(args) == 1 or args[1] in ["-h", "--help"]:
        _print_fresh_base()
    elif isinstance(args[1], str) and args[1].lower() in ["ua", "useragent"]:
        fresh_useragent()
