# -*- coding: utf-8 -*-
# @Time   : 2021-04-06 15:28
# @Author : Lodge
import json
import os
import random
import re
from typing import Dict, Iterable, List, Optional, Tuple, Union

from lite_tools.utils import VERSION
from lite_tools.utils.lite_dir import lite_tools_dir
from lite_tools.utils.u_ua_info import browser_data, platform_data, versions as default_versions


__all__ = [
    "get_ua", "generate_ua", "get_versions", "judge_ua", "lite_ua",
    "validate_versions_data", "reset_ua_cache"
]
__ALL__ = __all__

_DEFAULT_BROWSER = "chrome"
_BROWSER_VERSION_MAP = {
    "chrome": "chromium",
    "chromium": "chromium",
    "edge": "chromium",
    "opera": "chromium",
    "brave": "chromium",
    "samsung": "chromium",
    "firefox": "firefox",
    "safari": "safari",
}

__UA_CACHE: dict = {}   # 尽量减少io读取 用空间换时间


def _normalize_name(name: Optional[str]) -> str:
    if not isinstance(name, str):
        return ""
    name = name.strip().lower()
    alias_map = {
        "desktop": "desktop",
        "computer": "desktop",
        "windows": "win",
        "win32": "win",
        "win64": "win",
        "macos": "mac",
        "osx": "mac",
        "macbook": "mac",
        "iphoneios": "iphone",
        "ipadios": "ipad",
        "tabletpc": "tablet",
        "androidphone": "android",
        "iosphone": "iphone",
        "iospad": "ipad",
        "ff": "firefox",
        "mozilla": "firefox",
        "google": "chrome",
        "googlechrome": "chrome",
        "msedge": "edge",
        "edgechromium": "edge",
        "opr": "opera",
        "samsungbrowser": "samsung",
    }
    return alias_map.get(name, name)


def _choose_one(items: Iterable):
    items = list(items)
    if not items:
        raise ValueError("items must not be empty")
    return random.choice(items)


def _normalize_versions(raw_versions: Optional[dict] = None) -> Dict[str, List[str]]:
    source = raw_versions if isinstance(raw_versions, dict) else {}
    normalized: Dict[str, List[str]] = {}

    for browser, fallback_values in default_versions.items():
        values = source.get(browser, fallback_values)
        if not isinstance(values, list) or not values:
            values = fallback_values
        normalized[browser] = [str(value) for value in values if str(value)]
        if not normalized[browser]:
            normalized[browser] = [str(value) for value in fallback_values]

    chromium_versions = normalized.get("chromium", [])
    safari_versions = normalized.get("safari", [])
    normalized["chromium_desktop"] = chromium_versions
    normalized["chromium_mobile"] = chromium_versions
    normalized["safari_desktop"] = safari_versions
    normalized["safari_mobile"] = safari_versions

    return normalized


def validate_versions_data(raw_versions: Optional[dict]) -> bool:
    if not isinstance(raw_versions, dict):
        return False
    for browser in ("chromium", "firefox", "safari"):
        values = raw_versions.get(browser)
        if not isinstance(values, list) or not values:
            return False
    return True


def reset_ua_cache() -> None:
    global __UA_CACHE
    __UA_CACHE = {}


def _resolve_browser_version_key(browser: str, template: str = "") -> Optional[str]:
    browser_key = _BROWSER_VERSION_MAP.get(browser)
    if browser_key == "chromium":
        if re.search(r"(Mobile|Android|CriOS|EdgiOS|EdgA|SamsungBrowser)", template, re.I):
            return "chromium_mobile"
        return "chromium_desktop"
    if browser_key == "safari":
        if re.search(r"(Mobile|iPhone|iPad)", template, re.I):
            return "safari_mobile"
        return "safari_desktop"
    return browser_key


def _resolve_platform_templates(platform: str) -> List[Tuple[str, str]]:
    options = []
    for browser_item in platform_data.get(platform, []):
        if not isinstance(browser_item, dict):
            continue
        for browser, templates in browser_item.items():
            if isinstance(templates, list):
                options.extend((browser, str(template)) for template in templates if template)
            elif templates:
                options.append((browser, str(templates)))
    return options


def _resolve_browser_template(browser: str) -> str:
    template = browser_data.get(browser)
    if not template:
        return browser_data[_DEFAULT_BROWSER]
    return str(template)


def _build_ua_meta(platform: Optional[str], browser: str, template: str, version: Optional[str], ua: str) -> dict:
    return {
        "platform": platform or "",
        "browser": browser,
        "template": template,
        "version": version or "",
        "ua": ua,
    }


