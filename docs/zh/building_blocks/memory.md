# Memory（KV / Session）

## 解决的问题

长周期 Agent 需要“状态”：

- 经验教训（Reflexion）
- 用户偏好
- 中间产物与进度
- 中断恢复（interrupt/resume）

本仓库从最小、显式的 memory store 起步（KV + JSON session）。

## 本仓库对应代码

- KV：`src/agent_patterns_lab/runtime/memory/kv.py`
- Session：`src/agent_patterns_lab/runtime/memory/session.py`
- 测试：`tests/test_memory.py`

