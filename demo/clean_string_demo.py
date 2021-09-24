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
>>> 🙂哈哈 你好,不好.吃点《三体人》吧       哈哈
还有什么哈哈哈
>>> clean_string(need_clean_string, "xufs")   # s是清理python的转义字符 目前只清理\\a \\b \\000 \\n \\v \\t \\r \\f  # 这里是和x有重叠 不过x不清理常用的符号如前面 \\n \\v \\t \\r \\f
>>>
>>> clean_string(need_clean_string, "e")
>>>
>>> clean_string(need_clean_string, "pP")
>>>
>>> clean_string(need_clean_string, "s")
>>>
>>> clean_string(need_clean_string, "sp")
>>>
>>> clean_string(need_clean_string, "us")
>>>
"""