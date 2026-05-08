# Handoff（分诊 / 升级）

## 解决的问题

当前 agent 可能不是最佳“负责人”：

- 专长不匹配
- 权限/工具不匹配
- 风险级别不匹配

Handoff 把升级变得显式：**交接给谁 + 交接摘要**。

## 什么时候用

- 当前 agent 缺少专长/工具/权限（硬做只会瞎猜）。
- 错的代价很高，需要明确升级路径与责任边界。
- 你希望交接过程可审计、可复盘。

## 什么时候别用

- 一开始就能确定该找谁 → 做**确定性路由**，别让 handoff 连跳。
- 你希望主控 agent 始终是 owner，只是委派子任务 → 用 **agents-as-tools**。
- 你无法防止 handoff loop → 先加 manager/moderator（或保持单 agent）。

## 核心流程

```mermaid
flowchart TD
  U["Task"] --> R["Router / Triage"]
  R -->|handle| A0["Current agent answers"]
  R -->|handoff + summary| A1["Specialist agent"]
  A1 --> O["Answer"]
  A0 --> O
```

## 它是如何运作的

高质量 handoff 的关键是 **短而结构化的交接摘要**：

- 用户意图与约束
- 已尝试过什么
- 关键产物（链接/文件/中间结果）
- 未决问题与下一步动作

这样 specialist agent 可以快速接手，而不是从头读完整对话。

### 机制细节（让交接更安全）

- **summary schema**：定义必填字段（意图/约束/产物/未决问题）。
- **路由信号**：置信度阈值 + 能力边界（工具权限、语言、领域）。
- **loop 控制**：限制最大 handoff 次数；记录“为什么交接、交接给谁”。
- **权限边界**：handoff 不得绕过工具策略；权限应该按 agent 显式配置。

## 一个能对照的例子

```bash
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python examples/64_handoff.py
```

## 常见失败模式与对策

- **上下文丢失**：统一 handoff summary schema；确保关键产物齐全。
- **来回踢皮球**：明确 ownership；限制 handoff 深度；必要时引入 manager 仲裁。
- **绕过权限**：与 policy/guardrails 结合，handoff 不能变相提权。
- **过度交接**：只有在低置信或“错的代价很高”时才 handoff。

## 演化路径

- 属于“在 agent 间 routing”的模式（与 manager-worker 很搭）
- 常与治理结合：不同 agent 具备不同权限

## 本仓库对应

- 代码： [`src/agent_patterns_lab/patterns/handoff.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/handoff.py)
- 示例： [`examples/64_handoff.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/64_handoff.py)
- 测试： [`tests/test_handoff_pattern.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_handoff_pattern.py)

## 参考资料

- Azure Architecture Center — Handoff orchestration：https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
- Microsoft Agent Framework — Handoff orchestration：https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/handoff
