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
import requests
from prettytable import PrettyTable

from lite_tools.lib_jar.lib_ua import get_ua
from lite_tools.lib_jar.lib_time import get_time
from lite_tools.lib_jar.lib_try import try_catch
from lite_tools.lib_jar.lib_dict_parser import try_get
from lite_tools.lib_jar.lib_string_parser import color_string


@try_catch(log="本功能需要网络或者页面数据获取模式变更")
def blog_rank():
    resp = requests.get('https://weibo.com/ajax/statuses/hot_band', headers={"user-agent": get_ua()}, timeout=5)
    data = resp.json()
    parse_blog(data)


def parse_blog(data):
    tb_wb = PrettyTable(["序号", "时间", "热度值", "详情"])
    tb_wb.align['详情'] = "l"
    band_list = try_get(data, 'data.band_list', [])
    hot_gov = try_get(data, 'data.hotgov', {})
    if hot_gov:
        tb_wb.add_row([
            color_string("-", "yellow"),
            "置顶",
            "-",
            hot_gov.get('word')
        ])
    for ind, item in enumerate(band_list):
        tb_wb.add_row([
            color_string(str(ind+1), "cyan"),
            get_time(goal=item.get('onboard_time'), fmt="%H:%M"),
            item.get('num', 0),
            item.get('word')
        ])
    print(tb_wb)
