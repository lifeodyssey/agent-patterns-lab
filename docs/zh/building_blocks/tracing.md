# Tracing（可回放的可观测性）

## 解决的问题

没有 trace，Agent 很难 debug：

- 模型究竟看到了什么？
- 调了哪些工具？输出是什么？
- 卡在了哪里？为什么停不下来？

Tracing 把一次运行变成 **JSONL 事件流**，可回放、可对比、可做回归。

## 它是如何运作的（本仓库实现）

`Tracer` 故意做得很“朴素”：

- `tracer.emit(name, **data)`：追加一条事件（带时间戳）
- `tracer.export_jsonl(path)`：导出 JSONL，方便 diff / 回放

不搞复杂 exporter/OTel。先把“能复盘”做出来。

## 建议记录的事件

- 模型调用（输入/输出）
- 工具调用与结果
- loop step 与终止原因
- policy/guardrail/HITL 的拦截事件

## 什么时候用 / 什么时候别用

**适用：**

- 你在做 agent loop / multi-agent / RAG（没有 trace 基本没法复盘）。
- 你在做成本/延迟优化（需要知道 token/步骤/工具次数到底花在哪）。
- 你在做评测回归（trace 能帮你定位“分数掉了是哪里变了”）。

**不适用：**

- 你处理的是敏感数据但没有脱敏方案（先把数据治理补齐）。

## 一个能对照的例子

```python
from agent_patterns_lab.runtime import Tracer

tracer = Tracer()
tracer.emit("run.start", run_id="demo-001")
tracer.emit("tool.call", tool="search", args={"q": "react agent loop"})
tracer.emit("tool.result", tool="search", chars=1234)
tracer.emit("run.done", status="ok")

tracer.export_jsonl(".traces/demo.jsonl")
```

如果你把 `tracer=...` 传给模式实现（ReAct / RAG / …），就能看到模型调用、工具调用、loop step 等事件。

## 常见失败模式与对策

- **日志太大**：真实模型适配器里可用 `trace_content=False`（只记长度/元数据）。
- **PII/密钥泄露**：trace 视作敏感数据；必要时脱敏或避免记录原文。
- **难以对比**：事件名要稳定、结构要固定（别把信息都塞到一句字符串里）。

## 本仓库对应代码

- 实现： [`src/agent_patterns_lab/runtime/tracing.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/tracing.py)
- 输出：`.traces/*.jsonl`
