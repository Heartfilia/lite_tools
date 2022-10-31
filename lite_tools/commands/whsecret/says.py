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
目前只弄兽音 其他的不弄了 算法来源是 http://hi.pcmoe.net/roar.html 然后改编成python的
"""
from lite_tools.commands.whsecret.bearsay import roar_decode, roar_encode
from lite_tools.tools.utils.lite_table import get_terminal_long


def check_say_mode(string: str) -> int:
    """
    return 0: 这里是需要加密的
    return 1: 这里是需要解密的
    """
    base_str = set(string)
    for each in base_str:
        if each not in ["嗷", "呜", "啊", "~"]:
            return 0
    return 1


def cmd_say():
    while True:
        try:
            key = input("说>>> ")
        except KeyboardInterrupt:
            break
        else:
            if not key or len(key) < 4 or key in ['quit()', 'exit()']:
                break
            mode = check_say_mode(key)
            if mode == 0:
                s = roar_encode(key)   # 加密
                print(f"输出: {s}")
            else:
                s = roar_decode(key)   # 解密
                print(f"翻译: {s}")
            print(get_terminal_long() * "-")
