# lite-tools


![](https://img.shields.io/badge/python-3.8-brightgreen)
![](https://img.shields.io/github/watchers/Heartfilia/lite_tools?style=social)
![](https://img.shields.io/github/stars/Heartfilia/lite_tools?style=social)
![](https://img.shields.io/github/forks/Heartfilia/lite_tools?style=social)

## 特别声明: 目前均为**测试版本**,主要是探索新功能的，不保证稳定性和性能
### 不出意外会在正式版(1.0.0)的时候修复成稳定版本.
> 0.4.14.*  版本是ai修复校验过的版本，不保证稳定性


### 项目说明

**有空随缘更新一下**
> python 3.7+   // 什么年代了 该不会还有人还在用3.6及以下叭 0.4.10.0 版本再次兼容了3.6 3.7 版本

### Installation
```bash
pip install lite-tools
```

### SQL 工具的使用约定

`SqlString`、`MySql`、`AioMySql` 的类名、方法名和调用参数保持不变：

```python
from lite_tools import SqlString

sql = SqlString("users")
statement, rows = sql.insert({"id": 1, "name": "O'Reilly"})
# cursor.executemany(statement, rows)
statement, rows = sql.update({"name": "new"}, {"id": 1})
# cursor.executemany(statement, rows)

# 下面这些接口仍返回可单独执行的 SQL 字符串，不改为元组。
statement = sql.count({"name": "O'Reilly"})
statement = sql.exists({"id": 1})
statement = sql.delete({"id": 1})
```

- `insert/update/replace` 返回 `(SQL模板, 参数行列表)`；通过驱动的
  `executemany()` 执行，不要自行拼接参数。`MySql` 的 CRUD 方法会自动处理，
  并返回驱动报告的真实影响行数（upsert 的影响行数不一定等于输入条数）。
- `delete/exists/count/create_table/select` 仍返回字符串。为兼容独立执行，字典中的
  文本值使用 UTF-8 十六进制字面量转换，避免依赖服务器反斜杠转义模式；
  `MySql.delete/exists/count` 内部则直接使用驱动参数化查询。
- 更新、删除必须有非空条件。`None`、`{}`、空字符串、空列表或错误类型会报错，
  不会退化为整表操作。确实需要全表操作时必须显式使用可信条件 `"1=1"`。
  `count(None)` / `count({})` 统计全表；`exists(None)` / `exists({})` 判断表中是否有行。
- 批量数据必须非空，所有行的字段集合必须相同，字段顺序可以不同。
  批量更新只接受等长的字典条件列表，每个条件对应一条更新数据。
  单条更新的字符串条件列表表示各项加括号后通过 `AND` 连接。
- `duplicate_except=None` 不启用 upsert；`[]` 更新所有传入字段；非空列表排除指定字段。
  排除全部字段或写错字段名会报错；`ignore=True` 优先，生成 `INSERT IGNORE`。
- `replace(mapping)` 或 `replace([列名], [值])` / `replace([列名], [[值], ...])`
  均可使用。MySQL REPLACE 有删除后插入语义，不等同于 UPDATE。
- `create_table()` 的字典值是完整字段定义，列表元素是完整字段/约束定义；
  默认值、ENUM 中的引号会原样保留。`select()` 支持基础投影、JOIN、WHERE、GROUP BY。
- 字典条件表示等值比较，不会把列表自动解释为 `IN`；集合和任意对象作为值会报错。
- 原始字符串条件、投影、JOIN、GROUP BY 和字段定义都是**可信 SQL 代码**，不能直接
  使用外部用户输入。片段检查不是 SQL 防火墙，数据库账号仍需最小权限。
- 执行失败会回滚并抛出异常，不再以 `0` / `None` 假装成功或无结果；日志失败不影响
  已提交写入。`execute(sql, args=[])` / `args=()` 不执行 SQL；无参数语句请省略 `args`。
- 流式读取会占用连接直到迭代结束；提前停止时请调用生成器的 `close()`，或使用
  `contextlib.closing()` 确保归还连接。`drop/truncate` 构造方法明确抛出 `NotImplementedError`。

本地回归测试（SQL 执行层测试需要安装 `lite-tools[net]` 依赖）：

```bash
python -m unittest discover -s tests -v
```

真实数据库测试默认跳过。仅在专用测试库上设置 `LITE_TOOLS_MYSQL_TEST_CONFIG`
（JSON 连接配置，字段为 `database/host/user/password` 等）后，才会创建和清理随机命名的
测试表，并验证普通 SQL 模式及 `NO_BACKSLASH_ESCAPES` 模式。不要指向生产数据库。

### Redis、缓存及 JSON 模板的安全约定

- `LiteRedis` 支持 JSON/YAML、`redis://`、`rediss://`（TLS）、URL 转义认证信息及 IPv6。
  YAML 使用安全加载器，且仅在读取 YAML 时才需要 PyYAML；配置必须是字典。
- `keep_waiting=True` 现在表示**有限的只读重试**：默认最多尝试 3 次、重试时间预算
  30 秒、间隔由 `timeout` 决定。可经现有 `**kwargs` 设置 `retry_attempts`、
  `retry_deadline`。单次网络等待仍由 `socket_timeout/socket_connect_timeout` 控制。
  写命令、未知命令不自动重放；认证失败、WRONGTYPE、参数错误直接抛出，失败不再返回
  含糊的 `None`。底层 redis-py 自动重放也已禁用；自带连接池应自行遵守相同策略。
- 写入超时可能表示“服务端已执行但响应丢失”，不要直接重试计数、弹出等非幂等操作。
  `scan_iter/sscan_iter/hscan_iter/zscan_iter` 逐页重试当前游标；SCAN 本身仍可能返回重复项，
  不提供快照或恰好一次语义。`pipeline()` 直接返回原生管道，其执行异常由调用方处理。
- `BloomFilter.exists()` 现在检查所有哈希位；`remove()` 精确删除当前配置的全部分区，
  不使用通配符。位容量必须是 `1..2**32` 中的 2 的幂，分区数为 `1..256`。
  为兼容旧数据，合法配置的哈希和分区规则不变；同一 key 必须始终使用相同配置。
- `LiteCacher.cached()` 根据函数实际绑定参数计算有类型区分的缓存键，支持位置参数、
  关键字参数及默认值规范化；`main_key` 从本次调用取值，缺失参数报错。
  **main_key 只包含你指定的参数**：用户/租户/权限等会影响结果的参数必须包含进去。
  函数、闭包及不同实例隔离；实例方法不跨进程共享缓存。无法安全表示的参数跳过缓存，
  不使用含糊的 `str(obj)`。键使用新 `v2` 命名，旧缓存不会被读取，可等待原 TTL 到期。
- 内存缓存加锁、复制可变结果并按 TTL 过期，默认最多 1024 项；可通过现有 `**kwargs`
  设 `max_entries`。Redis 缓存读失败或内容损坏按未命中处理，不影响业务函数；同步函数
  配异步 Redis 时使用内存，异步函数配同步 Redis 时网络调用移入工作线程。
  缓存仍不是分布式锁，不保证并发未命中时业务函数只执行一次。
- `WrapJson` 不再执行 `exec()`，模板键始终按字典键处理，支持引号、点号、方括号等。
  `...` 必须匹配存在的标量（可为 `None`），不匹配集合。类型叶子 `list/dict` 保留整个
  集合；嵌套列表模板按下标投影；字典模板处理输入列表时筛选匹配记录。
- `check_proxy()` 修复异步调用和连接关闭，只检查 TCP 可达性，不代表代理认证或协议可用。

真实 Redis 集成测试默认跳过。仅在专用测试实例设置 `LITE_TOOLS_REDIS_TEST_URL` 后启用，
测试只创建、清理随机前缀的键，不执行 `FLUSHDB`。

### 命令行指令
```bash
lite-tools [-h]   # 可以获取帮助 我这里就不展示更多了
```

#### 真的懒得写文档 直接看源码 直接点这里 [`__init__.py`](https://github.com/Heartfilia/lite_tools/blob/master/lite_tools/__init__.py)

#### 还有稍微详细的查询工具网站，持续更新的 [lite-tools](https://www.yuque.com/heartfilia/oip3kg/egpxli)

#### 或者部分demo见 [demo.py](https://github.com/Heartfilia/lite_tools/tree/master/demo)
