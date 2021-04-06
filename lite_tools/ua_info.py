# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:28
# @Author : Lodge
from user_agent import generate_user_agent, generate_navigator, generate_navigator_js


def get_ua(*args, **kwargs):
    if not args:
        args = 'win'
    navigator = kwargs.get('navigator')
    platform = kwargs.get('platform')
    device_type = kwargs.get('device_type')
    return generate_user_agent(os=args, navigator=navigator, platform=platform, device_type=device_type)


def get_navigator(*args, **kwargs):
    if not args:
        args = 'win'
    navigator = kwargs.get('navigator')
    platform = kwargs.get('platform')
    device_type = kwargs.get('device_type')
    if kwargs.get('js') is True:
        return generate_navigator_js(os=args, navigator=navigator, platform=platform, device_type=device_type)
    return generate_navigator(os=args, navigator=navigator, platform=platform, device_type=device_type)
