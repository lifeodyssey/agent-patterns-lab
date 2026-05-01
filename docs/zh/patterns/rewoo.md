# REWOO（Reasoning Without Observation）

## 解决的问题

工具 loop 往返多次会很慢/很贵。REWOO 通过“先规划所有工具调用 → 批量执行 → 一次汇总”减少往返。

## 核心流程

```mermaid
flowchart TD
  U["Task"] --> P["Plan tool_calls (JSON)"]
  P --> T["Run tools (batch)"]
  T --> S["Synthesize"]
  S --> O["Final"]
```

## 它是如何运作的

REWOO 用“少交互”换“少往返”：

1. 模型先把大部分工具调用规划出来（结构化列表）。
2. 系统批量执行工具调用（必要时可并行）。
3. 最后模型一次性读取全部 observation 并汇总出最终答案。

适用于：工具调用延迟/成本很高，且任务能较稳定地拆成相对独立的工具调用时。

## 常见失败模式与对策

- **没有观测时计划就错了**：计划要短；允许第二轮规划；不行就回退 ReAct。
- **缺少中途决策**：只把 REWOO 用在“工具调用相互独立”的问题上。
- **单个工具失败导致整批失败**：为每个工具加重试与部分结果处理。
- **过度检索/过度调用**：加预算与去冗余裁剪。

## 演化路径

- 当工具成本主导时，是 ReAct 的 workflow 替代
- 常配合验证（CoVe/Maker-Checker）

## 参考

- REWOO（Reasoning Without Observation）：Xu 等，2023。citeturn3search3

## 本仓库对应

- 代码： [`src/agent_patterns_lab/patterns/rewoo.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/rewoo.py)
- 示例： [`examples/52_rewoo.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/52_rewoo.py)
- 测试： [`tests/test_rewoo.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_rewoo.py)
