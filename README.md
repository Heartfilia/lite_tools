# lite_tools
```
python version:
	3.6+   // 因为使用了f_string
requirements :
	loguru
	user_agent
```

### install

```bash
python setup.py install

# or

pip install dist/lite_tools*

# or
# 如果没有替换到国内镜像 那么使用 国内镜像一般慢一天更新版本 
pip install lite-tools 
# 如果替换了国内镜像 那么使用
pip install -i https://pypi.org/simple lite-tools
```



### Interface

```python
get_time()         # 时间操作 示例见demo.py
get_ua()           # 获取随机ua 
get_navigator()    # 获取随机浏览器信息
try_get()          # 获取字典里面的键的值 返回一个结果 没有返回None // 没有获取到期望类型也是None
try_get_by_name()  # 获取字典里面的键的值 返回一个列表 没有返回空列表 // 没有获取到期望类型也是空列表
get_md5()          # 用md5加密 直接传入字符串就可以了 默认输出十六进制、可选二进制 也可选择输出大写
get_sha()          # 用sha加密 默认mode=256 可以选择其它加密模式
get_sha3()         # 用sha3加密 默认mode=256
get_b64e()         # 用baseXX加密 默认mode=64 可以输出字节串
get_b64d()         # 用baseXX解密 默认mode=64

# Example in 'demo.py'  ||  示例见demo.py
```



see `demo.py`