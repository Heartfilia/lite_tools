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
import sys
from logs import logger

try:
    from lxml import etree
except ImportError:
    logger.error("需要安装requests和lxml才可以")
    sys.exit(0)

import requests
# from utils.tls import requests
# from tools.core.lite_ua import get_ua
from utils.lite_table import print_head
from tools.core.lite_string import color_string


# @try_catch(log="需要网络,可以重试,也可能网站数据源变更--短时间内重复请求会没有数据的哦 请求了要等好一会才能重新请求")
def get_fuli():
    return


def parse_fuli(html):
    if "<title>中国福彩网" not in html:
        return False
    obj = etree.HTML(html)
    base_string = print_head("福利彩票")
    title_ssq = "<blue>双色球: </blue>"
    ssq_date = "<yellow>" + "".join(obj.xpath('//div[@class="ssqQh-dom"]/text()')) + "</yellow> -- "
    ssq_red = "<red>" + "".join(obj.xpath('//div[@class="ssqRed-dom"]/text()')) + "</red>"
    ssq_blue = "<blue>" + "".join(obj.xpath('//div[@class="ssqBlue-dom"]/text()')) + "</blue>"

    title_kl8 = "\n<blue>快乐8 : </blue>"
    kl8_date = "<yellow>" + "".join(obj.xpath('//div[@class="kl8Qh-dom"]/text()')) + "</yellow> -- "
    kl8_red = "<red>" + "".join(obj.xpath('//div[@class="klRed-dom"]/text()')) + "</red>"

    title_fc = "\n<blue>福彩3D: </blue>"
    fc_date = "<yellow>" + "".join(obj.xpath('//div[@class="fcQh-dom"]/text()')) + "</yellow> -- "
    fc_blue = "<blue>" + "".join(obj.xpath('//div[@class="fcBlue-dom"]/text()')) + "</blue>"

    title_qlc = "\n<blue>七乐彩: </blue>"
    qlc_date = "<yellow>" + "".join(obj.xpath('//div[@class="qlcQh-dom"]/text()')) + "</yellow> -- "
    qlc_red = "<red>" + "".join(obj.xpath('//div[@class="qclRed-dom"]/text()')) + "</red>"
    qlc_blue = "<blue>" + "".join(obj.xpath('//div[@class="qclBlue-dom"]/text()')) + "</blue>"
    print(color_string("".join([
        base_string, title_ssq, ssq_date, ssq_red, ssq_blue, title_kl8, kl8_date, kl8_red,
        title_fc, fc_date, fc_blue, title_qlc, qlc_date, qlc_red, qlc_blue
    ])))
    return True


if __name__ == "__main__":
    get_fuli()
