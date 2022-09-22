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


# 其实colorama也是包含在了loguru里面的 这里不写 ide自检测会提示我没有这东西
base_requires = [
    'loguru', 'urllib3', 'colorama', 'httpx', 'httpx[http2]', 'pymysql>=1.0.2', 'dbutils>=3.0.2',
    "func_timeout", "requests", "prettytable", "datetime", "lxml"
]
# 这里暂时没有用到 -- 一些完整包的情况下的功能  # 目前很多包没有用到 以后会用 先给大家装着
file_requires = ["reportlab", "Pillow", "pandas", "xlsxwriter", "numpy"]

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
        'lite_tools.commands.acg',
        # 'lite_tools.commands.balls',    # 还没有调整好 先不放出来
        'lite_tools.commands.news',      # 新闻模块功能比较多 单独抽出来一个包搞
        'lite_tools.commands.today',
        'lite_tools.commands.trans',
        'lite_tools.commands.weather',
        'lite_tools.tools',
        'lite_tools.tools.js',
        'lite_tools.tools.sql',
        'lite_tools.tools.core',
        'lite_tools.tools.time',
        'lite_tools.tools.utils',
        'lite_tools.exceptions'
    ],
    license='MIT',
    install_requires=base_requires,
    entry_points={"console_scripts": [
        "lite-tools=lite_tools.commands.cmdline:execute",
    ]},
    python_requires=">=3.7",
    extras_require={
        "all": file_requires,
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
