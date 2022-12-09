import os
import re
import socket
import platform

import requests


"""
用最简单的方法实现读取本地的网络 --> 目前仅支持中国地区
"""


def get_command_result(cmd: str) -> str:
    """这里只能执行ip相关操作"""
    if cmd not in ['ipconfig', 'ifconfig']:
        return ""
    r = os.popen(cmd)
    context = r.read()
    r.close()
    return context


def get_lan() -> str:
    """
    获取本机内网ip
    """
    if platform.system() == "Windows":
        txt = get_command_result("ipconfig")
        ip_reg_0 = re.search(r"以太网适配器.*?IPv4\s?地址.*?(\d+\.\d+\.\d+\.\d+)", txt, re.S | re.I)
        # ip_reg_1 = re.search(r"(\d+\.\d+\.\d+\.\d+)", txt, re.S | re.I)
        ip_reg = ip_reg_0  # or ip_reg_1
    else:
        txt = get_command_result("ifconfig")
        ip_reg_0 = re.search(r"eth0.*?\n\s+inet\s(\d+\.\d+\.\d+\.\d+)", txt)
        ip_reg = ip_reg_0
    if not ip_reg:
        # 如果没有匹配到内容那么就走系统自带的方法
        print('获取内网ip通过正则获取失败，希望你能把你当前pc的特殊情况发给我,我这里先返回系统方法获取的ip给到你')
        ip = socket.gethostbyname_ex(socket.gethostname())[-1][0]
    else:
        ip = ip_reg.group(1)

    return ip


wan_ip = ""


def get_wan(vps: bool = False) -> str:
    """
    获取本机外网ip,基于互联网,没有网络获取不到
    :param vps: 如果是vps 那么这个ip就不要存储了 默认不是 需要存储ip 这样不用频繁请求加快相应
    """
    global wan_ip
    if vps and wan_ip:
        return wan_ip
    try:
        resp = requests.get('http://httpbin.org/ip', timeout=5)
        result = resp.json()
        ip = result.get('origin', "")
        if vps and ip:
            wan_ip = ip
        return ip
    except Exception as err:
        _ = err
        return ""


if __name__ == "__main__":
    print(get_wan())
