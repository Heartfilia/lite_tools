import os
import re
import socket
import platform
import telnetlib
from typing import Tuple

from lite_tools.logs import logger


"""
用最简单的方法实现读取本地的网络 --> 目前仅支持中国地区 并且只支持IPV4  V6以后作为参数配置 那以后再说
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
    ip_reg = None
    if platform.system() == "Windows":
        txt = get_command_result("ipconfig")
        for name, temp_ip in re.findall(
                r"(以太网适配器.*?:).*?IPv4\s?地址.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", txt, re.S | re.I
        ):
            if "WSL" not in name:
                return temp_ip
        # ip_reg_1 = re.search(r"(\d+\.\d+\.\d+\.\d+)", txt, re.S | re.I)
        # 其它情况写这里
    else:
        txt = get_command_result("ifconfig")
        ip_reg_0 = re.search(r"(?=eth0|en0).*?\n\s+inet\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", txt)
        # 如果有不同情况的方案二就放这里
        ip_reg = ip_reg_0
        if not ip_reg:
            ip_reg_1 = ""
            for temp_ip in re.findall(r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) ", txt):
                if temp_ip == "127.0.0.1":
                    continue
                ip_reg_1 = temp_ip
                break
            if ip_reg_1:
                return ip_reg_1
    if not ip_reg:
        # 如果没有匹配到内容那么就走系统自带的方法
        logger.warning('获取内网ip通过正则获取失败，希望你能把你当前pc的特殊情况发给我,我这里先返回系统方法获取的ip给到你')
        ip = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
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
        import requests
    except ImportError:
        from lite_tools.utils.pip_ import install
        install('requests')
        import requests
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


def check_proxy(proxy: str, timeout=3, log: bool = False) -> bool:
    """
    传入代理 校验代理是否有效
    :param proxy  : 代理用字符串传入就好了 带不带账密都可以 example: xxxx:xxx@iiii:ppp or iiii:ppp 都可以
    :param timeout: 校验超时 超过时间 即认定失效
    :param log    : 是否打印出结果日志 默认不打印
    """
    def extract_info(pro: str) -> Tuple[str, int]:
        if "@" in pro:
            pro = pro[pro.index("@")+1:]
        pro = re.sub("^https?://", "", pro)
        ip_port = pro.split(":")
        if len(ip_port) != 2 or not ip_port[1].isdigit():
            return "", 0
        return ip_port[0], int(ip_port[1])

    if not isinstance(proxy, str):
        return False
    ip, port = extract_info(proxy)
    try:
        telnetlib.Telnet(ip, port, timeout=timeout)
        if log:
            logger.success(f"[{proxy}] 可以成功访问，判定有效。")
        return True
    except Exception as err:
        _ = err
        if log:
            logger.warning(f"[{proxy}] 不可访问，暂定失效。")
        return False


if __name__ == "__main__":
    print(get_lan())
