from lite_tools.logs import logger


log_level = {
    "error": (10, logger.error),
    "warning": (8, logger.warning),
    "info": (6, logger.info),
    "success": (4, logger.success),
    "debug": (2, logger.debug)
}


def log(string: str, sql_string: str, string_level: str, output: bool = False, _log: bool = False) -> None:
    """
    level: (error > warning > info > success > debug)  目前只管是否要打日志 没有弄等级处理
    :param string: 需要提示的信息
    :param sql_string: 执行的sql语句
    :param string_level: 传入过来的等级
    :param output      : 默认不打印 弄这个参数主要是控制什么时候打印内容 不要一直打印 要分块打印输出数据
    :param _log        : 是否打印
    """
    if not log or not output:
        return
    level_rate, log_func = log_level.get(string_level.lower(), (0, None))
    if level_rate:
        log_func(f"{string}{'' if not sql_string else '  SQL --> '+sql_string}")
