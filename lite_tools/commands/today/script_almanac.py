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

from lite_tools.tools.pure.lib_ua import get_ua
from lite_tools.tools.pure.lib_time import get_time
from lite_tools.tools.pure.lib_try import try_catch
from lite_tools.tools.pure.lib_dict_parser import try_get
from lite_tools.tools.lib_string_parser import color_string, CleanString
urllib3.disable_warnings()
clean_string = CleanString(mode="s")


@try_catch(log="本功能为在线功能,需要网络。如有网络不要频繁请求，[如果网页数据版式有改动,这样的话这个功能暂时就废了需要修复]")
def print_today():
    """
    关于假期:如果假期是未发生的,那么将会是<黄色>标注,假如是正在假期间,将会是<绿色>标注,其次无颜色标注
    """
    html_text = get_date_web()
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
    html_json = get_wiki_info(time_fmt)
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


def get_wiki_info(time_fmt: str) -> dict:
    month = time_fmt.split('-')[1]
    resp = requests.get(
        f'https://baike.baidu.com/cms/home/eventsOnHistory/{month}.json',
        headers={'user-agent': get_ua()},
        verify=False)
    return resp.json()


def get_date_web() -> str:
    resp = requests.get('https://www.wannianli.cn/', headers={'user-agent': get_ua()}, verify=False)
    return resp.text


def parse_html_today(html: etree.HTML):
    tables = html.xpath('//table/tr')
    pt_today = PrettyTable(
        [color_string("今日运势", **{"v": "b", "f": "b"}),
         color_string(tables[0].xpath('./td/text()')[-1], **{"v": "b", "f": "b"})])
    pt_today.junction_char = "-"
    pt_today.vertical_char = " "
    for tr in tables[1:]:
        th = "".join(tr.xpath('./th[1]/text()'))
        td = "".join(tr.xpath('./td')[-1].xpath('./text()'))
        if th == "【宜】":
            th = color_string(f"<green>{th}</green>")
            td = color_string(f"<green>{td}</green>")
        elif th == "【忌】":
            th = color_string(f"<red>{th}</red>")
            td = color_string(f"<red>{td}</red>")
        elif "友情提示" in th or "彭祖百忌" in th:
            continue
        pt_today.add_row([th, td])
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
    tables = html.xpath('//table/tbody/tr[@class="c-table-hihead firstRow"]/following-sibling::tr')
    for tr in tables:
        name = "".join(tr.xpath('./td[1]/text()')).replace(' ', '').replace("\n", "").replace('\r', "")
        holiday_range = "".join(tr.xpath('./td[2]/text()')).replace(' ', '').replace("\n", "").replace('\r', "")
        _need_color = _holiday_judge_range(holiday_range)
        make_up_days = "".join(tr.xpath('./td[3]/text()')).replace(' ', '').replace("\n", "").replace('\r', "")
        holiday_days = "".join(tr.xpath('./td[4]/text()')).replace(' ', '').replace("\n", "").replace('\r', "")
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


if __name__ == "__main__":
    print_today()
