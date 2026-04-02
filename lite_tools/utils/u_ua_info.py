# 这里存放各个浏览器的版本
# 这里是不参与浏览器外部参数筛选的 仅供下面 platform_data browser_data 使用

# 下面的内容会载入缓存文件位置 可以手动更新缓存 下面的东西是网络没有获取到的时候给的默认数据
versions = {
    "chromium": [
        "70.0.3538.16", "70.0.3538.67", "70.0.3538.97",
        "71.0.3578.137", "71.0.3578.30", "71.0.3578.33", "71.0.3578.80",
        "72.0.3626.69", "72.0.3626.7",
        "73.0.3683.20", "73.0.3683.68",
        "74.0.3729.6",
        "75.0.3770.140", "75.0.3770.8", "75.0.3770.90",
        "76.0.3809.12", "76.0.3809.126", "76.0.3809.25", "76.0.3809.68",
        "77.0.3865.10", "77.0.3865.40",
        "78.0.3904.105", "78.0.3904.11", "78.0.3904.70",
        "79.0.3945.16", "79.0.3945.36",
        "80.0.3987.106", "80.0.3987.16",
        "81.0.4044.138", "81.0.4044.20", "81.0.4044.69",
        "83.0.4103.14", "83.0.4103.39",
        "84.0.4147.30",
        "85.0.4183.38", "85.0.4183.83", "85.0.4183.87",
        "86.0.4240.22",
        "87.0.4280.20", "87.0.4280.87", "87.0.4280.88",
        "88.0.4324.27", "88.0.4324.96",
        "89.0.4389.23",
        "90.0.4430.24",
        "91.0.4472.101", "91.0.4472.19",
        "92.0.4515.107", "92.0.4515.43",
        "93.0.4577.15", "93.0.4577.63",
        "94.0.4606.113", "94.0.4606.41", "94.0.4606.61",
        "95.0.4638.10", "95.0.4638.17", "95.0.4638.54", "95.0.4638.69",
        "96.0.4664.18", "96.0.4664.35", "96.0.4664.45", "96.0.1054.53",
        "97.0.4692.20", "97.0.4692.36", "97.0.4692.71",
        "98.0.4758.48", "98.0.4758.80", "98.0.4758.102",
        "99.0.4844.17", "99.0.4844.35", "99.0.4844.51",
        "100.0.4896.20", "100.0.4896.60",
        "101.0.4951.15", "101.0.4951.41",
        "102.0.5005.27", "102.0.5005.61",
        "103.0.5060.24", "103.0.5060.53", "103.0.5060.134",
        "104.0.5112.20", "104.0.5112.29", "104.0.5112.79", "104.0.5112.81",
        "105.0.5195.19", "105.0.5195.52",
        "106.0.5249.21", "106.0.5249.61",
        "107.0.5304.18", "107.0.5304.62",
        "108.0.5359.22", "108.0.5359.71",
        "109.0.5414.25", "109.0.5414.74",
        "110.0.5481.30", "110.0.5481.77",
        "111.0.5563.19", "111.0.5563.41"
    ],
    "firefox": [version for version in range(70, 112)],
    "safari": ["12.1.2", "13.1.1", "14.1.2", "15.6.1", "16.6.1"]
}


WIN_CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"
WIN_FIREFOX = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0"
WIN_EDGE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 Edg/{tag}"
WIN_OPERA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 OPR/{tag}"
WIN_BRAVE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"

MAC_CHROME = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"
MAC_SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{tag} Safari/605.1.15"
MAC_FIREFOX = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0"
MAC_EDGE = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 Edg/{tag}"
MAC_OPERA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 OPR/{tag}"

LINUX_CHROME = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"
LINUX_FIREFOX = "Mozilla/5.0 (X11; Linux x86_64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0"
LINUX_EDGE = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 Edg/{tag}"

ANDROID_CHROME = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36"
ANDROID_EDGE = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36 EdgA/{tag}"
ANDROID_SAMSUNG = "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/21.0 Chrome/{tag} Mobile Safari/537.36"
ANDROID_OPERA = "Mozilla/5.0 (Linux; Android 12; V2145) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36 OPR/{tag}"

