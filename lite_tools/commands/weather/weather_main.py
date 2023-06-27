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
import os
import re
import json
from urllib.parse import quote
from prettytable import PrettyTable

import requests
from loguru import logger

from lite_tools.tools.core.lite_ua import get_ua
from lite_tools.tools.time.lite_time import get_time
from lite_tools.tools.core.lite_try import try_catch
from lite_tools.utils.json_download import get_goal_dir
from lite_tools.tools.core.lite_string import color_string
from lite_tools.tools.core.lite_parser import try_key, JsJson, try_get

print_template = """<yellow>【今日天气】</yellow>[更新时间 {fresh_time}]
<cyan>{city}</cyan>当前: <red>{temp} ℃</red> {weather} {date}
{today_information}
<yellow>【近日情况】</yellow>
{recent_days}
<yellow>【今日指数】</yellow>
{index_information}"""


@try_catch(log="本功能需要网络或者页面数据获取模式变更,和当前网络也有关系,可以重试一下")
def get_weather(city: str = None, geo_id: str = None):
    city_id = None
    if city is not None:
        pure_city = clean_city_name(city)
        geo_id_list = try_key(get_city(), "AREAID", options={"filter": {"equal": {"NAMECN": pure_city}}})
        city_id = geo_id_list[0] if geo_id_list else None
        if not city_id:
            logger.warning("请输入国内有的准确的地点，只需要写入最小单位的数据即可[仅支持 - 市、区、县]")
            return
    if not city_id and geo_id is not None:
        city_id = geo_id if geo_id.isdigit() else None
    elif not city_id and not geo_id:
        city_id = geo_weather_id()

    if not city_id:
        raise KeyError
    information = request_weather(city_id, city)
    if information:
        parse_weather_info(information)


def get_city():
    base_root = get_goal_dir("weather", "cities.json", "http://static.litetools.top/source/json/cities.json")
    if not os.path.exists(base_root):
        logger.warning("字典源数据获取异常...")
        return
    with open(base_root, "r", encoding='utf-8') as fp:
        data = json.load(fp)
    return data


def parse_head_info(data):
    city = data.get('cityname', '')
    date = data.get('date', '')
    temp_now = data.get('temp')
    weather_now = data.get('weather')
    fresh_time = data.get('time')
    return city, date, temp_now, weather_now, fresh_time


def parse_today_info(data, temp_info):
    """今日天气"""
    temp_high = try_get(temp_info, 'f[0].fc')
    temp_low = try_get(temp_info, 'f[0].fd')
    weather_today = try_get(data, 'weatherinfo.weather')
    wd = try_get(data, 'weatherinfo.wd')
    ws = try_get(data, 'weatherinfo.ws')
    return f"今日总览: <red>{temp_low}/{temp_high} ℃</red> {weather_today} | <green>{wd}</green> {ws}"


def parse_recent_days(data):
    """近日情况"""
    heads = []
    temps = []
    weather_info = []
    winds = []
    wind_level = []
    for each in data.get('f'):
        heads.append(each.get('fj'))
        temp_high = each.get('fc')
        temp_low = each.get('fd')
        temps.append(f"{temp_low}/{temp_high} ℃")
        weather_info.append(weather_detail(each.get("fa")))
        winds.append(each.get('fe'))
        wind_level.append(each.get('fg'))
    tb_recent = PrettyTable(heads)
    tb_recent.add_row(temps)
    tb_recent.add_row(weather_info)
    tb_recent.add_row(winds)
    tb_recent.add_row(wind_level)
    return tb_recent


def parse_index_info(data):
    """今日指数"""
    zs = data.get('zs')
    tb_zs = PrettyTable(["穿衣", "路况", "钓鱼", "晨练", "夜生活", "感冒", "逛街", "空气", "旅游", "运动"])
    tb_zs.add_row([
        zs.get("ct_hint"), zs.get("lk_hint"), zs.get("dy_hint"), zs.get("cl_hint"), zs.get("nl_hint"),
        zs.get("gm_hint"), zs.get('gj_hint'), zs.get('pl_hint'), zs.get('tr_hint'), zs.get("yd_hint")
    ])
    return tb_zs


def parse_weather_info(js):
    items = JsJson(js)
    city, date, temp_now, weather_now, fresh_time = parse_head_info(items.get('dataSK'))
    today_info_all = parse_today_info(items.get('cityDZ'), items.get('fc'))
    tb_recent = parse_recent_days(items.get('fc'))
    index_information = parse_index_info(items.get('dataZS'))

    string = print_template.format(
        city=city, date=date, temp=temp_now, weather=weather_now, fresh_time=fresh_time,
        today_information=today_info_all, recent_days=tb_recent, index_information=index_information
    )
    print(color_string(string))


def clean_city_name(city):
    if city.endswith("市") or city.endswith("区") or city.endswith("县"):
        return city[:-1]
    else:
        return city


def weather_detail(code):
    weather_code = {
        "10": "暴雨", "11": "大暴雨", "12": "特大暴雨", "13": "阵雪", "14": "小雪", "15": "中雪", "16": "大雪", "17": "暴雪",
        "18": "雾", "19": "冻雨", "20": "沙尘暴", "21": "小到中雨", "22": "中到大雨", "23": "大到暴雨", "24": "暴雨到大暴雨",
        "25": "大暴雨到特大暴雨", "26": "小到中雪", "27": "中到大雪", "28": "大到暴雪", "29": "浮尘", "30": "扬沙",
        "31": "强沙尘暴", "32": "浓雾", "49": "强浓雾", "53": "霾", "54": "中度霾", "55": "重度霾", "56": "严重霾",
        "57": "大雾", "58": "特强浓雾", "99": "无", "301": "雨", "302": "雪", "00": "晴", "01": "多云", "02": "阴",
        "03": "阵雨", "04": "雷阵雨", "05": "雷阵雨伴有冰雹", "06": "雨夹雪", "07": "小雨", "08": "中雨", "09": "大雨"
    }
    return weather_code.get(code) or ""


def request_weather(geo_id, city=None):
    """
    这里负责请求城市信息
    """
    if city is None:
        city = try_key(get_city(), 'NAMECN', options={"filter": {"equal": {"AREAID": str(geo_id)}}})
        if not city:
            logger.warning(f"没有找到对应的城市...")
            return
        city = city[0]

    resp = requests.get(
        f"http://d1.weather.com.cn/weather_index/{geo_id}.html?_={get_time(unit='ms')}",
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
        f"http://wgeo.weather.com.cn/ip/?_={get_time(unit='ms')}",
        headers={
            "user-agent": get_ua(),
            'Referer': "http://www.weather.com.cn/",
        }).content.decode('utf-8')
    geo_id = re.search(r'id="(\d+)"', resp).group(1)
    if not geo_id:
        raise KeyError
    return geo_id



