# Retrieval Loop（检索→阅读→改 Query→再检索）

## 解决的问题

一次检索常常漏掉关键证据。Retrieval loop 通过“发现缺口→改写 query”迭代提升覆盖。

## 核心流程

```mermaid
flowchart TD
  Q["Question"] --> G["Propose query"]
  G --> S["Search"]
  S --> N["Notes (dedup evidence)"]
  N --> D{"Enough evidence?"}
  D -->|no| G
  D -->|yes| A["Answer with citations"]
```

## 什么时候用

- 第一次检索经常不全或偏题。
- 你需要多来源证据来建立置信度。
- 你把“搜索”当作迭代过程，而不是一次 tool call。

## 它是如何运作的

1. 从问题生成初始 query。
2. 检索文档/片段。
3. 维护一个 **notes / evidence** 结构（去重、记录 doc_id）。
4. 判断证据是否足够；不够就根据“缺口”改写 query 再检索。
5. 最终基于证据回答，并给出引用。

## 常见失败模式与对策

- **Query 漂移**（越搜越偏）：保持稳定目标描述；限制改写范围。
- **重复检索**：按 doc_id/hash 去重；对 query 做缓存。
- **检索内容注入**：加 guardrails；把“证据”与“指令”隔离。
- **无限搜索**：设预算（最大 query 次数/时间/token）。

## 演化路径

- 来源：classic RAG（一次检索→一次生成）
- 走向：Agentic RAG（检索变成 agent loop 的一个工具）

## 本仓库对应

- 代码： [`src/agent_patterns_lab/patterns/retrieval_loop.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/retrieval_loop.py)
- 示例： [`examples/40_retrieval_loop.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/40_retrieval_loop.py)
- 测试： [`tests/test_retrieval_loop.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_retrieval_loop.py)
