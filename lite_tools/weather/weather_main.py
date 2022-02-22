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
from lite_tools.lib_jar.lib_dict_parser import try_key

from lite_tools.weather.citys import city_data

"""


var cityDZ ={"weatherinfo":{"city":"广州","cityname":"guangzhou","temp":"6","tempn":"4","weather":"大雨","wd":"东北风转微风","ws":"3-4级转4-5级","weathercode":"d9","weathercoden":"n9","fctime":"202202200800"}};var alarmDZ ={"w":[]};var dataSK ={"nameen":"guangzhou","cityname":"广州","city":"101280101","temp":"5","tempf":"41","WD":"东北风","wde":"NE","WS":"2级","wse":"8km\/h","SD":"99%","sd":"99%","qy":"1021","njd":"6km","time":"21:10","rain":"2","rain24h":"2","aqi":"16","aqi_pm25":"16","weather":"中雨","weathere":"Moderate rain","weathercode":"d08","limitnumber":"","date":"02月20日(星期日)"};var dataZS ={"zs":{"date":"2022022018","ct_name":"穿衣指数","ct_hint":"冷","ct_des_s":"建议着棉衣加羊毛衫等冬季服装。","lk_name":"路况指数","lk_hint":"湿滑","lk_des_s":"路面湿滑，车辆易打滑，减慢车速。","dy_name":"钓鱼指数","dy_hint":"不宜","dy_des_s":"天气不好，有风，不适合垂钓。","cl_name":"晨练指数","cl_hint":"不宜","cl_des_s":"有较强降水，建议在室内做适当锻炼。","nl_name":"夜生活指数","nl_hint":"较不适宜","nl_des_s":"建议夜生活最好在室内进行。","gm_name":"感冒指数","gm_hint":"极易发","gm_des_s":"天气寒冷，湿度大风力强，易感冒。","gj_name":"逛街指数","gj_hint":"不适宜","gj_des_s":"有较强降水且风力较大，出门需带雨具。","pl_name":"空气污染扩散条件指数","pl_hint":"优","pl_des_s":"气象条件非常有利于空气污染物扩散。","tr_name":"旅游指数","tr_hint":"一般","tr_des_s":"风大天凉，有较强降雨需带雨具。","co_name":"舒适度指数","co_hint":"较不舒适","co_des_s":"白天风力较强，偏冷，注意保暖。","pj_name":"啤酒指数","pj_hint":"不适宜","pj_des_s":"天气寒冷，可少量饮用常温啤酒。","hc_name":"划船指数","hc_hint":"不适宜","hc_des_s":"天气不好，建议选择别的娱乐方式。","gl_name":"太阳镜指数","gl_hint":"不需要","gl_des_s":"白天能见度差不需要佩戴太阳镜","uv_name":"紫外线强度指数","uv_hint":"最弱","uv_des_s":"辐射弱，涂擦SPF8-12防晒护肤品。","wc_name":"风寒指数","wc_hint":"冷","wc_des_s":"风力较大，感觉有点冷，室外活动要穿厚实一点，年老体弱者要适当注意保暖。","pk_name":"放风筝指数","pk_hint":"不宜","pk_des_s":"天气不好，不适宜放风筝。","ac_name":"空调开启指数","ac_hint":"较少开启","ac_des_s":"体感舒适，不需要开启空调。","ls_name":"晾晒指数","ls_hint":"不宜","ls_des_s":"有较强降水会淋湿衣物，不适宜晾晒。","xc_name":"洗车指数","xc_hint":"不宜","xc_des_s":"有雨，雨水和泥水会弄脏爱车。","xq_name":"心情指数","xq_hint":"差","xq_des_s":"有较强降水，使人心情不佳，注意调节。","zs_name":"中暑指数","zs_hint":"无中暑风险","zs_des_s":"天气不热，在炎炎夏日中十分难得，可以告别暑气漫漫啦~","jt_name":"交通指数","jt_hint":"较差","jt_des_s":"有强降水且路面湿滑，注意控制车速。","yh_name":"约会指数","yh_hint":"不适宜","yh_des_s":"建议在室内约会，免去天气的骚扰。","yd_name":"运动指数","yd_hint":"较不宜","yd_des_s":"有降水，推荐您在室内进行休闲运动。","ag_name":"过敏指数","ag_hint":"极不易发","ag_des_s":"无需担心过敏。","mf_name":"美发指数","mf_hint":"适宜","mf_des_s":"风力较大空气干燥，注意清洁滋养头发。","ys_name":"雨伞指数","ys_hint":"带伞","ys_des_s":"较强降水，带雨伞，避免淋湿。","fs_name":"防晒指数","fs_hint":"弱","fs_des_s":"涂抹8-12SPF防晒护肤品。","pp_name":"化妆指数","pp_hint":"保湿","pp_des_s":"请选用滋润型化妆品。","gz_name":"干燥指数","gz_hint":"适宜","gz_des_s":"风速偏大，气温适宜，但体感温度会低一些，建议多使用保湿型护肤品涂抹皮肤，预防皮肤干燥。"},"cn":"广州"};var fc ={"f":[{"fa":"09","fb":"09","fc":"6","fd":"4","fe":"东北风","ff":"无持续风向","fg":"3-4级","fh":"4-5级","fk":"1","fl":"0","fm":"999.9","fn":"89.4","fi":"2\/20","fj":"今天"},{"fa":"09","fb":"08","fc":"7","fd":"4","fe":"无持续风向","ff":"无持续风向","fg":"3-4级","fh":"3-4级","fk":"0","fl":"0","fm":"87","fn":"79.5","fi":"2\/21","fj":"星期一"},{"fa":"07","fb":"07","fc":"8","fd":"5","fe":"无持续风向","ff":"北风","fg":"3-4级","fh":"3-4级","fk":"0","fl":"8","fm":"82","fn":"74.2","fi":"2\/22","fj":"星期二"},{"fa":"01","fb":"00","fc":"14","fd":"6","fe":"北风","ff":"无持续风向","fg":"3-4级","fh":"<3级","fk":"8","fl":"0","fm":"79.9","fn":"58.6","fi":"2\/23","fj":"星期三"},{"fa":"00","fb":"00","fc":"17","fd":"7","fe":"无持续风向","ff":"无持续风向","fg":"<3级","fh":"<3级","fk":"0","fl":"0","fm":"91.9","fn":"51.5","fi":"2\/24","fj":"星期四"}]}
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
    request_weather(city_id, city)


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
    print(resp.content.decode('utf-8'))


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
