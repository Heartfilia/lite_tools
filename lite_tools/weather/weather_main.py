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
import re
import requests
from urllib.parse import quote
from prettytable import PrettyTable

from loguru import logger
from lite_tools.lib_jar.lib_ua import get_ua
from lite_tools.lib_jar.lib_time import get_time
from lite_tools.lib_jar.lib_try import try_catch
from lite_tools.lib_jar.lib_string_parser import color_string
from lite_tools.lib_jar.lib_dict_parser import try_key, JsJson

from lite_tools.weather.citys import city_data

print_template = """【中国天气】 <red>{city}</red> -- {date} -- {}
{today_information}
"""


@try_catch(log="本功能需要网络或者页面数据获取模式变更,和当前网络也有关系,可以重试一下")
def get_weather(city: str = None, geo_id: str = None):
    city_id = None
    if city is not None:
        pure_city = clean_city_name(city)
        geo_id_list = try_key(city_data, "AREAID", options={"filter": {"equal": {"NAMECN": pure_city}}})
        city_id = geo_id_list[0] if geo_id_list else None
    if not city_id and geo_id is not None:
        city_id = geo_id if geo_id.isdigit() else None
    elif not city_id and not geo_id:
        city_id = geo_weather_id()

    if not city_id:
        raise KeyError
    infos = request_weather(city_id, city)
    if infos:
        parse_weather_info(infos)


def parse_weather_info(js):
    items = JsJson(js)
    items.get('')


def clean_city_name(city):
    if city.endswith("市") or city.endswith("区") or city.endswith("县"):
        return city[:-1]
    else:
        return city


def request_weather(geo_id, city=None):
    """
    这里负责请求城市信息
    """
    if city is None:
        city = try_key(city_data, 'NAMECN', options={"filter": {"equal": {"AREAID": str(geo_id)}}})
        if not city:
            logger.warning(f"没有找到对应的城市...")
            return
        city = city[0]

    resp = requests.get(
        f"http://d1.weather.com.cn/weather_index/{geo_id}.html?_={int(get_time(double=True) * 1000)}",
        headers={
            "user-agent": get_ua(),
            'Referer': "http://www.weather.com.cn/",
            'Cookie': f"Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b={get_time()}; "
                      f"f_city={quote(f'{city}|{geo_id}|')}; "
                      f"Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b={get_time()}"
        }
    )
    return resp.content.decode('utf-8')


def geo_weather_id():
    """
    var ip="61.140.93.216";var id="101280101";var addr="广东,广州,广州";  # 不需要后面的addr
    """
    resp = requests.get(
        f"http://wgeo.weather.com.cn/ip/?_={int(get_time(double=True) * 1000)}",
        headers={
            "user-agent": get_ua(),
            'Referer': "http://www.weather.com.cn/",
        }).text
    geo_id = re.search(r'id="(\d+)"', resp).group(1)
    if not geo_id:
        raise KeyError
    return geo_id


if __name__ == "__main__":
    # geo_weather_id()
    request_weather("101280101")
