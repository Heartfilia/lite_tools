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
from lxml import etree
from prettytable import PrettyTable

import requests
# from lite_tools.utils.tls import requests
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
    # _ = mode
    # resp = requests.get(
    #     'http://www.qiyoujiage.com/',
    #     headers={
    #         "user-agent": get_ua(),
    #         "Referer": "http://www.qiyoujiage.com",
    #         "Host": "www.qiyoujiage.com",
    #     }
    # )
    # resp.encoding = resp.apparent_encoding
    # return resp.text

    # https://www.tuanyou.net/youjia/   <<<-- 换成这个试试
    return ""


def parse_oil_data(html_obj):
    new_msg = "".join(html_obj.xpath('//div[@id="left"]/div[1]//text()')[:2])
    print(color_string(f"【今日油价】：{new_msg}"))
    tb_base = PrettyTable(["地区", "92#", "95#", "98#", "0#", " 地区", " 92#", " 95#", " 98#", " 0#"])
    city_nums = html_obj.xpath('//ul[@class="ylist"]/li[position() > 5]')
    temp_save = []
    for num in range(0, len(city_nums), 5):
        name = "".join(city_nums[num].xpath('./a/text()'))
        _92 = "".join(city_nums[num+1].xpath('./text()'))
        _95 = "".join(city_nums[num+2].xpath('./text()'))
        _98 = "".join(city_nums[num+3].xpath('./text()'))
        _0 = "".join(city_nums[num+4].xpath('./text()'))
        if len(temp_save) < 10:
            temp_save.extend([name, _92, _95, _98, _0])
        if len(temp_save) == 10:
            tb_base.add_row(temp_save)
            temp_save = []
    if len(temp_save) == 5:
        temp_save.extend(["", "", "", "", ""])
        tb_base.add_row(temp_save)
    print(tb_base)


if __name__ == "__main__":
    print_oil()
