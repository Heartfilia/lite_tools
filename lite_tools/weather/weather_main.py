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
from lite_tools.lib_jar.lib_dict_parser import try_key, JsJson, try_get

from lite_tools.weather.citys import city_data

print_template = """<yellow>【今日天气】</yellow> {date} {city}
当前: <red>{temp}℃</red> {weather}
{today_information}
<yellow>【近日情况】</yellow>
{recent_days}
<yellow>【今日指数】</yellow>
{index_information}
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
    information = request_weather(city_id, city)
    if information:
        parse_weather_info(information)


def parse_head_info(data):
    city = data.get('cityname', '')
    date = data.get('date', '')
    temp_now = data.get('temp')
    weather_now = data.get('weather')
    return city, date, temp_now, weather_now


def parse_today_info(data):
    temp_high = try_get(data, 'weatherinfo.temp')
    temp_low = try_get(data, 'weatherinfo.tempn')
    weather_today = try_get(data, 'weatherinfo.weather')
    wd = try_get(data, 'weatherinfo.wd')
    ws = try_get(data, 'weatherinfo.ws')
    base_info = f"气候: <red>{temp_high}℃ / {temp_low}℃</red> {weather_today}\n"
    base_info += f"风况: <green>{wd} </green> [{ws}]"
    return base_info


def parse_recent_days(data):
    heads = []
    temps = []
    winds = []
    for each in data.get('f'):
        heads.append(each.get('fj'))
        temp_high = each.get('fc')
        temp_low = each.get('fd')
        temps.append(f"{temp_high}℃ / {temp_low}℃")
        winds.append(each.get('fe'))
    tb_recent = PrettyTable(heads)
    tb_recent.add_row(temps)
    tb_recent.add_row(winds)
    return tb_recent


def parse_index_info(data):
    zs = data.get('zs')
    tb_zs = PrettyTable(["穿衣", "路况", "钓鱼", "晨练", "夜生活", "感冒", "逛街", "空气", "旅游", "运动"])
    tb_zs.add_row([
        zs.get("ct_hint"), zs.get("lk_hint"), zs.get("dy_hint"), zs.get("cl_hint"), zs.get("nl_hint"),
        zs.get("gm_hint"), zs.get('gj_hint'), zs.get('pl_hint'), zs.get('tr_hint'), zs.get("yd_hint")
    ])
    return tb_zs


def parse_weather_info(js):
    items = JsJson(js)
    city, date, temp_now, weather_now = parse_head_info(items.get('dataSK'))
    today_info_all = parse_today_info(items.get('cityDZ'))
    tb_recent = parse_recent_days(items.get('fc'))
    index_information = parse_index_info(items.get('dataZS'))

    string = print_template.format(
        city=city, date=date, temp=temp_now, weather=weather_now,
        today_information=today_info_all, recent_days=tb_recent, index_information=index_information
    )
    print(color_string(string))


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
        }).content.decode('utf-8')
    geo_id = re.search(r'id="(\d+)"', resp).group(1)
    if not geo_id:
        raise KeyError
    return geo_id


if __name__ == "__main__":
    # geo_weather_id()
    # request_weather("101280101")
    get_weather()
