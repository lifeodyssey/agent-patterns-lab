# Design — Agent Patterns Lab（Python, uv, offline-first）

**日期**：2026-04-25  
**状态**：v0（设计确认后开始实现 Iter 0）

---

## 目标

- 用纯 Python 从 0 到 1 实现主流 Agent Design Patterns 的**最小参考代码**
- 默认离线可跑（MockLLM），让读者专注在“控制流/状态/边界”的核心代码
- 真实模型（OpenAI/Anthropic）只做**薄适配器**，不引入大型框架
- 每个 pattern 都配套：概念说明（Mermaid + 为什么存在）+ demo + 回归测试

## Non-goals

- 不做端到端产品与 UI
- 不引入 LangChain/LangGraph 作为核心依赖
- 不追求覆盖所有论文/冷门模式（以常用、可组合为主）

## 关键约束与设计选择

- **离线优先**：`examples/`、`tests/` 默认使用 `MockLLM`
- **可观测**：所有 runner/模式要能通过 `Tracer` 看到关键事件（LLM/tool/guardrail/handoff…）
- **可组合**：模式实现优先以“小接口 + 小模块”组合，不写隐式魔法
- **依赖管理**：使用 `uv`；extras 形式引入可选依赖（`openai`、`anthropic` 等）

## Repo 结构（目标形态）

- `AGENT_DESIGN_PATTERNS_REPORT.md`：模式全景大纲
- `ITERATION_PLAN.md`：迭代计划（每轮输入/输出/验收）
- `src/agent_patterns_lab/runtime/`：最小运行时
- `src/agent_patterns_lab/patterns/`：模式实现
- `examples/`：可运行 demo（离线）
- `tests/`：回归测试（离线）

## 下一步

按 `ITERATION_PLAN.md` 执行 Iter 0 → Iter 1 …（逐步扩展 patterns 与横切能力）。

