# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:25
# @Author : Lodge
from sys import version_info
from setuptools import setup

from lite_tools.version import VERSION


if version_info < (3, 6, 0):
    raise SystemExit("Sorry! lite_tools requires python 3.6.0 or later.")


with open("README.md", "r", encoding='utf-8') as fd:
    long_description = fd.read()

base_requires = [
    'loguru',          # 基本的日志打印相关的调用
    # "tls-client",      # 替换requests用的
    "pydantic",        # 神器,不多说 一般你装其它的包这个也会被装，我这里只是避免提示
    'colorama',        # 其实colorama也是包含在了loguru里面的 这里不写 ide自检测会提示我没有这东西
    "prettytable",     # 基本的展示一些操作的模块
    "datetime",        # 谁没有一个datetime模块啊
    # "func_timeout",    # 用一个try上面 但是这个包没有封装好
    # 'httpx[http2]',    # 封装一个更加方便的请求模块的时候兼容h2 所以这里被迫装了一个 暂时没有用到
]

# 所有和网络有关的包可能都要判断一下了
net_requires = [
    'pymysql',         # mysql包全靠它 如果对版本介意 可以不管我这个  最好大于1.0.2
    "pyyaml",          # redis 那里读取配置文件要用这个
    "redis",           # redis 的一个东西需要用这个
    "requests",        # 请求模块，本来不想安装那么多东西的，现在谁没有一个requests啊
    'urllib3',         # 安装requests自动装的,主要是有个地方用到了它里面的解析模块,不写这里ide会提示
    "usepy",           # >> 米乐大佬的工具包，我只是用里面的部分功能二次封装，很多操作直接引用他的包就好了
    "lxml",            # 提取一些静态页面内容的时候要用这个
    'dbutils',         # MySQL池需要用  最好大于3.0.2
]

# 这里暂时没有用到 等以后搞文件操作的时候再完善这里
file_requires = [
    "reportlab",    # 这个是生成pdf的
    "Pillow",       # 这个是图像处理的
    # "pandas",       # 这东西没有用到
    # "xlsxwriter",   # 这东西也是只有pandas用到的时候才会用到
    # "numpy"         # 也米有用到
]

setup(
    name='lite-tools',
    version=VERSION.strip(),
    description='一些让你效率提升的小工具集合包[还在持续增加及优化]',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lodge',
    author_email='lodgeheartfilia@163.com',
    url='https://github.com/Heartfilia/lite_tools',
    packages=[
        'lite_tools',
        'lite_tools.commands',
        # 'lite_tools.commands.acg',      # 没弄好 不是太想弄了 就不一起打包进去了
        # 'lite_tools.commands.balls',    # 还没有调整好 先不放出来
        'lite_tools.commands.dictionary',
        'lite_tools.commands.flush',
        'lite_tools.commands.fresh',
        'lite_tools.commands.news',       # 新闻模块功能比较多 单独抽出来一个包搞
        'lite_tools.commands.today',
        'lite_tools.commands.trans',
        'lite_tools.commands.weather',
        'lite_tools.commands.whsecret',
        'lite_tools.exceptions',
        'lite_tools.logs',
        'lite_tools.tools',
        'lite_tools.tools.js',
        'lite_tools.tools.sql',
        'lite_tools.tools.core',
        'lite_tools.tools.time',
        # 'lite_tools.tools.http',   # 这个还在研发中
        'lite_tools.utils',
    ],
    license='MIT',
    install_requires=base_requires,
    entry_points={"console_scripts": [
        "lite-tools=lite_tools.commands.cmdline:execute",
    ]},
    python_requires=">=3.6",
    extras_require={
        "net": net_requires,
        "all": file_requires + net_requires,
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
    ]
)
