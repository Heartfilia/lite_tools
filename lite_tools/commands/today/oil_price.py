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
from lxml import etree
from prettytable import PrettyTable

from lite_tools.tools.core.lite_ua import get_ua
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_string import color_string
from lite_tools.commands.today.today_utils import check_cache


@try_catch(log="本功能为在线功能,需要网络。如有网络不要频繁请求，[如果网页数据版式有改动,这样的话这个功能暂时就废了需要修复]")
def print_oil():
    """
    今日全国油价
    """
    html_text = get_html_info("oil")
    html_obj = etree.HTML(html_text)
    parse_oil_data(html_obj)


@check_cache
def get_html_info(mode: str = "oil"):
    _ = mode
    return requests.get('https://oil.usd-cny.com', headers={"user-agent": get_ua()}).content.decode('gb2312')


def parse_oil_data(html_obj):
    fresh_time = "".join(html_obj.xpath("//time/text()"))
    print(color_string(f"【今日油价】刷新时间 -- {fresh_time}"))
    tb_base = PrettyTable(["地区", "92#", "95#", "98#", "0#"])
    city_infos = html_obj.xpath('//table[2]/tr[position()>1]')
    for city in city_infos:
        name = "".join(city.xpath('./td[1]/a/strong/text()'))
        _92 = "".join(city.xpath('./td[2]/text()'))
        _95 = "".join(city.xpath('./td[3]/text()'))
        _98 = "".join(city.xpath('./td[4]/text()'))
        _0 = "".join(city.xpath('./td[5]/text()'))
        tb_base.add_row([name, _92, _95, _98, _0])
    print(tb_base)
