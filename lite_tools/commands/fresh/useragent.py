import os
import json

import requests
from loguru import logger

from lite_tools.utils import VERSION
from lite_tools.tools.core.lib_hashlib import get_md5
from lite_tools.tools.core.lite_parser import try_get
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.utils.json_download import get_goal_dir


def fresh_useragent():
    ua_path = get_goal_dir("browser", "ua_version.json", "http://static.litetools.top/source/json/useragent.json")
    if os.path.exists(ua_path):
        with open(ua_path, "r", encoding='utf-8') as fp:
            file_hash = get_md5(fp.read())
    else:
        file_hash = ""
    ua = get_info()
    cal_hash = get_md5(try_get(ua, json=True))
    if ua and cal_hash != file_hash:
        with open(ua_path, 'w', encoding='utf-8') as fp:
            json.dump(ua, fp)
        logger.success(f"更新了缓存的ua版本库...")
    elif ua and cal_hash == file_hash:
        logger.info("文件已存在并且已经是和线上同样内容的最新版本无需更新.")
    else:
        logger.warning("获取api文件失败，请重试.")


@try_catch(log=False, retry=1)
def get_info():
    # http://static.litetools.top/source/json/useragent.json
    # https://cdn.jsdelivr.net/npm/litetools/tools/useragent.json
    resp = requests.get(
        "http://static.litetools.top/source/json/useragent.json",
        headers={"user-agent": f"python-lite-tools/{VERSION} Based On Script Engine"},
        timeout=5
    )
    ua = resp.json()
    if "chromium" in ua and "firefox" in ua and "safari" in ua:
        return ua
    raise ValueError
