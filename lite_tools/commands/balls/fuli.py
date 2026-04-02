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
import json
import re
from typing import Any

import requests

from lite_tools.logs import logger
from lite_tools.utils.lite_table import print_head
from lite_tools.tools.core.lite_string import color_string


_FULI_URL = "https://www.gdfc.org.cn/datas/drawinfos.js"
_FULI_GAME_MAP = {
    5: "双色球",
    6: "福彩3D",
    10: "快乐8",
}


def _load_draw_infos() -> list[dict[str, Any]]:
    resp = requests.get(
        _FULI_URL,
        timeout=15,
        headers={"user-agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()
    text = resp.content.decode("gbk", errors="ignore")
    matched = re.search(r"var\s+gameDrawInfos\s*=\s*(\[.*\]);?\s*$", text, re.S)
    if not matched:
        raise ValueError("未能解析福彩开奖数据")
    return json.loads(matched.group(1))


def _split_pairs(number_string: str) -> list[str]:
    string = re.sub(r"\s+", "", number_string)
    return [string[index:index + 2] for index in range(0, len(string), 2) if string[index:index + 2]]


def _format_ssq(number_string: str) -> tuple[str, str]:
    numbers = _split_pairs(number_string)
    red = " ".join(numbers[:-1]) if len(numbers) > 1 else "--"
    blue = numbers[-1] if numbers else "--"
    return red, blue


def _format_kl8(number_string: str) -> str:
    return " ".join(_split_pairs(number_string)) or "--"


def _format_fc3d(number_string: str) -> str:
    parts = [item for item in str(number_string).split() if item]
    return " ".join(parts) or "--"


def get_fuli():
    try:
        raw_items = _load_draw_infos()
    except requests.RequestException as err:
        logger.error(f"请求福利彩票数据失败: {err}")
        return
    except ValueError as err:
        logger.error(f"解析福利彩票数据失败: {err}")
        return

    parsed: dict[int, dict[str, Any]] = {}
    for item in raw_items:
        game_id = item.get("gameID")
        if game_id in _FULI_GAME_MAP:
            parsed[game_id] = item

    missing = [name for game_id, name in _FULI_GAME_MAP.items() if game_id not in parsed]
    if missing:
        logger.error(f"福利彩票数据缺少游戏: {', '.join(missing)}")
        return

    parse_fuli(parsed)


def parse_fuli(data: dict[int, dict[str, Any]]):
    base_string = print_head("福利彩票")

    ssq = data[5]
    ssq_red, ssq_blue = _format_ssq(ssq.get("luckyNo", ""))
    title_ssq = "<blue>双色球: </blue>"
    ssq_date = f"<yellow>{ssq.get('drawName', '--')}</yellow> -- "
    ssq_red_string = f"<red>[{ssq_red}]</red>"
    ssq_blue_string = f"<blue>[{ssq_blue}]</blue>"

    fc3d = data[6]
    fc3d_numbers = _format_fc3d(fc3d.get("luckyNo", ""))
    title_fc3d = "\n<blue>福彩3D: </blue>"
    fc3d_date = f"<yellow>{fc3d.get('drawName', '--')}</yellow> -- "
    fc3d_string = f"<blue>[{fc3d_numbers}]</blue>"

    kl8 = data[10]
    kl8_numbers = _format_kl8(kl8.get("luckyNo", ""))
    title_kl8 = "\n<blue>快乐8 : </blue>"
    kl8_date = f"<yellow>{kl8.get('drawName', '--')}</yellow> -- "
    kl8_string = f"<red>[{kl8_numbers}]</red>"

    print(color_string("".join([
        base_string,
        title_ssq, ssq_date, ssq_red_string, ssq_blue_string,
        title_fc3d, fc3d_date, fc3d_string,
        title_kl8, kl8_date, kl8_string,
    ])))
    return True


if __name__ == "__main__":
    get_fuli()
