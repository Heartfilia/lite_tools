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

from lite_tools.tools.core.lite_ua import get_ua
from lite_tools.tools.time.lite_time import get_time
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_parser import try_get
from lite_tools.tools.core.lite_string import color_string


@try_catch(log="本功能需要网络或者页面数据获取模式变更,和当前网络也有关系,可以重试一下")
def blog_rank():
    resp = requests.get('https://weibo.com/ajax/statuses/hot_band', headers={"user-agent": get_ua()}, timeout=5)
    data = resp.json()
    parse_blog(data)


def parse_blog(data):
    tb_wb = PrettyTable(["序号", "标签", "时间", "热度值", "详情"])
    tb_wb.align["详情"] = "l"
    band_list = try_get(data, 'data.band_list', [])
    hot_gov = try_get(data, 'data.hotgov')
    if hot_gov and isinstance(hot_gov, dict):
        hot_gov = [hot_gov]
    if hot_gov and isinstance(hot_gov, list):
        for item in hot_gov:
            tb_wb.add_row([
                color_string("-", "yellow"),
                get_wb_tag(item.get('icon_desc')),
                "置顶",
                "-",
                item.get('word')
            ])
    for ind, item in enumerate(band_list):
        tb_wb.add_row([
            color_string(str(ind+1), "cyan"),
            get_wb_tag(item.get('label_name')),
            get_time(goal=item.get('onboard_time'), fmt="%H:%M"),
            item.get('num', 0),
            item.get('word')
        ])
    print(tb_wb)


def get_wb_tag(icon):
    if icon == "热":
        return color_string("热", "yellow")
    elif icon == "新":
        return color_string("新", "green")
    elif icon == "爆":
        return color_string("爆", "red")
    elif icon == "沸":
        return color_string("沸", "purple")
    return " "
