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

from lite_tools.tools.core.lite_string import color_string
from lite_tools.commands.today.today_utils import check_cache


_OIL_URL = "https://www.tuanyou.net/youjia/"


def _clean_text(value: str) -> str:
    return " ".join(str(value).split())


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
    resp = requests.get(
        _OIL_URL,
        headers={"user-agent": "Mozilla/5.0"},
        timeout=15,
    )
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text


def parse_oil_data(html_obj):
    h1 = _clean_text("".join(html_obj.xpath("//h1//text()"))).replace("北京市", "全国")
    summary_rows = [_clean_text("".join(row.xpath(".//text()"))) for row in html_obj.xpath("//table[1]//tr")]
    summary_rows = [row for row in summary_rows if row]
    summary_text = " | ".join(summary_rows[:4])
    print(color_string(f"【今日油价】：{h1}"))
    if summary_text:
        print(color_string(summary_text))

    tb_base = PrettyTable(["地区", "92#", "95#", "98#", "0#", "地区 ", "92# ", "95# ", "98# ", "0# "])
    city_rows = []

    for item in html_obj.xpath("/html/body/div/div[5]/div[7]/div[2]/li"):
        values = [_clean_text("".join(link.xpath(".//text()"))) for link in item.xpath("./a")]
        values = [value for value in values if value]
        if len(values) >= 5:
            if values[0].startswith("地区") or values[1].startswith("92号"):
                continue
            city_rows.append(values[:5])

    for index in range(0, len(city_rows), 2):
        left = city_rows[index]
        right = city_rows[index + 1] if index + 1 < len(city_rows) else ["", "", "", "", ""]
        tb_base.add_row(left + right)

    print(tb_base)


if __name__ == "__main__":
    print_oil()
