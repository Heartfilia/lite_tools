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
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_parser import try_get
from lite_tools.tools.core.lite_string import color_string

_WEIBO_HOT_SEARCH_URL = "https://weibo.com/ajax/side/hotSearch"
_WEIBO_HOT_REFERER = "https://weibo.com/hot/search"


@try_catch(log="本功能需要网络或者页面数据获取模式变更,和当前网络也有关系,可以重试一下")
def blog_rank():
    headers = {
        "user-agent": get_ua("desktop", "chrome"),
        "referer": _WEIBO_HOT_REFERER,
        "accept": "application/json, text/plain, */*",
    }
    resp = requests.get(_WEIBO_HOT_SEARCH_URL, headers=headers, timeout=8)
    resp.raise_for_status()
    data = resp.json()
    if try_get(data, "ok") != 1:
        raise ValueError("微博热搜接口返回异常")
    parse_blog(data)


def parse_blog(data):
    tb_wb = PrettyTable(["序号", "标签", "状态", "热度值", "详情"])
    tb_wb.align["详情"] = "l"
    real_time_list = try_get(data, 'data.realtime', [])
    hot_gov_list = try_get(data, 'data.hotgovs', [])

    if hot_gov_list and isinstance(hot_gov_list, dict):
        hot_gov_list = [hot_gov_list]
    if hot_gov_list and isinstance(hot_gov_list, list):
        for item in hot_gov_list:
            tb_wb.add_row([
                color_string("-", "yellow"),
                get_wb_tag(item.get('icon_desc') or item.get('small_icon_desc')),
                "置顶",
                "-",
                item.get('note') or item.get('word') or item.get('name', '')
            ])

    for ind, item in enumerate(real_time_list):
        hot_num = item.get('num', 0) or "-"
        status_text = get_wb_status(item)
        tb_wb.add_row([
            color_string(str(ind+1), "cyan"),
            get_wb_tag(item.get('label_name') or item.get('icon_desc') or item.get('small_icon_desc')),
            status_text,
            hot_num,
            item.get('note') or item.get('word') or item.get('word_scheme', '')
        ])
    print(tb_wb)


def get_wb_status(item):
    rank = item.get("realpos") or item.get("rank")
    if isinstance(rank, int) and rank > 0:
        return f"#{rank}"
    if item.get("is_ad"):
        return "广告"
    return "实时"


def get_wb_tag(icon):
    if icon == "热":
        return color_string("热", "yellow")
    elif icon == "新":
        return color_string("新", "green")
    elif icon == "爆":
        return color_string("爆", "red")
    elif icon == "沸":
        return color_string("沸", "purple")
    elif icon == "重磅":
        return color_string("磅", "cyan")
    return " "


if __name__ == "__main__":
    blog_rank()
