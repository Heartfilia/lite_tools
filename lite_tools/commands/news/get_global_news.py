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
import requests
# from lite_tools.utils.tls import requests
from lite_tools.tools.core.lite_ua import get_ua
from lite_tools.tools.time.lite_time import get_time
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.tools.core.lite_parser import try_get
from lite_tools.tools.core.lite_string import color_string
from lite_tools.utils.lite_table import get_terminal_long, print_head


_base_template = """{split_line}
<yellow>时间: {publish_time}</yellow>
<cyan>标题: {title}</cyan>
链接: {link}
简述: {summary}
<blue>来源: {source}</blue>
"""


@try_catch(log="本功需要网络或者网页样式变更或者你开了抓包工具才拿不到")
def get_china_news(callback=False):
    """
    获取国内新闻
    """
    url = "https://china.huanqiu.com/api/list"
    params = {
        "node": '"/e3pmh1nnq/e3pmh1obd","/e3pmh1nnq/e3pn61c2g","/e3pmh1nnq/e3pn6eiep",'
                '"/e3pmh1nnq/e3pra70uk","/e3pmh1nnq/e5anm31jb","/e3pmh1nnq/e7tl4e309"',
        "offset": 0,
        "limit": 20
    }
    data = _get_global_requests(url, params)
    if callback is True:
        return data
    else:
        _parse_news(data, "国内")


def get_world_news():
    """
    获取国际新闻
    """
    url = "https://world.huanqiu.com/api/list"
    params = {
        "node": '"/e3pmh22ph/e3pmh2398","/e3pmh22ph/e3pmh26vv","/e3pmh22ph/e3pn6efsl","/e3pmh22ph/efp8fqe21"',
        "offset": 0,
        "limit": 24
    }
    data = _get_global_requests(url, params)
    _parse_news(data, "国际")


def _get_global_requests(url, params=None) -> dict:
    resp = requests.get(
        url,
        params=params,
        headers={
            "user-agent": get_ua(),
            "referer": "https://world.huanqiu.com/"
        }
    )
    return resp.json()


def _parse_news(data, location):
    items = data.get('list')
    title_line = "\n".join(print_head(f"【每日资讯】<red>{location}</red> 最新消息", 11).split("\n")[:2])
    base_string = f"{title_line}\n"
    for item in items:
        time_info = item.get('ctime')
        if not time_info:
            continue
        publish_time = get_time(int(time_info), fmt=True)
        title = item.get('title')
        if not title:
            continue
        link = try_get(item, "source.url") or \
            "https://world.huanqiu.com/" if location == "国际" else "https://china.huanqiu.com"
        summary = try_get(item, 'summary')
        source = try_get(item, 'source.name')
        base_string += _base_template.format(
            split_line=get_terminal_long() * "-",
            publish_time=publish_time,
            title=title,
            link=link,
            summary=summary,
            source=source
        )
    print(color_string(base_string))


if __name__ == "__main__":
    get_china_news()
