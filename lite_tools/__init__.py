# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:50
# @Author : Lodge
name = "lite-tools"
__ALL__ = [
    "get_lan",       # 获取内网ip
    "get_wan",       # 获取外网ip
    "check_proxy",   # 校验代理是否有效
    "try_catch",     # @ 异常捕获 + 重试配置 + 回调
    "get_time",      # 时间转换 + 时间获取
    "time_range",    # 获取时间起始范围
    "time_count",    # @ 获取函数运行时间
    "get_b64e",      # 加密成 base64 有其它配置
    "get_b64d",      # 解密   base64
    "get_md5",       # 加密成 md5
    "get_sha",       # 用sha 加密  默认sha  256 有其它配置
    "get_sha3",      # 用sha3加密  默认sha3 256 有其它配置
    "get_ua",        # 获取一条随机ua 可以加参数指定浏览器或者系统
    "try_get",       # jsonPath 方式取字典值
    "try_key",       # 可根据键/值 取值/键
    "MySql",         # MySql 连接池对象
    "AioMySql",      # mysql 异步链接池
    "MySqlConfig",   # mysql -- 专属配置 可以直接用 或者  MySqlConfig.new(dict 相关配置)
    "FlattenJson",   # 把json平坦化
    # "JsJson",        # 从js里面提取json内容,这个目前不可以泛用
    "WrapJson",      # 把一个json按照指定模板折叠
    "match_case",    # 类似match case
    "clean_html",    # 提取html标签内的内容
    "CleanString",   # 清理字符串里面的特殊字符 文本不是太大可以用
    "color_string",  # 给字体加颜色
    "SqlString",     # 获取mysql的语句 太复杂不行
    "math_string",   # 没啥用，就是打印以下数学字符
    "PrettySrt",     # 优化 srt 文件的工具
    "cookie_s2d",    # cookie转换 str -> dict
    "cookie_d2s",    # cookie转换 dict -> str
    "pretty_indent",  # 美化缩进空格
    # "x_timeout",     # 这个没有弄好 就是限制函数最大运行时间的
    "Singleton",     # @ 单例
    "Buffer",        # @ 缓存队列 + 统计
    "count_lines",   # 获取文件行数
    "LiteLogFile",   # 日志文件记录到缓存区 --> 这里是偶尔记录一条那种(打点) 10000条内容缓冲区 超了从1开始记录 高频记录用 loguru
    # 下面的是js转python的操作 还没有写完 也没有弄完 还有 >>>  36进制转换等等操作
    "atob",          # ascii to bytes
    "btoa",          # bytes to ascii
    "to_string_2",  # js里面数字转2进制   (123456789).toString(2)
    "to_string_16",  # js里面数字转16进制   (123456789).toString(16)
    "to_string_36",  # js里面数字转36进制   (123456789).toString(36)
    "xor",           # 异或 同python ^  这里主要是解决精度问题
    "unsigned_right_shift",  # >>>  无符号右移  解决精度问题
    "left_shift",   # << 左移  解决精度问题
    "dec_to_bin",   # 十进制浮数转二进制数据(返回的是字符串 注意哦)  同 toString(2)
    # 下面是一些可以对外使用的一些redis操作 等http包第一版能用的时候再放出来
    "LiteRedis",     # 这个用处不大 但是可以用一个本地文件的配置文件来初始化这个对象使用 如 rd = LiteRedis("/root/config.json")
    "LiteProxy",     # 更方便的获取代理的操作 基于redis的set/list模式 默认set随机弹出 也可以切换为mode='list'滚动获取 使用方式可以使用 LiteRedis.help() 获取
    "BloomFilter",   # 基于redis的布隆过滤器
    "install",       # 实现pip install 的操作
]

# 还有一个东西不放这里了 可以这样引用
from lite_tools.tools.core.lite_ja3 import sync_ja3, aio_ja3

from lite_tools.tools.core.ip_info import get_lan, get_wan, check_proxy
from lite_tools.tools.core.lib_base64 import get_b64d, get_b64e
from lite_tools.tools.core.lite_parser import try_get, try_key, FlattenJson, JsJson, WrapJson
from lite_tools.tools.core.lib_hashlib import get_md5, get_sha, get_sha3, get_5dm  # 5dm是我自己用的不对外展示
from lite_tools.tools.time.lite_time import get_time, time_count, time_range
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_ua import get_ua
try:
    from lite_tools.tools.sql.config import MySqlConfig
    from lite_tools.tools.sql.lite_mysql import MySql, AioMySql
except ImportError:  # 这里是忽略这里面的包异常的
    pass
try:
    from lite_tools.tools.sql.lite_redis import LiteRedis, LiteProxy, BloomFilter
except ImportError:
    pass

from lite_tools.tools.sql.lib_mysql_string import SqlString
from lite_tools.tools.core.lite_match import match_case
from lite_tools.tools.core.lite_string import (
    clean_html, CleanString, color_string, math_string, PrettySrt,
    cookie_s2d, cookie_d2s, pretty_indent
)
# from lite_tools.tools.time.httpx_timeout import x_timeout
try:
    from lite_tools.tools.core.lite_cache import Singleton, Buffer, LiteCacher
except ImportError:
    pass
from lite_tools.tools.core.lite_file import count_lines, LiteLogFile

from lite_tools.tools.js import (
    atob, btoa,
    to_string_2, to_string_16, to_string_36,
    xor, unsigned_right_shift, left_shift, dec_to_bin
)
from lite_tools.utils.pip_ import install
from lite_tools.utils import VERSION


version = VERSION

__ALL__ += ["5dm"]  # 这个是给我自己用的
