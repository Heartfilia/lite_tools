import os
import json

import requests
from loguru import logger

from lite_tools.version import VERSION
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.utils.lite_dir import lite_tools_dir


def fresh_useragent():
    ua_root = os.path.join(lite_tools_dir(), "browser")
    if not os.path.exists(ua_root):
        os.makedirs(ua_root)
    ua_path = os.path.join(ua_root, "ua_version.json")
    ua = get_info()
    if ua:
        with open(ua_path, 'w', encoding='utf-8') as fp:
            json.dump(ua, fp)
        logger.success(f"更新了缓存的ua版本库...")


@try_catch(log=False, retry=3)
def get_info():
    resp = requests.get(
        "https://cdn.jsdelivr.net/npm/litetools/tools/useragent.json",
        headers={"user-agent": f"python-lite-tools/{VERSION} Based On Script Engine"},
        timeout=5
    )
    ua = resp.json()
    if "chromium" in ua and "firefox" in ua and "safari" in ua:
        return ua
    raise ValueError
