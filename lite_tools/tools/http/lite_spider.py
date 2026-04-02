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
from threading import Thread
from lite_tools.tools.http.models import LiteRequest


"""
最小单元轻量级小爬虫
请求
重试
解析
校验
信息统计
"""


class LiteSpider(LiteRequest, Thread):

    spider_name: str = "Spider"

    def __init__(self, thread_num: int = 1):
        if not isinstance(thread_num, int):
            raise TypeError("thread_num 需要是 int 类型")
        LiteRequest.__init__(self)
        Thread.__init__(self)
        self.thread_num = thread_num

    def _buffer_task(self):
        pass

    def run(self):
        """
        class SpiderName(LiteSpider):
            pass
        启动程序流程是:
        spider = SpiderName(10)
        spider.run()
        """
        pass