def _split_args(args: Tuple[str, ...]) -> Tuple[List[str], List[str], List[str]]:
    platforms: List[str] = []
    browsers: List[str] = []
    unknown: List[str] = []

    for raw_item in args:
        item = _normalize_name(raw_item)
        if not item:
            continue
        if item in platform_data:
            platforms.append(item)
        elif item in browser_data:
            browsers.append(item)
        else:
            unknown.append(str(raw_item))
    return platforms, browsers, unknown


def generate_ua(
    platform: Optional[str] = None,
    browser: Optional[str] = None,
    strict: bool = False,
    return_meta: bool = False
) -> Union[str, dict]:
    """
    更明确的 UA 生成入口。

    :param platform: 平台名，如 win/mac/linux/mobile/android/ios/pc
    :param browser: 浏览器名，如 chrome/edge/firefox/safari/ie
    :param strict: True 时传入非法 platform/browser 会抛异常
    :param return_meta: True 时返回包含 platform/browser/template/version/ua 的字典
    """
    platform = _normalize_name(platform)
    browser = _normalize_name(browser)

    if platform and platform not in platform_data:
        if strict:
            raise ValueError(f"unsupported platform: {platform}")
        platform = ""

    if browser and browser not in browser_data:
        if strict:
            raise ValueError(f"unsupported browser: {browser}")
        browser = ""

    selected_browser = browser or _DEFAULT_BROWSER
    selected_template = _resolve_browser_template(selected_browser)

    if platform:
        platform_options = _resolve_platform_templates(platform)
        if browser:
            platform_options = [item for item in platform_options if item[0] == browser]
        if platform_options:
            selected_browser, selected_template = _choose_one(platform_options)
        elif strict and browser:
            raise ValueError(f"unsupported browser/platform combination: {browser}/{platform}")

    ua, version = judge_ua(selected_browser, selected_template, return_version=True)
    if return_meta:
        return _build_ua_meta(platform, selected_browser, selected_template, version, ua)
    return ua


def get_ua(*args, return_meta: bool = False) -> Union[str, dict]:
    """
    兼容旧接口，同时支持平台和浏览器组合筛选。

    示例:
    - get_ua()
    - get_ua('win')
    - get_ua('chrome')
    - get_ua('win', 'chrome')
    """
    if not args:
        return generate_ua(return_meta=return_meta)

    platforms, browsers, _unknown = _split_args(args)
    platform = _choose_one(platforms) if platforms else None
    browser = _choose_one(browsers) if browsers else None
    return generate_ua(platform=platform, browser=browser, strict=False, return_meta=return_meta)


def judge_ua(browser: str, template: str, return_version: bool = False) -> Union[str, Tuple[str, str]]:
    """
    根据模板和版本库组装 UA。
    """
    if not isinstance(template, str) or not template:
        template = _resolve_browser_template(_DEFAULT_BROWSER)

    if not re.search(r"\{tag}", template):
        if return_version:
            return template, ""
        return template   # 如果没有匹配到证明是完整的ua 不需要组合

    version_key = _resolve_browser_version_key(_normalize_name(browser), template)
    version_pool = get_versions().get(version_key or "", [])
    if not version_pool:
        version = _choose_one(default_versions["chromium"])
    else:
        version = _choose_one(version_pool)

    ua = template.format(tag=version)
    if return_version:
        return ua, version
    return ua


def get_versions() -> dict:
    global __UA_CACHE
    if __UA_CACHE:
        return __UA_CACHE

    ua_path = os.path.join(lite_tools_dir(), "browser", "ua_version.json")
    loaded_versions = None
    if os.path.exists(ua_path):
        try:
            with open(ua_path, 'r', encoding='utf-8') as fp:
                loaded_versions = json.load(fp)
        except Exception:
            loaded_versions = None

    if not validate_versions_data(loaded_versions):
        loaded_versions = None

    __UA_CACHE = _normalize_versions(loaded_versions)
    return __UA_CACHE


def lite_ua(name=None) -> str:
    base_ua = f"python-lite-tools/{VERSION} Based On Script Engine"
    if name is not None:
        base_ua = f"{base_ua} {name}"
    return base_ua


if __name__ == "__main__":
    print(get_ua())
    print(get_ua('mobile'))
    print(get_ua('win'))
    print(get_ua('linux'))
    print(get_ua('ios'))
    print(get_ua('pc'))
    print(get_ua('chrome'))
    print(get_ua('edge'))
    print(get_ua('mac'))
    print(get_ua('win', 'chrome'))
