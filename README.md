# lite_tools


![](https://img.shields.io/badge/python-3.6-brightgreen)
![](https://img.shields.io/github/watchers/Heartfilia/lite_tools?style=social)
![](https://img.shields.io/github/stars/Heartfilia/lite_tools?style=social)
![](https://img.shields.io/github/forks/Heartfilia/lite_tools?style=social)


### 项目说明
```
等彩票 天气 的展示和采集问题弄完了后 就要停一段时间了 要学习下其它语言了 这工具先停止更新 预计规划的时间模块没有搞完的有空随缘更新一下
本项目基础功能只是封装了 - python**自带包**的功能 
-- loguru(打印日志的)
-- 1.0.0以下均为beta版本(就是为了试错 改bug的)
补充版功能依赖第三方包

```
```
python version:
    3.6+   // 因为使用了f_string
requirements :
    loguru
extral_requirements:
    datetime
    reportlab
    Pillow
```

### Installation

```bash
# 安装
【普通版】cmd/bash >> pip install --upgrade lite-tools        # 有的人的pip是pip3 一般的功能用这些就够了
---------------- 下面两个还没有正式启用 --------------
【文件版】cmd/bash >> pip install --upgrade lite-tools[file]  # 只增加了文件处理模块
【日历版】cmd/bash >> pip install --upgrade lite-tools[date]  # 只增加了文件处理模块
【补充版】cmd/bash >> pip install --upgrade lite-tools[all]   # 包含上面所有功能
```

### 命令行指令
```bash
lite-tools [-h]   # 可以获取帮助 我这里就不展示更多了
lite-tools fish   # 即可获取摸鱼日历
lite-tools ball   # 彩票数据 - 暂时没有弄好
lite-tools news   # 获取当日新闻 可以跟 -h 查看更多操作
lite-tools today  # 即可获取当天黄历 后面加 history 可以获取往年今日
lite-tools trans -i 输入文件 [-o 输出文件路径]  # 这里 -m pdf 省略了 默认转pdf 
lite-tools weather # 默认本地 后面直接跟地点获取指定地点
```


### Interface

```bash
get_time()         # 时间操作 示例见demo.py
get_ua()           # 获取随机ua 
time_count         # 时间统计装饰器

# ==============下面是推荐使用的功能===================
try_get()          # 字典或者json串操作
try_key()          # 获取字典里键对应的值们 或者值对应的键们 --> 列表
# =================================
get_md5()          # 用md5加密 直接传入字符串就可以了 默认输出十六进制、可选二进制 也可选择输出大写
get_sha()          # 用sha加密 默认mode=256 可以选择其它加密模式
get_sha3()         # 用sha3加密 默认mode=256
get_b64e()         # 用baseXX加密 默认mode=64 可以输出字节串
get_b64d()         # 用baseXX解密 默认mode=64

# ==================================
# 新增异常捕获装饰器 同时支持异步函数的捕获
@try_catch    # 普通的捕获 输出为单条记录
def test(): ...

# 下面扩号里面得参数可以混用 不过日志等级log>catch 如果设置了log=False那么catch不起作用
try_catch(log=False)   # 普通捕获 不输出任何异常报错 默认是True
try_catch(catch=True)  # 栈捕获   可以输出详细的报错栈信息 默认是False
try_catch(default="xxx")   # 可以给定默认获取了异常后返回得默认值 默认返回None

# ===================================
clean_string("今天😄嘿 嘿,活活《拉拉\n嘿嘿.", mode="xufpPs", ignore=".") -->今天嘿嘿活活拉拉嘿嘿.

math_string("x^2 + y^5 = z")       --> x² + y⁵ = z
math_string("2H_2 + O_2 = 2H_2O")  --> 2H₂ + O₂ = 2H₂O

# Example in 'demo.py'  ||  示例见demo.py
```

```bash
# 临时新增下面功能
@match_case      # 这是一个装饰器 修改自 the EdgeDB open source project.
def test(): ...  # 这里的试用我会在demo中详细介绍 大体就是实现match_case的功能

color_string(string, "红")  # 这种就只修改字体颜色 修改整句

# 字典参数也是有详细介绍 反正就是可以自定义字体颜色 背景颜色 显示模式 输出字体宽度  键也可以简写，值也可以简写，可以中文，可以英文，可以数字
color_string(string, {"font": "黄", "background": "b", "v": "b", "length": 10})  # 这种
# 新增颜色方案 多种颜色混合写法就这么简单
color_string("<red>今天</red>，我新增了一个<yellow>颜色</yellow>方案，让<blue>color string</blue>使用更加<green>方便.</green>")

sql_obj = SqlString("table_name")   # 这是个类 只负责sql拼接的 目前只弄了插入，更新，(delete)删除的操作，详细操作后续介绍
sql_obj.insert({})
sql_obj.update({})
sql_obj.update_many([])  # 这里还没有做好 但是知道的是传入的是列表 毕竟要多条数据一起拼接嘛
sql_obj.delete(where={})
```


##### TODO（）

```text
_lib_file_jar.py --> 一些文件转换的操作(以后再说 -- 接口也是后续铺设)

# 下面的争取在0.5.0版本都修复或者优化
get_data  --> 有什么功能还要考虑一下 -- 还没有开始写
get_time  --> 这里需要重构一下--优化细节 增加自动匹配功能(以后再说)

# 需要新增功能 (下面功能实现了 但是需要测试 目前没有到1.0版本都算是beta版本)
# ===== 目前字符串处理已经优化 速度变快了 但是还是需要测试..... ========
clean_string   --> 清理字符串("\x"  "\u"  标点  emoji)  -> 目前只设置这四个清理功能 默认全部清理
预设值clean_string(string, mode="xuf")  # 意思就是  
参数可选值:
mode清除模式：
    "a"：实现下面所有功能
    "x"：\\x开头的符号 - 
    "u": \\u转义报错的符号 还有空白字符 - 
    "U": 在win上有字符linux上是空的字符 - 
    "p": 英文标点(含空格) - 
    "P": 中文标点 - 
    "e": emoji - 
    "s": 常用特殊符号 如'\\t' '\\n' 不包含空格 - 
    "f": 全角字符  -- 
    "r": 预留字符显示为 ֌这样的 -
ignore忽略字符:
	忽略掉不用处理的字符 如:
	a = "你好，牛逼啊（这个东西）"
	b = clean_string(a, "P", "（）")
b ====> "你好牛逼啊（这个东西）"
```


更多见 [demo.py](https://github.com/Heartfilia/lite_tools/tree/master/demo)