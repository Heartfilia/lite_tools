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
from loguru import logger

try:
    import requests
    from lxml import etree
except ImportError:
    logger.error("需要安装requests和lxml才可以")
    sys.exit(0)

from lite_tools.tools.pure.lib_ua import get_ua
from lite_tools.tools.utils.lite_table import print_head
from lite_tools.tools.lib_string_parser import color_string

# TODO(这里不知道为啥就第一次可以请求到数据 后面的就拿不到了 当然加上代理就随时能拿到数据 可是网页还是能正常访问的)


# @try_catch(log="需要网络,可以重试,也可能网站数据源变更--短时间内重复请求会没有数据的哦 请求了要等好一会才能重新请求")
def get_fuli():
    return
    resp_base = requests.get(
        'http://www.cwl.gov.cn/cwl_admin/front/stat/dealer?Event=Unload&SiteID=21&StickTime=25150',
        headers={
            "user-agent": get_ua(),
            "Referer": "http://www.cwl.gov.cn/",
            "cookie": "C3VK=0ea372; HMF_CI=088fdbb2e1c09308336e3bdbc7da1466db86050081ec91500c4e78804ffad7c0d4; 21_vq=1"
        },
    )
    # print(resp_base.headers)
    # html_1 = requests.get('http://www.cwl.gov.cn/')
    #
    # flag = parse_fuli(html_1.content.decode('utf-8'))
    # if not flag:
    #     print(html_1.text)
    #     cookie = re.search(r'cookie="(\w+)=(\w+);', html_1.text, re.I)
    #     key = cookie.group(1)
    #     value = cookie.group(2)
    #     session.cookies.update({key: value})
    #     resp = session.get('http://www.cwl.gov.cn')
    #     parse_fuli(resp.text)


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
