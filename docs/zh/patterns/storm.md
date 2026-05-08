# STORM（研究写作：分段检索 + 组装）

## 解决的问题

研究写作不是一次 query：你需要先有结构，再逐段补证据，然后组装。

- 先 outline
- 每节独立检索证据
- 每节写作要落地到证据
- 最后 assemble

## 什么时候用

- 你要产出长文（文章/报告），而不是一次性回答。
- 你需要“按章节”组织证据（而不是把一坨 context 全塞给模型）。
- 你需要最后有一个 editor pass 来去冗余、调结构、补引用。

## 什么时候别用

- 用户只要一个短答案/快速查证 → retrieval loop / agentic RAG 就够。
- 你负担不起大量检索+写作调用 → STORM 天生高成本。
- 引用不重要 → STORM 的“按章证据”结构会变成负担。

## 核心流程

```mermaid
flowchart TD
  T["Topic"] --> O["Outline sections"]
  O --> S1["Section i: query + retrieve"]
  S1 --> W1["Write section with citations"]
  W1 --> N["Next section"]
  N -->|done| A["Assemble article"]
```

## 它是如何运作的

STORM 风格把“文章”当作结构化产物来生产：

1. 先产出 **大纲**（章节结构 + 每节关键问题）。
2. 对每一节：
   - 围绕本节问题做检索补证据
   - 用证据写出可落地的段落，并给出引用
3. 把各节组装为完整文章。
4. 可选：最后跑一轮 **编辑器**（一致性/冗余/语气/缺失引用）。

关键设计点：检索是 **按章节作用域** 来做的，可以显著减少“证据串台”。

### 机制细节（更像 STORM 的地方）

- **先做 pre-writing**：先把大纲质量当作 deliverable，别急着写正文。
- **每节独立检索**：每节有自己的问题清单与证据池。
- **每节独立账本**：证据 ledger 按节拆开，引用更可审计，也更不容易串台。
- **编辑器是可选但很值**：最后一轮专门做去冗余、调结构、查引用密度。

## 一个能对照的例子

```bash
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python examples/56_storm.py
```

## 常见失败模式与对策

- **大纲太浅**：用 rubric 迭代大纲（覆盖度、顺序、目标读者）。
- **证据混用**：每节维护独立 evidence ledger；按段落引用。
- **上下文溢出**：每节做摘要与笔记；不要把整份语料塞回去。
- **伪造引用**：引用必须来自 retriever 的 doc_id；对引用存在性做验证。

## 演化路径

- 基于 Retrieval Loop 家族
- 可与 Agentic RAG 结合（每节动态决定检索次数）

## 本仓库对应

- 代码： [`src/agent_patterns_lab/patterns/storm.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/storm.py)
- 示例： [`examples/56_storm.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/56_storm.py)
- 测试： [`tests/test_storm.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_storm.py)

## 参考资料

- Stanford STORM project：https://storm-project.stanford.edu/research/storm/
- Shao 等（2024）：Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models：https://arxiv.org/abs/2402.14207
- Agent Patterns — STORM pattern page：https://agent-patterns.readthedocs.io/en/stable/patterns/storm.html
