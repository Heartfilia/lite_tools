# lite_tools
```
support python 3.6+
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
# 如果没有替换到国内镜像 那么使用
pip install lite-tools 
# 如果替换了国内镜像 那么使用
pip install -i https://pypi.org/simple lite-tools
```





```python
get_time()         # timestamp to strftime    strftime to timestamp
get_ua()           # random user_agent   
get_navigator()    # random navigator
try_get()          # get dict info
try_get_by_name()  # get dict info
```



see `demo.py`