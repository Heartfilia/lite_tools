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

try:
    import urllib3
    import requests
    from lxml import etree
    from typing import Tuple, Union
    from prettytable import PrettyTable
except ImportError:
    raise ImportError

from lite_tools.lib_jar.lib_ua import get_ua, lite_ua
from lite_tools.lib_jar.lib_time import get_time
from lite_tools.lib_jar.lib_try import try_catch
from lite_tools.lib_jar.lib_dict_parser import try_get
from lite_tools.news.z_sfg import my_temp_host as mh
urllib3.disable_warnings()


def print_hot_news():
    print("数据采集中...", end="")
    crawl_from_my_service() or crawl_detail_from_paper()


# -------------------------- 下面是自己服务器流程 --- 以后会换 -------------------------------
@try_catch(log=False)
def crawl_from_my_service():
    data = requests.get(f'http://{mh}/news',
                        headers={"user-agent": lite_ua("-news")})
    news_list = try_get(data.json(), 'newslist', [])
    pt_news = PrettyTable(["序号", f"{get_time(fmt=True)} 新闻如下"])
    pt_news.align[f"{get_time(fmt=True)} 新闻如下"] = "l"
    for ind, news in enumerate(news_list):
        pt_news.add_row([ind+1, news.get('title')])
    print("\r数据来源互联网 -- 每小时会更新一轮资源 ")
    print(pt_news)
    return True

# -------------------------- 下面是澎湃新闻流程 -------------------------------


@try_catch(log=False, default=False)
def crawl_detail_from_paper():
    """
    这里是一直有数据的 但是数据量较少 作为最后方案
    """
    html = get_html_from_paper()
    if not html:
        return False
    parse_html_paper(html)


@try_catch(log=False, default=False)
def get_html_from_paper():
    """
    这里是一直有数据的 但是数据量较少 作为最后方案
    """
    resp = requests.get('https://www.thepaper.cn/', headers={"user-agent": get_ua()}, verify=False)
    return resp.text


@try_catch(log=False, default=False)
def parse_html_paper(html):
    obj = etree.HTML(html)
    item_list = obj.xpath('//ul[@id="listhot0"]/li/a/text()')
    pt_news = PrettyTable(["序号", "近日热闻"])
    has_item = False
    for ind, text in enumerate(item_list):
        pt_news.add_row([ind+1, text.strip("\n ")])
        has_item = True
    if not has_item:
        return False
    pt_news.align["近日热闻"] = "l"  # 内容左对齐
    print("\r【热闻】来源于澎湃新闻网近一日数据 ")
    print(pt_news)
    return True
