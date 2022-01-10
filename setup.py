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


base_requires = ['loguru']
# 这里暂时没有用到 -- 一些完整包的情况下的功能
file_requires = ["reportlab", "Pillow", "pandas", "xlsxwriter"]
date_requires = ["datetime", "lxml", "requests", "prettytable"]

all_requires = date_requires + file_requires


setup(
    name='lite-tools',
    version=VERSION.strip(),
    description='一些基于内建函数的小工具集合[更多拓展功能基于第三方包,安装参考github页面]',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lodge',
    author_email='lodgeheartfilia@163.com',
    url='https://github.com/Heartfilia/lite_tools',
    packages=[
        'lite_tools',
        'lite_tools.trans',
        'lite_tools.commands',
        'lite_tools.lib_jar',
        'lite_tools.utils_jar'
    ],
    license='MIT',
    install_requires=base_requires,
    entry_points={"console_scripts": [
        "lite-tools=lite_tools.commands.cmdline:execute",
    ]},
    python_requires=">=3.6",
    extras_require={
        "all": all_requires,
        "date": date_requires,
        "file": file_requires
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
