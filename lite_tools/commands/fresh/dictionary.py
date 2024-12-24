import os

import requests
from loguru import logger

from lite_tools.tools.core.lib_hashlib import get_md5
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.utils.lite_dir import lite_tools_dir


def fresh_dictionary():
    dict_root = os.path.join(lite_tools_dir(), "dict")
    if not os.path.exists(dict_root):
        os.makedirs(dict_root)
    dict_path = os.path.join(dict_root, "dictionary.json")
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding='utf-8') as fp:
            file_hash = get_md5(fp.read())
    else:
        file_hash = ""
    dic = get_info()
    cal_hash = get_md5(dic)
    if dic and cal_hash != file_hash:
        with open(dict_path, 'w', encoding='utf-8') as fp:
            fp.write(dic)
        logger.success(f"更新了缓存的dict版本库...")
    elif dic and cal_hash == file_hash:
        logger.info("文件已存在并且已经是和线上同样内容的最新版本无需更新.")
    else:
        logger.warning("获取api文件失败，请重试.")


@try_catch(log=False)
def get_info():
    resp = requests.get("http://static.litetools.top/source/json/dictionary.json")
    data = resp.text
    return data
