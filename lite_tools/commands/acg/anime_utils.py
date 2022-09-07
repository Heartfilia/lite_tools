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


week_hash = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}


def input_data(msg: str = "") -> str:
    while True:
        try:
            info = input(f"{msg + ' ' if msg else ''}>> ").strip()
            if not info and '[*]' in msg and "名称" not in msg:  # 如果标题带了[*]就是必填参数
                continue
            return info
        except KeyboardInterrupt:
            print("\t")
            break
