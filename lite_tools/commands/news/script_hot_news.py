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
from prettytable import PrettyTable

import requests
# from lite_tools.utils.tls import requests
from lite_tools.tools.core.lite_ua import get_ua, lite_ua
from lite_tools.tools.time.lite_time import get_time
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_parser import try_get
from lite_tools.commands.news.z_sfg import my_temp_host as mh
from lite_tools.commands.news.get_global_news import get_china_news


def print_hot_news():
    print("数据采集中...", end="")
    crawl_from_china() or crawl_detail_from_paper()


# -------------------------- 下面是自己服务器流程 --- 以后会换 -------------------------------
@try_catch(log=False)
def crawl_from_my_service():
    data = requests.get(
        f'http://{mh}/news',
        headers={"user-agent": lite_ua("-news")},
        # timeout=2
        # timeout_seconds=5    # tls 专用
    )
    news_list = try_get(data.json(), 'newslist', [])
    pt_news = PrettyTable(["序号", f"{get_time(fmt=True)} 新闻如下"])
    pt_news.align[f"{get_time(fmt=True)} 新闻如下"] = "l"
    for ind, news in enumerate(news_list):
        pt_news.add_row([ind+1, news.get('title')])
    print("\r数据来源互联网 -- 半小时更新一轮资源 ")
    print(pt_news)
    return True


# -------------------------- 下面是环球时报流程 -------------------------------
@try_catch(log=False)
def crawl_from_china():
    data = get_china_news(True)
    if not data:
        return False
    gb_news = PrettyTable(["序号", "最新新闻"])
    gb_news.align["最新新闻"] = "l"  # 内容左对齐
    items = data.get('list')
    for ind, item in enumerate(items):
        title = item.get('title')
        if not title:
            continue
        gb_news.add_row([ind+1, title])
    print(f"\r【热闻】 {get_time(fmt=True)} 数据来源于环球网最新新闻资讯")
    print(gb_news)
    return True


# -------------------------- 下面是澎湃新闻流程 -------------------------------
@try_catch(log=False)
def crawl_detail_from_paper():
    """
    这里是一直有数据的 但是数据量较少 作为最后方案
    """
    data = get_data_from_paper()
    if not data:
        return
    parse_data_paper(data)


@try_catch(log=False)
def get_data_from_paper():
    """
    这里是一直有数据的 但是数据量较少 作为最后方案
    # 备选方案
    GET https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar
    """
    resp = requests.post(
        'https://api.thepaper.cn/contentapi/nodeCont/getByChannelId',
        json={
            "channelId": "",
            "excludeContIds": [23552071, 23550469, 23550755, 23551298, 23552289, 23550625, 23549993, 23552072, 23551304, 23552244, 23552146, 23550834, 23552145, 23552144, 23461919, 23543706],
            "listRecommendIds": [23550834, 23551298, 23550625, 23551304],
            "pageSize": 20,
            "startTime": ""
        },
        headers={
            "user-agent": get_ua(),
            "referer": "https://www.thepaper.cn/"
        })
    return resp.json()


@try_catch(log=False)
def parse_data_paper(data):
    items = try_get(data, 'data.list', [])
    pt_news = PrettyTable(["序号", "近日热闻"])
    for ind, item in enumerate(items):
        pt_news.add_row([ind+1, item['name'].strip("\n ")])
    pt_news.align["近日热闻"] = "l"  # 内容左对齐
    print("\r【热闻】来源于澎湃新闻网近一日数据 ")
    print(pt_news)


if __name__ == "__main__":
    print_hot_news()
