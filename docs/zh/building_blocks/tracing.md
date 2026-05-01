# Tracing（可回放的可观测性）

## 解决的问题

没有 trace，Agent 很难 debug：

- 模型究竟看到了什么？
- 调了哪些工具？输出是什么？
- 卡在了哪里？为什么停不下来？

Tracing 把一次运行变成 **JSONL 事件流**，可回放、可对比、可做回归。

## 建议记录的事件

- 模型调用（输入/输出）
- 工具调用与结果
- loop step 与终止原因
- policy/guardrail/HITL 的拦截事件

## 本仓库对应代码

- 实现：`src/agent_patterns_lab/runtime/tracing.py`
- 输出：`.traces/*.jsonl`

