# 命令解释：`uv run` 到底在干嘛

文档里最常见的命令是：

```bash
uv run python examples/21_react_loop.py
```

它的意思是：**用 `uv` 管理的 Python 环境，运行这个示例文件。**

## 最推荐的命令

第一次读这个仓库，先用简单版：

```bash
uv run python examples/21_react_loop.py
```

如果它能跑，就不用管下面那些环境变量。

## 为什么有时会看到长版本

有些文档或 CI 会写成：

```bash
PYTHONPATH=src uv run --no-sync python examples/21_react_loop.py
```

拆开看：

| 片段 | 作用 | 什么时候需要 |
|---|---|---|
| `PYTHONPATH=src` | 告诉 Python 从 `src/` 目录找本仓库代码。 | 如果报 `ModuleNotFoundError`。 |
| `uv run` | 在 `uv` 管理的环境里运行命令。 | 基本都用它。 |
| `--no-sync` | 不自动同步/安装依赖，直接运行。 | 已经装好依赖、想快一点时。 |
| `python examples/21_react_loop.py` | 真正要执行的 Python 文件。 | 这是主角。 |

还有一个偶尔会出现的写法：

```bash
UV_CACHE_DIR=.uv_cache uv run ...
```

它只是把 `uv` 的缓存放到当前项目的 `.uv_cache/` 里，方便在某些沙盒或 CI 环境中隔离缓存。平时本地阅读不需要。

## 如果你不想记命令

可以把它理解成三层：

```text
uv run         # 用项目环境运行
python         # 启动 Python
examples/...   # 跑某个示例文件
```

这本小册子的重点不是 `uv`，而是示例文件里的控制流。

## 常见问题

**`uv: command not found`**

说明你本机还没装 `uv`。可以先安装 `uv`，或者用你自己的虚拟环境运行。

**`ModuleNotFoundError: agent_patterns_lab`**

说明 Python 没找到 `src/agent_patterns_lab`。用这个版本：

```bash
PYTHONPATH=src uv run --no-sync python examples/21_react_loop.py
```

**为什么不用 `python examples/...`？**

很多机器上 `python` 命令不存在，或者指向错误版本。`uv run python ...` 会在项目环境里找合适的 Python，更稳定。
