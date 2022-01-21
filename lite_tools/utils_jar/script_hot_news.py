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
import time

try:
    import urllib3
    import requests
    from lxml import etree
    from prettytable import PrettyTable
except ImportError:
    raise ImportError

from lite_tools.lib_jar.lib_ua import get_ua
from lite_tools.lib_jar.lib_time import get_time
from lite_tools.lib_jar.lib_try import try_catch
from lite_tools.lib_jar.lib_dict_parser import try_get
urllib3.disable_warnings()


session = requests.Session()


@try_catch(log="本功能为在线功能,需要网络。如有网络不要频繁请求，[如果网页数据版式有改动,这样的话这个功能暂时就废了需要修复]")
def print_hot_news():
    print("数据采集中...", end="")
    set_cookie()
    bjh_01 = get_html_from_qq()
    if bjh_01:
        flag = parse_bjh_article(bjh_01)
        if flag:
            return
    bjh_02 = get_html_from_bjh_02()
    if bjh_02:
        flag = parse_bjh_dt(bjh_01)
        if flag:
            return

    # 这一组是请求澎湃新闻的 如果上面那两组没有获取到 就从这里获取
    html = get_html_from_paper()
    parse_html_paper(html)


def set_cookie():
    session.get(
        'https://author.baidu.com/home?from=bjh_article&app_id=1681307856424533', headers={"user-agent": get_ua()}
    )


@try_catch
def get_html_from_qq():
    """
    https://view.inews.qq.com/media/21167905?tbkt=D&uid=  # 这里基本是凌晨1点左右更新
    """
    return get_item_from_bjh("22zyV-F12BRCAu5uXhboFg")    # 这个号主牛更新快


def parse_bjh_article(data):
    """
    这里是从 文章 里面获取内容
    """
    time_struct = time.localtime()
    year = time_struct.tm_year
    month = time_struct.tm_mon
    day = time_struct.tm_mday
    for item in try_get(data, 'data.list', []):
        title = try_get(item, 'itemData.title', '')
        if "每日" in title and f"{year}年{month}月{day}日" in title:
            url = try_get(item, 'itemData.url')
            flag = get_bjh_article_detail(url)
            return flag


def get_bjh_article_detail(url):
    """
    获取百家号的详情信息
    """
    print(url)
    resp = session.get(url, headers={"user-agent": get_ua()})
    html = resp.text
    print(html)
    html_obj = etree.HTML(html)
    title = "".join(html_obj.xpath('//title/text()'))
    if not title:
        return
    bjh_tb = PrettyTable([title])
    bjh_tb.align[title] = "l"
    judge_list = []
    for each_info in html_obj.xpath(
            '//div[@class="app-module_leftSection_EaCvy"]/div[1]/div[contains(@class, "textWrap")][position()>1]'):
        each = "".join(each_info.xpath('./p[@data-from-paste="1"]/text()'))
        judge_list.append(each)
        bjh_tb.add_row([each])
    if judge_list:
        print(bjh_tb)
        return "ok"


@try_catch
def get_html_from_bjh_02():
    """
    https://author.baidu.com/home?from=bjh_article&app_id=1681307856424533   # 这里是走动态 但是更新频率低 基本要10点
    """
    return get_item_from_bjh("9uCLchoe4keqLUvD0WrDYw", "dynamic")


def parse_bjh_dt(item):
    """
    这里是从 动态 获取内容
    """
    return "ok"


def get_item_from_bjh(uk, tab="article"):
    url = "https://mbd.baidu.com/webpage"
    params = {
        "tab": tab,
        "num": 10,
        "uk": uk,  # uid
        "source": "pc",
        "type": "newhome",
        "action": "dynamic",
        "format": "json",
        "Tenger-Mhor": get_time()
    }
    resp = session.get(url, params=params, headers={"user-agent": get_ua()}, verify=False)
    return resp.json()


def get_html_from_paper():
    """
    这里是一直有数据的 但是数据量较少 作为最后方案
    """
    resp = requests.get('https://www.thepaper.cn/', headers={"user-agent": get_ua()}, verify=False)
    return resp.text


def parse_html_paper(html):
    obj = etree.HTML(html)
    item_list = obj.xpath('//ul[@id="listhot0"]/li/a/text()')
    pt_news = PrettyTable(["序号", "近日热闻"])
    for ind, text in enumerate(item_list):
        pt_news.add_row([ind+1, text.strip("\n ")])
    print("\r【热闻】来源于澎湃新闻网近一日数据 ")
    pt_news.align["近日热闻"] = "l"  # 内容左对齐
    print(pt_news)


if __name__ == "__main__":
    print_hot_news()
