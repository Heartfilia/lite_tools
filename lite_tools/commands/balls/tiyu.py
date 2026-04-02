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
from typing import Mapping, Any

from lite_tools.logs import logger

try:
    import requests
except ImportError:
    logger.error("需要安装requests和lxml才可以")
    sys.exit(0)

from lite_tools.utils.lite_table import print_head
from lite_tools.tools.core.lite_string import color_string


_SPORTTERY_API = "https://webapi.sporttery.cn/gateway/lottery/getDigitalDrawInfoV1.qry"
_SPORTTERY_REFERER = "https://www.sporttery.cn/digitallottery/"
_SPORTTERY_PARAMS = {
    "isVerify": "1",
    "param": "85,0;35,0;350133,0;04,0",
    # 大乐透 排列三 排列五 七星彩
}


def _build_headers() -> dict:
    return {
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        ),
        "accept": "application/json, text/javascript, */*; q=0.01",
        "referer": _SPORTTERY_REFERER,
        "origin": "https://www.sporttery.cn",
        "x-requested-with": "XMLHttpRequest",
    }


def get_tiyu():
    try:
        resp = requests.get(
            _SPORTTERY_API,
            params=_SPORTTERY_PARAMS,
            headers=_build_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as err:
        logger.error(f"请求体育彩票接口失败: {err}")
        return
    except ValueError as err:
        logger.error(f"解析体育彩票接口返回失败: {err}")
        return

    if str(data.get("errorCode")) != "0" or not isinstance(data.get("value"), dict):
        logger.error(f"体育彩票接口返回异常: {data.get('errorMessage') or data}")
        return

    parse_tiyu(data["value"])


def _safe_text(value: Any, default: str = "--") -> str:
    if value is None:
        return default
    string = str(value).strip()
    return string or default


def _draw_result(value: Mapping[str, Any], key: str) -> list[str]:
    result = _safe_text(value.get(key), "").split()
    return result


def parse_tiyu(data: Mapping[str, Mapping[str, Any]]):
    base_string = print_head("体育彩票")

    dlt = data.get("dlt", {})
    title_dlt = "<green>大乐透: </green>"
    dlt_result = _draw_result(dlt, "lotteryDrawResult")
    dlt_date = f"<red>{_safe_text(dlt.get('lotteryDrawNum'))}</red> -- "
    dlt_blue = "<blue>[" + " ".join(dlt_result[:-2]) + "]</blue>" if len(dlt_result) >= 2 else "<blue>[--]</blue>"
    dlt_yellow = "<red>[" + " ".join(dlt_result[-2:]) + "]</red>" if len(dlt_result) >= 2 else "<red>[--]</red>"

    pls = data.get("pls", {})
    title_pls = "\n<green>排列三: </green>"
    pls_date = f"<red>{_safe_text(pls.get('lotteryDrawNum'))}</red> -- "
    pls_purple = f"<purple>[{_safe_text(pls.get('lotteryDrawResult'))}]</purple>"

    plw = data.get("plw", {})
    title_plw = "\n<green>排列五: </green>"
    plw_date = f"<red>{_safe_text(plw.get('lotteryDrawNum'))}</red> -- "
    plw_purple = f"<purple>[{_safe_text(plw.get('lotteryDrawResult'))}]</purple>"

    qxc = data.get("qxc", {})
    title_qxc = "\n<green>七星彩: </green>"
    qxc_result = _draw_result(qxc, "lotteryDrawResult")
    qxc_date = f"<red>{_safe_text(qxc.get('lotteryDrawNum'))}</red> -- "
    qxc_blue = "<blue>[" + " ".join(qxc_result[:-1]) + "]</blue>" if qxc_result else "<blue>[--]</blue>"
    qxc_yellow = f"<yellow>[{qxc_result[-1]}]</yellow>" if qxc_result else "<yellow>[--]</yellow>"

    print(color_string("".join([
        base_string, title_dlt, dlt_date, dlt_blue, dlt_yellow, title_pls, pls_date, pls_purple,
        title_plw, plw_date, plw_purple, title_qxc, qxc_date, qxc_blue, qxc_yellow
    ])))


if __name__ == "__main__":
    get_tiyu()
