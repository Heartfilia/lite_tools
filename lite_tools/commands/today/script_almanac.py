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

import urllib3
import requests
from lxml import etree
from prettytable import PrettyTable

from lite_tools.tools.core.lite_ua import get_ua
from lite_tools.tools.time.lite_time import get_time
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_parser import try_get
from lite_tools.tools.core.lite_string import color_string, CleanString
from lite_tools.commands.today.today_utils import check_cache
urllib3.disable_warnings()
clean_string = CleanString(mode="s")


@try_catch(log="本功能为在线功能,需要网络。如有网络不要频繁请求，[如果网页数据版式有改动,这样的话这个功能暂时就废了需要修复]")
def print_today():
    """
    关于假期:如果假期是未发生的,那么将会是<黄色>标注,假如是正在假期间,将会是<绿色>标注,其次无颜色标注
    """
    html_text = get_date_web("almanac")
    html_obj = etree.HTML(html_text)
    print(color_string("【假期】还不到的假期显示<<yellow>黄色</yellow>>，正在假期中显示<<green>绿色</green>>，已经过了的假期<无色>"))
    parse_html_holiday(html_obj)   # 解析假期
    print(color_string("【今日】数据来源互联网,<red>仅供参考</red>,请不要随意迷信~"))
    parse_html_today(html_obj)     # 解析今天的运势


@try_catch(log="本功能为在线功能,需要网络。如有网络不要频繁请求，[如果网页数据版式有改动,这样的话这个功能暂时就废了需要修复]")
def print_today_history():
    """
    https://baike.baidu.com/cms/home/eventsOnHistory/01.json  只需要改月份
    """
    print("数据获取中...", end="")
    time_fmt = get_time(fmt="%Y-%m-%d")
    html_json = get_wiki_info("history", time_fmt)
    parse_history_json(html_json, time_fmt)


def parse_history_json(html_json: dict, time_fmt: str):
    base_string = color_string("【历史今日】数据来源--百度百科")
    today_date = time_fmt.split('-')
    month = today_date[1]
    month_day = "".join(today_date[1:])
    today_list = try_get(html_json, f'{month}.{month_day}', [])
    history_table = PrettyTable(["年份", f"今日是:{time_fmt},历史今日事件有"])
    history_table.align[f"今日是:{time_fmt},历史今日事件有"] = "l"    # 内容左对齐
    for each_year in today_list:
        history_table.add_row([clean_string.get(each_year.get('year')), clean_html_tag(each_year.get('title'))])
    print(f"\r{base_string}   ")
    print(history_table)


def clean_html_tag(html):
    obj = etree.HTML(html)
    return clean_string.get("".join(obj.xpath('//text()')))


@check_cache
def get_wiki_info(mode: str = "history", time_fmt: str = "") -> dict:
    _ = mode
    month = time_fmt.split('-')[1]
    resp = requests.get(
        f'https://baike.baidu.com/cms/home/eventsOnHistory/{month}.json',
        headers={'user-agent': get_ua()},
        timeout=5)
    return resp.json()


@check_cache
def get_date_web(mode: str = "almanac") -> str:
    _ = mode
    resp = requests.get('https://www.wannianli123.com/', headers={'user-agent': get_ua()}, timeout=5)
    # http://www.wannianli.cn/    竟然倒闭了这个网站
    # https://www.wannianli123.com/
    return resp.text


def parse_html_today(html: etree.HTML):
    pt_today = PrettyTable(
        [color_string("运势", **{"v": "b", "f": "b"}),
         color_string(" 详 ", **{"v": "b", "f": "b"})])
    pt_today.junction_char = "-"
    pt_today.vertical_char = " "

    tables = html.xpath('//div[@class="detail"]/div[@class="items"]/table/tbody/tr')
    for table in tables:
        th = "".join(table.xpath('./td[1]/text()'))
        td = ";".join(table.xpath('./td[2]/span/text()') or table.xpath('./td[2]/p/text()'))
        pt_today.add_row([th, td])

    yi = ",".join(html.xpath('//div[@class="detail"]/div[@class="yiji"]/div[1]/div[2]/span/text()'))
    pt_today.add_row([color_string("<red>宜</red>"), color_string(f"<red>{yi}</red>")])
    ji = ",".join(html.xpath('//div[@class="detail"]/div[@class="yiji"]/div[2]/div[2]/span/text()'))
    pt_today.add_row([color_string("<green>忌</green>"), color_string(f"<green>{ji}</green>")])
    print(pt_today)


def parse_html_holiday(html: etree.HTML):
    year = time.localtime().tm_year
    pt_holiday = PrettyTable([
        color_string(f"{year}年节日", **{"v": "b", "f": "b"}),
        color_string("放假时间", **{"v": "b", "f": "b"}),
        color_string("调休日期", **{"v": "b", "f": "b"}),
        color_string("放假天数", **{"v": "b", "f": "b"})]
    )
    # pt_holiday.set_style(pt.PLAIN_COLUMNS)
    pt_holiday.junction_char = "-"
    pt_holiday.vertical_char = " "
    tables = html.xpath('//div[@id="jiari"]/div/table/tbody/tr')
    for tr in tables:
        name = "".join(tr.xpath('./td[1]/text()')).strip()
        holiday_range = "".join(tr.xpath('./td[2]/text()')).strip()
        _need_color = _holiday_judge_range(holiday_range)
        make_up_days = "".join(tr.xpath('./td[3]/text()')).strip().replace(' ', "、")
        holiday_days = "".join(tr.xpath('./td[4]/text()')).strip()
        if _need_color:
            name = color_string(f"<{_need_color}>{name}</{_need_color}>")
            holiday_range = color_string(f"<{_need_color}>{holiday_range}</{_need_color}>")
            make_up_days = color_string(f"<{_need_color}>{make_up_days}</{_need_color}>")
            holiday_days = color_string(f"<{_need_color}>{holiday_days}</{_need_color}>")
        pt_holiday.add_row([name, holiday_range, make_up_days, holiday_days])
    print(pt_holiday)


def _get_time_ts(string: str) -> float:
    """
    通过传入的字符串获取时间戳
    """
    year = time.localtime().tm_year
    month = re.search(r"(\d+)月", string).group(1)
    day = re.search(r"(\d+)日", string).group(1)
    if month == "12" and day == "31":  # 元旦那天需要调整
        year -= 1
    return time.mktime(time.strptime(f"{year}-{month:>02}-{day:>02}", "%Y-%m-%d"))


def _holiday_judge_range(chinese_time_range: str):
    """
    为假期来判断当前时间是否在某个时间段内
    返回需要装饰的颜色
    """
    time_range = [_get_time_ts(each) for each in chinese_time_range.replace("~", "-").split("-")]
    time_start = min(time_range)
    time_end = max(time_range) + 86399    # 需要补充一下白天的时间
    now_time = time.time()
    if now_time < time_start:
        return "yellow"
    elif time_start < now_time < time_end:
        return "green"
    elif now_time > time_end:
        return ""
    else:
        return ""


if __name__ == '__main__':
    print_today()
