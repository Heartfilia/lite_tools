from lite_tools.logs import logger


log_level = {
    "error": (10, logger.error),
    "warning": (8, logger.warning),
    "info": (6, logger.info),
    "success": (4, logger.success),
    "debug": (2, logger.debug)
}


def x(string: str, level: str = "debug") -> None:
    """
    level: (error > warning > info > success > debug)  目前只管是否要打日志 没有弄等级处理
    :param string: 需要提示的信息
    :param level: 传入过来的等级
    """
    if not string:
        return
    level_rate, log_func = log_level.get(level.lower(), (0, None))
    if level_rate:
        log_func(string)
