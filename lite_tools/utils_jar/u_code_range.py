# 下面的字符可能不够准确 但是基本不会错

# unicode:在win和linux都不能正常显示的字符
u_range_list = [1564, 6158, 7355, 7356, 12288, 65279, 65529, 65530, 65531] + list(range(8192, 8208)) + list(range(8232, 8240)) + list(range(8287, 8293)) + list(range(8294, 8304)) + list(range(55296, 57344))

# Unicode:在win上是能显示的字符 但是在linux上显示不出来的
U_range_list = [1757, 1807, 2043, 2274, 2229, 4760, 13055, 12549, 12550] + list(range(1536, 1542)) + list(range(6170, 6175))


"""
根据Unicode5.0整理如下：

1）标准CJK文字
http://www.unicode.org/Public/UNIDATA/Unihan.html

2）全角ASCII、全角中英文标点、半宽片假名、半宽平假名、半宽韩文字母：FF00-FFEF
http://www.unicode.org/charts/PDF/UFF00.pdf

3）CJK部首补充：2E80-2EFF
http://www.unicode.org/charts/PDF/U2E80.pdf

4）CJK标点符号：3000-303F
http://www.unicode.org/charts/PDF/U3000.pdf

5）CJK笔划：31C0-31EF
http://www.unicode.org/charts/PDF/U31C0.pdf

6）康熙部首：2F00-2FDF
http://www.unicode.org/charts/PDF/U2F00.pdf

7）汉字结构描述字符：2FF0-2FFF
http://www.unicode.org/charts/PDF/U2FF0.pdf

8）注音符号：3100-312F
http://www.unicode.org/charts/PDF/U3100.pdf

9）注音符号（闽南语、客家语扩展）：31A0-31BF
http://www.unicode.org/charts/PDF/U31A0.pdf

10）日文平假名：3040-309F
http://www.unicode.org/charts/PDF/U3040.pdf

11）日文片假名：30A0-30FF
http://www.unicode.org/charts/PDF/U30A0.pdf

12）日文片假名拼音扩展：31F0-31FF
http://www.unicode.org/charts/PDF/U31F0.pdf

13）韩文拼音：AC00-D7AF
http://www.unicode.org/charts/PDF/UAC00.pdf

14）韩文字母：1100-11FF
http://www.unicode.org/charts/PDF/U1100.pdf

15）韩文兼容字母：3130-318F
http://www.unicode.org/charts/PDF/U3130.pdf

16）太玄经符号：1D300-1D35F
http://www.unicode.org/charts/PDF/U1D300.pdf

17）易经六十四卦象：4DC0-4DFF
http://www.unicode.org/charts/PDF/U4DC0.pdf

18）彝文音节：A000-A48F
http://www.unicode.org/charts/PDF/UA000.pdf

19）彝文部首：A490-A4CF
http://www.unicode.org/charts/PDF/UA490.pdf

20）盲文符号：2800-28FF
http://www.unicode.org/charts/PDF/U2800.pdf

21）CJK字母及月份：3200-32FF
http://www.unicode.org/charts/PDF/U3200.pdf

22）CJK特殊符号（日期合并）：3300-33FF
http://www.unicode.org/charts/PDF/U3300.pdf

23）装饰符号（非CJK专用）：2700-27BF
http://www.unicode.org/charts/PDF/U2700.pdf

24）杂项符号（非CJK专用）：2600-26FF
http://www.unicode.org/charts/PDF/U2600.pdf

25）中文竖排标点：FE10-FE1F
http://www.unicode.org/charts/PDF/UFE10.pdf

26）CJK兼容符号（竖排变体、下划线、顿号）：FE30-FE4F
http://www.unicode.org/charts/PDF/UFE30.pdf
"""