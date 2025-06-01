import os
import re
import socket
import asyncio
import platform
import telnetlib3
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


async def check_proxy(proxy: str, timeout=3, log: bool = False) -> bool:
    """
    异步校验代理有效性（基于 telnetlib3）

    :param proxy: 代理地址（支持带认证信息）格式: user:pass@ip:port 或 ip:port
    :param timeout: 连接超时时间（秒）
    :param log: 是否输出日志
    :return: 代理是否有效

    ------------------------
    # 异步批量检测代理
    async def batch_check_proxies(proxies):
        tasks = [check_proxy_async(p, log=True) for p in proxies]
        results = await asyncio.gather(*tasks)
        return {p: valid for p, valid in zip(proxies, results)}
    """

    def extract_info(pro: str) -> Tuple[str, int]:
        """提取代理IP和端口"""
        if "@" in pro:
            pro = pro.split("@")[-1]
        pro = re.sub(r"^https?://", "", pro)
        ip_port = pro.split(":")
        if len(ip_port) != 2 or not ip_port[1].isdigit():
            return "", 0
        return ip_port[0], int(ip_port[1])

    if not isinstance(proxy, str):
        return False

    ip, port = extract_info(proxy)
    if not ip or port == 0:
        return False

    try:
        # 异步建立连接（核心改造点）[1,2](@ref)
        async with telnetlib3.open_connection(
                host=ip,
                port=port,
                connect_maxwait=timeout
        ) as client:
            # 连接成功即认为代理有效
            if log:
                print(f"[{proxy}] 连接成功，代理有效")
            return True

    except (ConnectionRefusedError, asyncio.TimeoutError, OSError) as e:
        if log:
            print(f"[{proxy}] 连接失败: {str(e)}")
        return False
    except Exception as e:
        if log:
            print(f"[{proxy}] 未知错误: {str(e)}")
        return False


if __name__ == "__main__":
    print(get_lan())
