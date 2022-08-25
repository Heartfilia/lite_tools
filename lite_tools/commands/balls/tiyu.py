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
except ImportError:
    logger.error("需要安装requests和lxml才可以")
    sys.exit(0)

from lite_tools.tools.core.lite_ua import get_ua
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.utils.lite_table import print_head
from lite_tools.tools.core.lite_parser import try_get
from lite_tools.tools.core.lite_string import color_string


@try_catch(log="需要网络,可以重试,也可能网站数据源变更")
def get_tiyu():
    params = {
        "isVerify": "1",
        "param": "85,0;35,0;350133,0;04,0;"
        #         大乐透 排列三 排列五 七星彩
    }
    resp = requests.get(
        'https://webapi.sporttery.cn/gateway/lottery/getDigitalDrawInfoV1.qry',
        params=params,
        headers={"user-agent": get_ua()}
    )
    parse_tiyu(resp.text)


def parse_tiyu(data):
    base_string = print_head("体育彩票")
    title_dlt = "<green>大乐透: </green>"
    dlt_result = try_get(data, 'value.dlt.lotteryDrawResult').split()
    dlt_date = "<red>" + try_get(data, 'value.dlt.lotteryDrawNum') + "</red> -- "
    dlt_blue = "<blue>[" + " ".join(dlt_result[:-2]) + "]</blue>"
    dlt_yellow = "<red>[" + " ".join(dlt_result[-2:]) + "]</red>"

    title_pls = "\n<green>排列三: </green>"
    pls_date = "<red>" + try_get(data, 'value.pls.lotteryDrawNum') + "</red> -- "
    pls_purple = "<purple>[" + try_get(data, 'value.pls.lotteryDrawResult') + "]</purple>"

    title_plw = "\n<green>排列五: </green>"
    plw_date = "<red>" + try_get(data, 'value.plw.lotteryDrawNum') + "</red> -- "
    plw_purple = "<purple>[" + try_get(data, 'value.plw.lotteryDrawResult') + "]</purple>"

    title_qxc = "\n<green>七星彩: </green>"
    qxc_result = try_get(data, 'value.qxc.lotteryDrawResult').split()
    qxc_date = "<red>" + try_get(data, 'value.qxc.lotteryDrawNum') + "</red> -- "
    qxc_blue = "<blue>[" + " ".join(qxc_result[:-1]) + "]</blue>"
    qxc_yellow = "<yellow>[" + qxc_result[-1] + "]</yellow>"
    print(color_string("".join([
        base_string, title_dlt, dlt_date, dlt_blue, dlt_yellow, title_pls, pls_date, pls_purple,
        title_plw, plw_date, plw_purple, title_qxc, qxc_date, qxc_blue, qxc_yellow
    ])))
