# lite-tools


![](https://img.shields.io/badge/python-3.6-brightgreen)
![](https://img.shields.io/github/watchers/Heartfilia/lite_tools?style=social)
![](https://img.shields.io/github/stars/Heartfilia/lite_tools?style=social)
![](https://img.shields.io/github/forks/Heartfilia/lite_tools?style=social)

## 特别声明: 目前均为测试版本,主要是探索新功能的，不保证稳定性和性能，会在正式版(1.0.0)的时候修复成稳定版本.


### 项目说明
```
等彩票 天气 的展示和采集问题弄完了后 就要停一段时间了 要学习下其它语言了 这工具先停止更新 预计规划的时间模块没有搞完的有空随缘更新一下
本项目基础功能只是封装了 - python**自带包**的功能 
-- loguru(打印日志的 -- 这个里面包含了colorma问题不大)
-- 1.0.0以下均为beta版本(就是为了试错 改bug的)
补充版功能依赖第三方包

```
```
python version:
    3.7+   // 因为使用了f_string 和一些类型声明 不确定3.6是否可以 应该可以吧
requirements :
    loguru
extral_requirements:
    datetime
    reportlab
    Pillow
```

### Installation

```bash
# 安装
【普通版】cmd/bash >> pip install --upgrade lite-tools        # 有的人的pip是pip3 一般的功能用这些就够了
---------------- 下面两个还没有正式启用 --------------
【完整版】cmd/bash >> pip install --upgrade lite-tools[all]   # 包含上面所有功能
```

### 命令行指令
```bash
lite-tools [-h]   # 可以获取帮助 我这里就不展示更多了
```

### 真的懒得写文档 直接看源码 那个入口 `__init__.py` 文件里面 `__ALL__` 有全部的功能额

更多见 [demo.py](https://github.com/Heartfilia/lite_tools/tree/master/demo)