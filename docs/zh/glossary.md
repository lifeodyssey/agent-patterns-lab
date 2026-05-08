# 术语表（关键概念）

这份术语表用于统一本书中反复出现的关键名词与翻译方式。原则很简单：**英文术语第一次出现时保留，中文负责解释，不硬翻。**

如果你在某个页面看到同一个词被用成了别的意思，以这页为准。

## 解决的问题

Agent 系统“变复杂”的第一步，往往不是代码，而是术语开始漂：

- “agent” 和 “workflow” 被混用
- “tool calling” 和 “function calling” 被当成两件事
- “retrieval loop” 和 “agentic RAG” 说不清差别

双语站点里这种漂移更常见。这页的目标很朴素：**一个概念，一个名字，一套解释**，避免全书变成名词动物园。

## 什么时候用

- 你在读某个 pattern 页面，想快速对齐定义。
- 你在写/改页面，需要统一 EN↔ZH 翻译与术语。
- 你怀疑两个名词其实是一个东西（通常是）。

## 它是如何运作的（怎么用）

- 每个概念只保留 **一个主名词**。
- 常见同义词可以写在备注里，但不要拆成两条互相竞争的词条。
- 词条尽量短：1–2 句定义 + 1 条“容易混淆点”。
- 如果某个词条需要长段解释，说明它应该升级成单独页面。

## 一个能对照的例子（新增一个词条）

新增词条时至少补齐：

- 简短定义
- 1 条常见混淆点
- 1–3 条延伸阅读

示例：

```text
| **Tool policy（工具策略）** | 约束哪些工具能被调用（以及参数边界）。 | 通常 allowlist-first；配合 guardrails。 |
```

## 常见失败模式与对策

- **同义词泛滥**：强制一个主名词，同义词只做备注。
- **中英漂移**：把 EN/CH 当作一对文件，一次改动两边一起更新。
- **越写越像百科**：如果需要多段解释，拆成单独页面更清晰。

## 中文写法约定

| 英文术语 | 本书中文写法 | 不建议写法 | 为什么 |
|---|---|---|---|
| Agent | Agent / 智能体 | 代理 | “代理”容易和 proxy 混淆；中文读者也更习惯直接说 Agent。 |
| Workflow | 固定流程 / Workflow | 工作流（单独出现） | “工作流”太泛，最好强调“路径由代码固定”。 |
| Agent loop | Agent 循环 / Agent loop | 闭环、智能体闭环 | “闭环”可以解释，但不要当主名词。 |
| Observation | observation / 工具返回 | 观测 | “观测”太像机器翻译；代码里仍可保留 observation。 |
| Runtime | 运行时代码 / runtime | 运行时（孤立使用） | 这里指负责解析、执行、记录、停止的 Python 代码。 |
| Controller | 控制器 | 控制器程序 | 控制器即可，别写得太重。 |
| Multi-agent orchestration | 多 Agent 协作 / 编排 | 多智能体编排 | 可用，但不要每句都堆“编排”。 |
| Governance | 权限与护栏 / 治理 | 治理与安全（空泛） | 具体写成权限、审批、审计、护栏更好懂。 |
| HITL | 人工确认 / Human-in-the-loop | 人类在环 | “人类在环”直译感强；正文优先说人工确认。 |
| Evidence ledger | 证据清单 | 证据账本 | “账本”能用，但“证据清单”更像人话。 |

## 核心运行时概念

| 术语 | 简述 | 备注 |
|---|---|---|
| **Workflow（固定流程）** | 控制流由代码/配置固定（或有限分支）。 | 通常比 agent loop 更好测、更稳定。 |
| **Agent（智能体）** | 下一步由 LLM 基于当前 state 动态决定的控制器。 | 这里的 Agent 指控制流，不指“意识”。 |
| **Agent loop（Agent 循环）** | 决定下一步 → 执行工具 → 得到 observation → 更新 state → 重复。 | ReAct 是最典型形态。 |
| **State（状态）** | 控制器“看得见”的一切：messages + scratchpad/ledger + 相关记忆。 | 能结构化就结构化。 |
| **Action schema（动作格式）** | 用可解析的结构表达“下一步做什么”（tool/final/ask）。 | 避免靠文本正则解析。 |
| **Tool calling（工具调用）** | 选择工具/函数 + 传参 → 得到工具返回。 | 也常被叫做 function calling。 |
| **Observation（工具返回）** | 工具输出回写到 state，作为下一轮决策依据。 | 检索到的文本默认不可信。 |
| **Budget（预算）** | 硬限制：max steps / tool calls / tokens / 时间 / 成本。 | 防止 loop 失控。 |

## 检索与记忆

