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
	"firefox": [version for version in range(70, 112)],  # 同chrome一样 只存70版本以上
	"safari": ["12.1.2", "13.1.1", "14.1.2"]
}

# 这里存放各个平台对应的浏览器内核
# 下面手机基本都只有chromium 是因为一样的 只有安卓和苹果的区分
platform_data = {
	"win": [
		{"chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"},
		{"firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0"},
		{"ie": [
			"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
			"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko"
		]},
		{"edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 Edg/{tag}"}
	],
	"pc": [
		{"chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"},
		{"safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{tag} Safari/605.1.15"},
		{"firefox": [
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 13.8; rv,{tag}.1) Gecko/20100101 Firefox/{tag}.1"
		]},
		{"ie": [
			"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
			"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko"
		]},
		{"edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 Edg/{tag}"}
	],
	"linux": [
		{"chrome": [
			"Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36",
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"
		]},
		{"firefox": [
			"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0",
			"Mozilla/5.0 (X11; Linux x86_64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0"
		]}
	],
	"mac": [
		{"chrome": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36"},
		{"safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{tag} Safari/605.1.15"},
		{"firefox": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.8; rv,{tag}.1) Gecko/20100101 Firefox/{tag}.1"},
		{"edge": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 Edg/{tag}"}
	],
	"mobile": [
		{"chrome": [
			"Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/{tag} Mobile Safari/537.36",
			"Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36 Edg/{tag}",
			"Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36 Edg/{tag}",
			"Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36"
		]}
	],
	"android": [
		{"chrome": [
			"Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/{tag} Mobile Safari/537.36"
			"Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36 Edg/{tag}",
			"Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36 Edg/{tag}",
			"Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36",
			"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Mobile Safari/537.36 Edg/{tag}",
		]}
	],
	"ios": [
		{"chrome": [
			"Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 Edg/{tag}",
			"Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/{tag}",
			"Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1 Edg/{tag}",
		]}
	]
}

# 浏览器的string 这里存了各种浏览器的拼接模板 需要结合version_data
browser_data = {
	"chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36",
	"edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{tag} Safari/537.36 Edg/{tag}",
	"safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{tag} Safari/605.1.15",
	"firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{tag}.0) Gecko/20100101 Firefox/{tag}.0",
	"ie": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
}
