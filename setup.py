# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:25
# @Author : Lodge
from setuptools import setup


with open("README.md", "r", encoding='utf-8') as fd:
    long_description = fd.read()


setup(
    name='lite-tools',
    version='0.4.6.6',
    description='一些python小工具||some little tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lodge',
    author_email='lodgeheartfilia@163.com',
    url='https://github.com/Heartfilia/lite_tools',
    packages=['lite_tools'],
    license='MIT',
    install_requires=['loguru'],
    classifiers=[
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Natural Language :: Chinese (Simplified)',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
    ]
)
