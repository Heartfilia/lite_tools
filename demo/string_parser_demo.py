from lite_tools import clean_string


need_clean_string = "🙂哈哈 你好,不好.吃点《三体人》吧\t哈哈\n还有什么\uFFFF哈哈哈"
print(clean_string(need_clean_string))

"""
- 清理模式 可以组合使用 -> - 
"x"：\\x开头的符号 - 
"u": \\u转义报错的符号 还有空白字符 - 
"U": 在win上有字符linux上是空的字符 - 
"p": 英文标点(含空格) - 
"P": 中文标点 - 
"e": emoji - 
"s": 常用特殊符号 如'\\t' '\\n' 不包含空格 - 
"f": 全角字符  -- 
"r": 预留字符显示为 ֌这样的 -

>>> clean_string(need_clean_string)   # 默认就是清理 xuf  意思就是x:\\x开头 u:\\u开头 还有f:全角字符 
>>> 🙂哈哈 你好,不好.吃点《三体人》吧	哈哈
还有什么￿哈哈哈
>>> clean_string(need_clean_string, "xufs")   # s是清理python的转义字符 目前只清理\\a \\b \\000 \\n \\v \\t \\r \\f  # 这里是和x有重叠 不过x不清理常用的符号如前面 \\n \\v \\t \\r \\f
>>> 🙂哈哈 你好,不好.吃点《三体人》吧哈哈还有什么￿哈哈哈
>>> clean_string(need_clean_string, "e")
>>> 哈哈 你好,不好.吃点《三体人》吧	哈哈
还有什么￿哈哈哈
>>> clean_string(need_clean_string, "pP")
>>> 🙂哈哈你好不好吃点三体人吧	哈哈
还有什么￿哈哈哈
>>> clean_string(need_clean_string, "pP", ' ')   # 第三个参数是忽略的字符 可以填写多个的单个字符 
>>> 🙂哈哈 你好不好吃点三体人吧	哈哈
还有什么￿哈哈哈  
>>> clean_string(need_clean_string, "sp")
>>> 🙂哈哈你好不好吃点《三体人》吧哈哈还有什么￿哈哈哈
>>> clean_string(need_clean_string, "us")
>>> 🙂哈哈 你好,不好.吃点《三体人》吧哈哈还有什么￿哈哈哈
"""

from lite_tools import deco_clr
from loguru import logger

# deco_clr 第一个参数是传入的字符串
# 第二个参数 如果是单独的字或者数字 就是装饰字体的颜色
#           如果是字典 那么就根据字典里面的参数来自定义颜色或者其它属性
# 字典参数：
# 直接写字典传可以  用**{}传也可以
# f : font       就是字体颜色   颜色可以写中文 英文 简写 对应的输出颜色编码  不支持颜色的十六进制这种 只能用我给的默认的(要不然工程量太大 这个东西也不重要 没必要)
# b : background 背景颜色
# v : view       显示的方式     可以
# l/lenght :     输出字符串的长度
# 下面是详细的操作 不需要刻意记 用ide的时候 指着就会提示下面的东西
"""
:param string: 传入的字符串
:param args  : 参数注解如下面所示  传入非字典类型的时候 只有第一个参数起作用在字体颜色上面  -->传入字典同下操作
:param kwargs: 这里传入需要用 **{}   
:param f     : 字体颜色 -> (30, 黑色/black)(31, 红色/r/red)(32, 绿色/g/green)(33, 黄色/y/yellow)(34, 蓝色/b/blue)(35, 紫色/p/purple)(36, 青蓝色/c/cyan)(37, 白色/w/white)
                        -> (90, darkgrey)(91, lightred)(92, lightgreen)(93, lightyellow)(94, lightblue)(95, pink)(96, lightcyan)
:param b     : 背景颜色 -> (40, 黑色/black)(41, 红色/r/red)(42, 绿色/g/green)(43, 黄色/y/yellow)(44, 蓝色/b/blue)(45, 紫色/p/purple)(46, 青蓝色/c/cyan)(47, 白色/w/white)
:param v     : 显示方式 -> (0, 重置/reset)(1, 加粗/b/bold)(2, 禁止/disable)(4, 使用下划线/u/underline)(5, 闪烁/f/flash)(7, 反相/r/reverse)(8, 不可见/i/invisible)(9, 删除线/s/strikethrough)
"""
print(f"{'hello':<20}", "aaaaa")
print(deco_clr("hellow", {"f": "红", "b": "白", "v": "strikethrough", "lenght": 20}), "aaaaa")
print(deco_clr("a", {"f": "红", "b": "白", "v": "strikethrough", "l": 20}), "aaaaa")
print(deco_clr("hellow", {"f": "y", "b": "g"}), "aaaaa")
print(deco_clr("hellow", **{"f": "b", "b": "r"}), "aaaaa")
logger.info(f'{deco_clr("hellow", "红")} aaaaa')