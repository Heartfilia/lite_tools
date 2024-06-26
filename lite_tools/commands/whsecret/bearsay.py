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
roar_key_arr = ["嗷", "呜", "啊", "~"]


def roar_encode(string: str) -> str:
    """这里是把正常文字转为 加密文字"""
    d = ""
    for each_char in string:
        d += f"{ord(each_char):04x}"

    b = ""
    for a, x in enumerate(d):
        c = int(x, 16) + a % 16
        if 16 <= c:
            c -= 16
        b += roar_key_arr[c // 4] + roar_key_arr[c % 4]
    result = roar_key_arr[3] + roar_key_arr[1] + roar_key_arr[0] + b + roar_key_arr[2]
    return result


def roar_decode(string: str) -> str:
    """解密部分"""
    if len(string) < 4:
        return ""
    c = roar_key_arr
    a = string[3:-1]

    d = ""
    b = a
    for e in range(0, len(a), 2):
        f = 0
        g = b[e]
        while 3 >= f and g != c[f]:
            g = b[e]
            f += 1
        h = 0
        g = b[e+1]
        while 3 >= h and g != c[h]:
            g = b[e + 1]
            h += 1

        g = 4 * f + h - (e // 2) % 16
        if 0 > g:
            g += 16
        d += f"{g:x}"
    a = ""
    for start_ind in range(0, len(d), 4):
        e = d[start_ind:start_ind+4]
        a += chr(int(e, 16))

    return a


if __name__ == '__main__':
    print(roar_encode("不要告诉我，这里东西太多了"))