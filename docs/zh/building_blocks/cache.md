# Cache（成本控制与回归稳定）

## 解决的问题

对 LLM/tool 调用做缓存，可以：

- 降低成本与延迟
- 稳定 eval（减少随机波动）
- 避免重复的昂贵工作

## 本仓库对应代码

- 实现： [`src/agent_patterns_lab/runtime/cache.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/cache.py)
- 测试： [`tests/test_cache.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_cache.py)

