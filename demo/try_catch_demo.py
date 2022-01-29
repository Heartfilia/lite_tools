# -*- coding: utf-8 -*-
from lite_tools import try_catch


# try_catch 适用于单一的功能判断的异常捕获 不建议被装饰的函数里面再写循环之类的:成功返回结果 失败返回None
# try_catch 默认是打印日志的
# try_catch(log=False)  则不打印日志

# async_try_catch  这个没有参数可以选择,异常捕获不确定是否会有什么问题，还需要发现


@try_catch
def start_run(n):
    # 这里面正常处理即可 如果报错异常直接返回的None 所以不建议任何地方都用这个处理 如果明确返回值也有可能是None的就别这里处理了
    if n < 5:
        raise TimeoutError
    return n


def circle_test():
    for ind in range(10):
        result = start_run(ind)
        if result: return result

# 2021-07-19 17:27:12.358 | ERROR    | lite_tools.try_decorater:wrapper:25 - [start_run: TimeoutError] detail: 
# 2021-07-19 17:27:12.361 | ERROR    | lite_tools.try_decorater:wrapper:25 - [start_run: TimeoutError] detail: 
# 2021-07-19 17:27:12.368 | ERROR    | lite_tools.try_decorater:wrapper:25 - [start_run: TimeoutError] detail: 
# 2021-07-19 17:27:12.373 | ERROR    | lite_tools.try_decorater:wrapper:25 - [start_run: TimeoutError] detail: 
# 2021-07-19 17:27:12.376 | ERROR    | lite_tools.try_decorater:wrapper:25 - [start_run: TimeoutError] detail: 
# 5


if __name__ == "__main__":
    print(circle_test())
