# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:25
# @Author : Lodge
from setuptools import setup


setup(
    name='lite_tools',
    version='0.3.7',
    description='some little tools',
    author='Lodge',
    author_email='lodgeheartfilia@163.com',
    url='https://github.com/Heartfilia/lite_tools',
    packages=['lite_tools'],
    license='MIT',
    install_requires=['loguru', 'user_agent'],
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
