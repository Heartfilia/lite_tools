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
import re
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


def print_hot_news():
    print("数据采集中...", end="")
    log_info = crawl_detail_from_bjh() or crawl_detail_from_qq() or crawl_detail_from_paper()
    if not log_info:
        print("\r没有网络或者网页变更")


# -------------------------- 下面是企鹅号流程 -------------------------------


@try_catch(log=False)
def crawl_detail_from_qq():
    """
    https://view.inews.qq.com/media/21167905?tbkt=D&uid=  # 这里基本是凌晨1点左右更新
    """
    qq_json = get_item_from_qq(21167905)    # 这个号主相对更新快
    flag = parse_qq_article_list(qq_json)
    return flag


def get_item_from_qq(uid) -> dict:
    """
    21167905
    """
    resp = requests.get(
        f"https://view.inews.qq.com/share/getSubQQNewsIndex?chlid={uid}",
        headers={"user-agent": get_ua(), "referer": "https://view.inews.qq.com/"}
    )
    return resp.json()


def parse_qq_article_list(data) -> bool:
    """
    解析用户列表 判断是否有发当日新闻
    """
    news_list = data.get('newslist', [])
    if not news_list:
        return False
    for recent_news in news_list:
        _time = recent_news.get('time')   # 获取发布时间
        if get_time(fmt='%Y-%m-%d') not in _time:
            continue
        url = recent_news.get('url')
        return get_today_news_qq(url)
    return False


def get_today_news_qq(url):
    """
    从静态页面提取当日内容
    """
    try:
        resp = requests.get(url, headers={"user-agent": get_ua(), "referer": "https://view.inews.qq.com/"})
        return extract_detail_from_qq_html(resp.text)
    except Exception as err:
        _ = err
        return False


def extract_detail_from_qq_html(qq_html):
    json_data = re.search(r'(?<=<script>window.initData = )(.*)(?=;</script><script>var)', qq_html)
    if json_data:
        data = try_get(json_data.group(0), 'content.cnt_html', "")
        each_items = re.findall(r"(?<=<p>)(\d+)、(\S+?)(?=</p>)", data, re.I)
        pt_news = PrettyTable(["序号", "近日热闻"])
        print("\r【热闻】来源于互联网 ")
        for item in each_items:
            pt_news.add_row([item[0], item[1]])
        pt_news.align["近日热闻"] = "l"  # 内容左对齐
        print(pt_news)
        return True
    return False


# -------------------------- 下面是百家号流程 -------------------------------


def set_bjh_cookie():
    session = requests.Session()
    session.get(
        'https://author.baidu.com/home?from=bjh_article&app_id=1681307856424533',
        headers={"user-agent": get_ua()}
    )
    return session


@try_catch(log=False)
def crawl_detail_from_bjh():
    session = set_bjh_cookie()
    bjh_data = get_html_from_bjh_dynamic(session)
    if not bjh_data:
        return False
    return parse_bjh_dynamic(bjh_data)


@try_catch(log=False, default=False)
def get_html_from_bjh_dynamic(session):
    """
    https://author.baidu.com/home?from=bjh_article&app_id=1681307856424533   # 这里是走动态 但是更新频率低 基本要10点
    """
    url = "https://mbd.baidu.com/webpage"
    params = {
        "tab": "dynamic",
        "num": 10,
        "uk": "9uCLchoe4keqLUvD0WrDYw",  # uid
        "source": "pc",
        "type": "newhome",
        "action": "dynamic",
        "format": "json",
        "Tenger-Mhor": get_time()
    }
    resp = session.get(url, params=params, headers={"user-agent": get_ua()}, verify=False)
    return resp.json()


def parse_bjh_dynamic(data):
    """
    这里是从 动态 获取内容
    """
    time_struct = time.localtime()
    year = time_struct.tm_year
    month = time_struct.tm_mon
    day = time_struct.tm_mday
    today_date = f"{year}年{month}月{day}日"
    for item in try_get(data, 'data.list', []):
        title = try_get(item, 'itemData.origin_title', '')
        if "简报" in title and today_date[5:] in title:
            return print_bjh(title, today_date)
    return False


def print_bjh(text, today_date):
    reg_rule = f"({today_date}.*?)(?=1、)"
    detail_title = re.search(reg_rule, text, re.S)
    if detail_title:
        title = detail_title.group(0).strip()
        print("\r【热闻】来源于互联网 ")
        pt_news = PrettyTable(["序号", title])
        pt_news.align[title] = "l"
        for each_item in re.findall(r"(\d+)、(.*?。)", text, re.S):
            pt_news.add_row([each_item[0], each_item[1]])
        print(pt_news)
        return True
    return False


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
    for ind, text in enumerate(item_list):
        pt_news.add_row([ind+1, text.strip("\n ")])
    print("\r【热闻】来源于澎湃新闻网近一日数据 ")
    pt_news.align["近日热闻"] = "l"  # 内容左对齐
    print(pt_news)
    return True
