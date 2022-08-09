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


class Config:
    def __init__(
        self,
        database: str,
        host: str,
        user: str,
        password: str = "",
        port: int = 3306,
        charset: str = "utf8mb4",
        maxconnections: int = 20,
        table_name: str = None,
    ):
        """
        mysql的配置文件 这里只有默认的配置 要改其他的可以自己传pool配置
        :param database (*): database的名字
        :param host     (*): 数据的host啦
        :param user     (*): 数据库的用户
        :param password (*): 数据库的密码
        :param port  (3306): 端口
        :param charset ('utf8mb4'): 默认的字符集格式
        :param maxconnections (20): 默认的最大链接数
        :param table_name (str)   : 这个是给insert  update  delete 用的
        """
        self.database = database
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.charset = charset
        self.maxconnections = maxconnections
        self.table_name = table_name




