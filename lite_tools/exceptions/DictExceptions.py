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


class TemplateFormatError(Exception):
    def __init__(self):
        self.detail = "模板格式错误"

    def __str__(self):
        return self.detail


class NotJsonException(Exception):
    def __init__(self):
        self.detail = "传入的参数不是json或者字典"

    def __str__(self):
        return self.detail


class NotGoalItemException(Exception):
    def __init__(self):
        self.detail = "不能匹配目标数据格式的数据集,可以尝试...忽略数据格式匹配"

    def __str__(self):
        return self.detail


class RetryFailedException(Exception):
    def __init__(self):
        self.error = "这里是因为重试错误"

    def __str__(self):
        return self.error
