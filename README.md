# lite_tools

### 项目说明
```
本项目只是封装了 - python**自带包**的功能 不过还是装了另外两个包
-- loguru(打印日志的) datetime(目前没有用到 后续会改进get_date)
-- 0.5.0以下均为beta版本(就是为了试错 改bug的)
```
```
python version:
    3.6+   // 因为使用了f_string
requirements :
    loguru
    datetime
```

### install

```bash
# 安装
cmd/bash >> pip install lite-tools   # 有的人的pip是pip3
```


### Interface

```bash
get_time()         # 时间操作 示例见demo.py
get_ua()           # 获取随机ua 
timec              # 时间统计装饰器

# ==============下面是推荐使用的功能===================
try_get()          # 字典或者json串操作
try_get_by_name()  # 获取字典里键对应的值们 或者值对应的键们 --> 列表
# =================================
get_md5()          # 用md5加密 直接传入字符串就可以了 默认输出十六进制、可选二进制 也可选择输出大写
get_sha()          # 用sha加密 默认mode=256 可以选择其它加密模式
get_sha3()         # 用sha3加密 默认mode=256
get_b64e()         # 用baseXX加密 默认mode=64 可以输出字节串
get_b64d()         # 用baseXX解密 默认mode=64

# ==================================
# 新增异常捕获装饰器 同时支持异步函数的捕获
try_catch    # 普通的捕获 输出为单条记录

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

```python
# 临时新增下面功能  本次git提交为数据保存 暂时还不打包 等后续处理好了在弄
@match_case  # 这是一个装饰器 修改自 the EdgeDB open source project.
             # 这里的试用我会在demo中详细介绍 大体就是实现match_case的功能
 

color_string(string, "红")  # 这种就只修改字体颜色
color_string(string, {"font": "黄", "background": "b", "v": "b", "length": 10})
# 字典参数也是有详细介绍 反正就是可以自定义字体颜色 背景颜色 显示模式 输出字体宽度  键也可以简写，值也可以简写，可以中文，可以英文，可以数字

SqlString()   # 这是个类 只负责sql拼接的 目前只弄了插入，更新，(delete)删除的操作，详细操作后续介绍
```


##### TODO（）

```text
_lib_file_jar.py --> 一些文件转换的操作(以后再说 -- 接口也是后续铺设)

# 下面的争取在0.5.0版本都修复或者优化
get_data  --> 有什么功能还要考虑一下 -- 还没有开始写
get_time  --> 这里需要重构一下--优化细节 增加自动匹配功能(以后再说)

# 需要新增功能 (下面功能实现了 但是需要测试 目前0.5.0以下版本都算是beta版本)
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


see `demo.py`