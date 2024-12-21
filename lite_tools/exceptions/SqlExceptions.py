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


class NeedPoolOrConfig(Exception):
    def __init__(self):
        pass


class DuplicateEntryException(Exception):
    def __init__(self):
        pass


class IterNotNeedRun(Exception):
    def __init__(self):
        pass


class NotSupportType(Exception):
    def __init__(self):
        self.error = "不支持的类型"

    def __str__(self):
        return self.error


class LengthError(Exception):
    pass


class EmptyConfigException(Exception):
    pass


class KeyFieldNeedError(Exception):
    def __init__(self, key: str):
        self.error = f"缺少关键的字段: {key}"

    def __str__(self):
        return self.error
