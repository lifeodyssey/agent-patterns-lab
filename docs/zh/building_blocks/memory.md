# Memory（KV / Session）

## 解决的问题

长周期 Agent 需要“状态”。不然每次运行都像失忆：

- 经验教训（Reflexion）
- 用户偏好
- 中间产物与进度
- 中断恢复（interrupt/resume）

本仓库从最小、显式的 memory store 起步（KV + JSON session）。不搞“玄学记忆”，就是可读、可测的数据结构。

## 它是如何运作的（本仓库实现）

两块积木：

- **KV store**：按 key 取值
  - `InMemoryKV`：进程内，适合 tests/examples
  - `JsonFileKV`：用一个 JSON 文件做持久化 KV
- **Session store**：保存/恢复一次运行的快照
  - `JsonFileSessionStore`：`save(session_id, state)` / `load(session_id)`

## 什么时候用 / 什么时候别用

KV 适合存：

- 稳定偏好（`timezone`、`tone`、`tool_allowlist`）
- 可复用的“教训”（Reflexion 的 do/don’t）

Session 适合用在：

- 需要中断恢复的流程（HITL 审批、崩溃、超时）
- 需要复盘/debug 的流程（“第 7 步 state 是什么？”）

不建议存：

- 没有 policy 的隐私/密钥（尤其是落盘）
- 体积很大的 blob（JSON 文件会把你拖死）
- 未验证的“模型自述想法”（更建议存事实/证据，而不是情绪）

## 一个能对照的例子

```python
from pathlib import Path

from agent_patterns_lab.runtime.memory import InMemoryKV, JsonFileSessionStore

kv = InMemoryKV()
kv.set("user.tone", "direct")
kv.set("user.timezone", "Asia/Shanghai")

sessions = JsonFileSessionStore(root=Path(".sessions"))
sessions.save(
    "run-001",
    {
        "step": 7,
        "ledger": [{"id": "t1", "status": "done"}],
        "notes": "waiting for approval",
    },
)

state = sessions.load("run-001")
assert state["step"] == 7
```

## 常见失败模式与对策

- **记忆过期**：key 加版本（`v1/user.tone`）；或者存时间戳并设置过期策略。
- **schema 漂移**：把落盘 JSON 当成“API”，需要迁移就显式写迁移。
- **记忆注入**：把“事实”与“指令”隔离（和 evidence ledger 的思路一样）。

## 本仓库对应代码

- KV： [`src/agent_patterns_lab/runtime/memory/kv.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/memory/kv.py)
- Session： [`src/agent_patterns_lab/runtime/memory/session.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/memory/session.py)
- 测试： [`tests/test_memory.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_memory.py)
