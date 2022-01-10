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
    import requests
    from lxml import etree
    import prettytable as pt
    from prettytable import PrettyTable
except ImportError:
    raise ImportError

from lite_tools.lib_jar.lib_ua import get_ua
from lite_tools.lib_jar.lib_try import try_catch
from lite_tools.lib_jar.lib_string_parser import color_string


# @try_catch(log="请不要频繁请求<或者>网页数据版式有改动[如果这样的话那就不要用这个功能啦]")
def print_today():
    """
    关于假期:如果假期是未发生的,那么将会是<黄色>标注,假如是正在假期间,将会是<绿色>标注,其次无颜色标注
    """
    print(color_string("【假期】还不到的假期显示<<yellow>黄色</yellow>>，正在假期中显示<<green>绿色</green>>，已经过了的假期<无色>"))
    print('- - ' * 20)
    html_text = get_date_web()
    html_obj = etree.HTML(html_text)
    # parse_html_holiday(html_obj)   # 解析假期
    print('- - ' * 20)
    parse_html_today(html_obj)     # 解析今天的运势


def get_date_web() -> str:
    # resp = requests.get('https://www.wannianli.cn/', headers={'user-agent': get_ua()})
    # return resp.text
    with open(r"E:\my_github\lite_tools\lib_jar\date_test.html", 'r', encoding='utf-8') as fp:
        html = fp.read()
    return html


def parse_html_today(html: etree.HTML):
    tables = html.xpath(
        '//div[@class="widget-box"]//table[0]/tbody/tr')
    print(tables)
    table_head = "".join(tables[0].xpath('./td[3]/text()'))
    pt_today = PrettyTable(["今日运势", table_head])
    pt_today.set_style(pt.PLAIN_COLUMNS)
    for tr in tables[1:]:
        th = "".join(tr.xpath('./th[1]/text()'))
        td = "".join(tr.xpath('./td')[-1].xpath('./text()'))
        if th == "【宜】":
            th = color_string(f"<green>{th}</green>")
            td = color_string(f"<green>{td}</green>")
        elif th == "【忌】":
            th = color_string(f"<red>{th}</red>")
            td = color_string(f"<red>{td}</red>")
        elif "友情提示" in th:
            continue
        pt_today.add_row([th, td])
    print(pt_today)


def parse_html_holiday(html: etree.HTML):
    year = time.localtime().tm_year
    pt_holiday = PrettyTable([f"{year}年节日", "放假时间", "调休日期", "放假天数"])
    pt_holiday.set_style(pt.PLAIN_COLUMNS)
    tables = html.xpath('//div[contains(@class, "theme-showcase")]/div/div[2]/div[1]/table/tbody/tr[position()>1]')
    for tr in tables:
        name = "".join(tr.xpath('./td[1]/text()')).replace(' ', '').replace("\n", "")
        holiday_range = "".join(tr.xpath('./td[2]/text()')).replace(' ', '').replace("\n", "")
        _need_color = _holiday_judge_range(holiday_range)
        make_up_days = "".join(tr.xpath('./td[3]/text()')).replace(' ', '').replace("\n", "")
        holiday_days = "".join(tr.xpath('./td[4]/text()')).replace(' ', '').replace("\n", "")
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
