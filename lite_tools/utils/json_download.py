import os
import requests

from lite_tools.tools.core.lite_try import try_catch
from lite_tools.utils.lite_dir import lite_tools_dir


def get_goal_dir(folder_name: str, json_name: str, file_url: str) -> str:
    dict_root = os.path.join(lite_tools_dir(), folder_name)
    if not os.path.exists(dict_root):
        os.makedirs(dict_root)

    file_dir = os.path.join(dict_root, json_name)
    if not os.path.exists(file_dir):
        download_file(file_dir, file_url)
    return file_dir


@try_catch(log="下载失败,可能网络异常")
def download_file(save_dir: str, file_url: str):
    """
    采用的是我的服务 所以应该 大概 也许 会有段时间用不了 需要修复
    """
    resp = requests.get(file_url)
    data = resp.text
    with open(save_dir, 'w', encoding='utf-8') as fp:
        fp.write(data)