| 术语 | 简述 | 备注 |
|---|---|---|
| **Retrieval（检索 / RAG）** | 从外部知识库拿文档，把回答“落在证据上”。 | 传统 RAG 往往是“检索一次就回答”。 |
| **Retrieval loop（检索循环）** | 检索 → 阅读 → 改写 query → 再检索 → 直到够用再停。 | 面向搜索的专用 loop。 |
| **Agentic RAG** | 把检索放进 agent loop：模型决定何时检、检什么、何时停。 | 常配合“证据清单”做审计。 |
| **Evidence ledger（证据清单）** | 结构化记录：claim → evidence（doc_id/snippet/source）。 | 用来避免“引用摆设”并支持审计。 |
| **Memory（记忆）** | 跨 step 或跨 session 的持久化信息（KV、摘要、经验）。 | 长任务与 Reflexion 常用。 |
| **Episodic memory（情景记忆）** | 把一次运行的经验/教训以文本或结构化形式存起来。 | 类 Reflexion 的“无训练学习”。 |

## 可靠性与验证

| 术语 | 简述 | 备注 |
|---|---|---|
| **Maker-Checker（写-审）** | 先生成，再按准则批评/打分，再改写（可多轮）。 | 也叫 reviewer/critic。 |
| **Voting / 自洽投票** | 采样多个候选答案，再投票/排序/融合。 | 更稳但更贵。 |
| **CoVe（验证链）** | 先产出 claim，再验证 claim（工具/规则），失败就修。 | 把验证当作一等公民。 |
| **Retry / Backoff（重试退避）** | 失败后用延迟或调整参数重试。 | 需要配合预算 + 熔断。 |
| **Circuit breaker（熔断）** | 连续失败就停止或降级（工具故障/限流）。 | 防止“重试风暴”。 |

## 规划与搜索

| 术语 | 简述 | 备注 |
|---|---|---|
| **Plan & Solve** | 先显式产出计划，再执行/回答。 | 改善多步推理。 |
| **PER（Plan-Execute-Replan）** | 计划 → 执行 → 基于反馈/失败/预算触发重规划。 | 把 replan 显式化。 |
| **ReWOO** | “不看观测先推理”：先写工具计划，再批量执行工具。 | 可能比 ReAct 更省 token。 |
| **LLM Compiler** | 把计划编译成 DAG（依赖图），再按依赖执行。 | 有利并行与复用。 |
| **LATS（树搜索）** | 在多条轨迹上做搜索：展开/评估/回传，选更好的路径。 | 成本高，用于硬问题。 |

## 多智能体

| 术语 | 简述 | 备注 |
|---|---|---|
| **Manager-Worker** | 管理者分解任务并委派给专长 worker。 | 适合专业化 + 并行。 |
| **Agents-as-Tools** | 把每个专长 agent 当成可调用的 tool，让 orchestrator 统一调度。 | 简化路由与治理。 |
| **Group chat / Council（圆桌）** | 多个 agent 讨论/互评，最后由 selector 选择或融合。 | 可类比 debate/committee。 |
| **Handoff / Triage（分诊/交接）** | 根据线索把任务交给最合适的 agent（或人）。 | 避免“一个 agent 包打天下”。 |

## 治理、可观测、评测

| 术语 | 简述 | 备注 |
|---|---|---|
| **Policy（策略）** | 约束工具 allowlist、参数边界与权限（按任务/路由）。 | 建议“默认拒绝”。 |
| **Guardrails（护栏）** | 对输入/输出/工具调用的 tripwire：拦截、脱敏、要求审批。 | 处理注入、越权、泄露等。 |
| **HITL（人工确认）** | 对高风险动作进行人工确认（写入/花钱/prod）。 | 必须支持审批后继续执行。 |
| **Tracing（追踪）** | 结构化日志：步骤、工具调用、决策、耗时。 | 用于 debug 与评测。 |
| **Eval harness（评测框架）** | 可复现的任务集 + 打分 + 回归报告。 | 能“证明你变好了”。 |

## “人味”（文档写作）

| 术语 | 简述 | 备注 |
|---|---|---|
| **模板味** | 看起来像模板拼出来的低信息密度文字。 | 解决：加真实失败模式 + 能对照的例子。 |
| **禁用短语列表** | 明确禁止的“AI 腔”填充词。 | 最好在生成阶段就约束。 |

## 参考资料

- Agentic RAG（概览）：https://www.ibm.com/think/topics/agentic-rag
- Agentic RAG（术语解释风格）：https://exploreagentic.ai/glossary/agentic-rag/
- Agentic RAG（公共部门风险视角）：https://www.gov.uk/government/publications/ai-insights/ai-insights-agentic-rag-html
- Reflexion（论文）：https://arxiv.org/abs/2303.11366
- Plan-and-Solve（论文）：https://arxiv.org/abs/2305.04091
- ReWOO（论文）：https://arxiv.org/abs/2305.18323
- LATS（论文）：https://arxiv.org/abs/2310.04406
- “人味”写作习惯（实用）：https://www.microsoft.com/en-us/microsoft-copilot/copilot-101/humanize-ai-text