IPHONE_SAFARI = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{tag} Mobile/15E148 Safari/604.1"
IPHONE_CHROME = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{tag} Mobile/15E148 Safari/604.1"
IPHONE_EDGE = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/{tag} Mobile/15E148 Safari/605.1.15"
IPAD_SAFARI = "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{tag} Mobile/15E148 Safari/604.1"
IPAD_CHROME = "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{tag} Mobile/15E148 Safari/604.1"


platform_data = {
    "win": [
        {"chrome": WIN_CHROME},
        {"firefox": WIN_FIREFOX},
        {"ie": [
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko"
        ]},
        {"edge": WIN_EDGE},
        {"opera": WIN_OPERA},
        {"brave": WIN_BRAVE}
    ],
    "pc": [
        {"chrome": WIN_CHROME},
        {"safari": MAC_SAFARI},
        {"firefox": [WIN_FIREFOX, MAC_FIREFOX]},
        {"ie": [
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko"
        ]},
        {"edge": WIN_EDGE},
        {"opera": [WIN_OPERA, MAC_OPERA]},
        {"brave": [WIN_BRAVE, MAC_CHROME]}
    ],
    "desktop": [
        {"chrome": WIN_CHROME},
        {"safari": MAC_SAFARI},
        {"firefox": [WIN_FIREFOX, MAC_FIREFOX, LINUX_FIREFOX]},
        {"edge": [WIN_EDGE, MAC_EDGE, LINUX_EDGE]},
        {"opera": [WIN_OPERA, MAC_OPERA]},
        {"brave": [WIN_BRAVE, MAC_CHROME, LINUX_CHROME]}
    ],
    "linux": [
        {"chrome": [
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36",
            LINUX_CHROME
        ]},
        {"firefox": [
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0",
            LINUX_FIREFOX
        ]},
        {"edge": LINUX_EDGE},
        {"opera": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 OPR/{tag}"}
    ],
    "mac": [
        {"chrome": MAC_CHROME},
        {"safari": MAC_SAFARI},
        {"firefox": MAC_FIREFOX},
        {"edge": MAC_EDGE},
        {"opera": MAC_OPERA},
        {"brave": MAC_CHROME}
    ],
    "mobile": [
        {"chrome": [ANDROID_CHROME, IPHONE_CHROME, IPAD_CHROME]},
        {"edge": [ANDROID_EDGE, IPHONE_EDGE]},
        {"safari": [IPHONE_SAFARI, IPAD_SAFARI]},
        {"samsung": ANDROID_SAMSUNG},
        {"opera": ANDROID_OPERA}
    ],
    "android": [
        {"chrome": [
            ANDROID_SAMSUNG,
            "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36",
            ANDROID_CHROME
        ]},
        {"edge": ANDROID_EDGE},
        {"samsung": ANDROID_SAMSUNG},
        {"opera": ANDROID_OPERA}
    ],
    "ios": [
        {"chrome": [IPHONE_CHROME, IPAD_CHROME]},
        {"edge": IPHONE_EDGE},
        {"safari": [IPHONE_SAFARI, IPAD_SAFARI]}
    ],
    "iphone": [
        {"chrome": IPHONE_CHROME},
        {"edge": IPHONE_EDGE},
        {"safari": IPHONE_SAFARI}
    ],
    "ipad": [
        {"chrome": IPAD_CHROME},
        {"safari": IPAD_SAFARI}
    ],
    "tablet": [
        {"chrome": IPAD_CHROME},
        {"safari": IPAD_SAFARI}
    ]
}


browser_data = {
    "chrome": WIN_CHROME,
    "chromium": WIN_CHROME,
    "edge": WIN_EDGE,
    "safari": MAC_SAFARI,
    "firefox": WIN_FIREFOX,
    "ie": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "opera": WIN_OPERA,
    "brave": WIN_BRAVE,
    "samsung": ANDROID_SAMSUNG,
}
