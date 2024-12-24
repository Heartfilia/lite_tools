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
from lite_tools.utils.RequestsAdapter import ssl_gen as sync_ja3
from lite_tools.utils.AiohttpAdapter import ssl_gen as aio_ja3
from lite_tools.utils.HttpxAdapter import ssl_gen as httpx_ja3

"""
食用方案：headers 均为正常的headers
s = requests.Session()
s.headers.update(headers)
s.mount('https://ja3er.com', sync_ja3())
resp = s.get('https://ja3er.com/json').json()

async with aiohttp.ClientSession() as session:
    async with session.get("https://ja3er.com/json", headers={}, ssl=aio_ja3()) as resp:
        data = await resp.json()
        
async with httpx.AsyncClient(verify=httpx_ja3()) as client:
    resp = await client.get('https://ja3er.com/json')
    result = resp.json()

with httpx.Client(headers={}, http2=True, verify=httpx_ja3()) as client:
    response = client.get('https://ja3er.com/json')
    print(response.text)
"""
