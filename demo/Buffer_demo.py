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
import time
from queue import Empty
import threading

# from lite_tools import Buffer
from lite_tools.tools.core.lite_cache import Buffer
from loguru import logger
"""
这里的线程由用户 启动管理 一般来说 task 是由单个线程启动 
每个Buffer的函数 都需要一个单独的线程启动 如果不启动线程 那么请把任务队列放前 消耗队列任务放后
"""


@Buffer.task(name="queue_a")   # 这里的任务放到队列 queue_a
def test1():
    # 如果想构建循环任务 这里可以
    """
    while True:
        ...
        yield xxx
    """
    for i in range(5):
        yield i


@Buffer.task    # 不写这里是默认队列   这里也可以写queue_a 这样就是多个任务往同一个队列放 多线程任务种子
def test2():
    for i in range(5, 10):
        yield i


@Buffer.worker(name="queue_a")   # 这里是消耗 queue_a 队列任务的消费者 一般这里是多个线程
def test3():
    i = Buffer.seed("queue_a")   # 从queue_a队列拿到任务种子
    logger.info(i)
    time.sleep(1)
    try:
        i = Buffer.seed()           # 不写参数这里是从默认队列拿到任务种子
        logger.info(i)              # 如果没有这个队列 那么会报 Empty异常 不会报错
    except Empty:
        pass
    logger.warning("走到了这里")


if __name__ == "__main__":
    # 不是多线程 那么就是先拿完任务再跑
    test1()
    # test2()
    test3()  # 这里面会有个拿默认队列的任务 不会报错 但是这个取任务下面的不会操作 如果要可以继续操作 可以Try出来

    # 多线程
    # threading.Thread(target=test1).start()
    # threading.Thread(target=test2).start()
    # for _ in range(3):
    #     threading.Thread(target=test3).start()


