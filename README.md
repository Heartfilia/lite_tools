# lite_tools
```
python version:
	3.6+   // 因为使用了f_string
requirements :
	loguru
```

### install

```bash
python setup.py install

# or   # then chose one version 选择是需要whl还是tar.gz的安装包
cd dist
pip install xxxxx

# or  # 可以直接通过pip安装 国内镜像可能会版本更新不及时 用国内镜像也可以
pip install lite-tools 
```



### Interface

```python
get_time()         # 时间操作 示例见demo.py
get_ua()           # 获取随机ua 
timec              # 时间统计装饰器

# ==============下面是推荐使用的功能===================
try_get()          # 获取*字典或者json串*里面的键的值 返回一个结果 没有默认返回None // 没有获取到期望类型也是None
try_get_by_name()  # 获取*字典或者json串*里面的键的值 返回一个列表 没有返回空列表 // 没有获取到期望类型也是空列表
# =================================
get_md5()          # 用md5加密 直接传入字符串就可以了 默认输出十六进制、可选二进制 也可选择输出大写
get_sha()          # 用sha加密 默认mode=256 可以选择其它加密模式
get_sha3()         # 用sha3加密 默认mode=256
get_b64e()         # 用baseXX加密 默认mode=64 可以输出字节串
get_b64d()         # 用baseXX解密 默认mode=64

# ==================================
# 新增两个异常捕获装饰器
try_catch
try_catch(log=False)

async_try_catch     
# 这个暂时不对外使用 还需要调整一下 如果要测试 可以用 
from lite_tools.try_decorater import async_try_catch

# Example in 'demo.py'  ||  示例见demo.py
```



see `demo.py`