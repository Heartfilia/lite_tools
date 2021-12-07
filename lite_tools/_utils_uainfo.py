# 这里存放各个浏览器的版本
# 这里是不参与浏览器外部参数筛选的 仅供下面 platform_data browser_data 使用
versions = {
	"fresh_date": "2021-11-23",
	"chromium": {
		"base_string": {
			"edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36 Edg/{}.0.864.67",
			"chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
			"android": [
				"Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36"
				"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67",
				"Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67",
				"Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67",
				"Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36 Edg/91.0.864.67",
				"Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36",
				"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36",
				"Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36",
				"Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36"
			],
		},
		"versions": {
			70: ["70.0.3538.16", "70.0.3538.67", "70.0.3538.97"],
			71: ["71.0.3578.137", "71.0.3578.30", "71.0.3578.33", "71.0.3578.80"],
			72: ["72.0.3626.69", "72.0.3626.7"],
			73: ["73.0.3683.20", "73.0.3683.68"],
			74: ["74.0.3729.6"],
			75: ["75.0.3770.140", "75.0.3770.8", "75.0.3770.90"],
			76: ["76.0.3809.12", "76.0.3809.126", "76.0.3809.25", "76.0.3809.68"],
			77: ["77.0.3865.10", "77.0.3865.40"],
			78: ["78.0.3904.105", "78.0.3904.11", "78.0.3904.70"],
			79: ["79.0.3945.16", "79.0.3945.36"],
			80: ["80.0.3987.106", "80.0.3987.16"],
			81: ["81.0.4044.138", "81.0.4044.20", "81.0.4044.69"],
			83: ["83.0.4103.14", "83.0.4103.39"],
			84: ["84.0.4147.30"],
			85: ["85.0.4183.38", "85.0.4183.83", "85.0.4183.87"],
			86: ["86.0.4240.22"],
			87: ["87.0.4280.20", "87.0.4280.87", "87.0.4280.88"],
			88: ["88.0.4324.27", "88.0.4324.96"],
			89: ["89.0.4389.23"],
			90: ["90.0.4430.24"],
			91: ["91.0.4472.101", "91.0.4472.19"],
			92: ["92.0.4515.107", "92.0.4515.43"],
			93: ["93.0.4577.15", "93.0.4577.63"],
			94: ["94.0.4606.113", "94.0.4606.41", "94.0.4606.61"],
			95: ["95.0.4638.10", "95.0.4638.17", "95.0.4638.54", "95.0.4638.69"],
			96: ["96.0.4664.18", "96.0.4664.35", "96.0.4664.45"],
			97: ["97.0.4692.20", "97.0.4692.36"]
		},
		"default_version": "90.0.4430.24",  # 这里是当上面的筛选都被排除了之后给定的默认版本值
	},
	"firefox": {
		"base_string": {},
		"version": [version for version in range(70, 97)],  # 同chrome一样 只存70版本以上
		"default_version": ""
	},
	"safari": {
		"base_string": {},
		"version": {},
		"default_version": ""
	},
	"ios": {
		"base_string": {},
		"version": {},
		"default_version": ""
	},
	"ie": {
		"base_string": {},
		"version": {},
		"default_version": ""
	},
	"opera": {
		"base_string": {},
		"version": {},
		"default_version": ""
	}
}

# 这里存放各个平台对应的浏览器内核
# 下面手机基本都只有chromium 是因为一样的 只有安卓和苹果的区分
platform_data = {
	"win": ["chrome", "firefox", "ie", "edge"],
	"pc": ["chrome", "firefox", "ie", "safari", "edge"],
	"linux": ["chrome", "firefox"],
	"mac": ["chrome", "firefox", "safari", "edge"],
	"mobile": ["chrome"],
	"android": ["chrome"],
	"ios": ["chrome"]
}

# 浏览器的string 这里存了各种浏览器的拼接模板 需要结合version_data
browser_data = {
	"chrome": {
		"mapping": "",
		"base": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36'
	},
	"edge": {
		"mapping": "",
		"base": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36 Edg/{}'
	},
	"safari": {
		"mapping": "",
		"base": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"]
	},
	"firefox": {
		"mapping": "",
		"base": [
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0 ",
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0 "
		]
	},
	"ie": {
		"mapping": "",
		"base": ""
	},
	"opera": {
		"mapping": "",
		"base": ""
	}
}

"""
上述操作的实现逻辑如下

输入参数 ---随机选择--[浏览器]--browser_data --随机选择--> versions ==> 可用ua
			|[系                   ↑
			↓ 统]     		       |
		platform_data --随机选择--[浏览器]
"""

ua_data = {}
