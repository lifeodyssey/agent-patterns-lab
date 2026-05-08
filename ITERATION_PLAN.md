# Iteration Plan — Agent Patterns Lab (Python, uv, no LangChain)

> 目标：用纯 Python（允许第三方库，但不依赖 LangChain / LangGraph 等框架）做一个 **离线可跑（MockLLM）** 的参考实现仓库，用代码理解并复现主流 Agent Design Patterns。  
> 约束：`examples/` 与 `tests/` 默认 **不需要 API key / 不需要网络**；真实模型适配器作为可选 extras。

**更新日期**：2026-04-25

---

## Repo 总体交付（最终形态）

- `docs/`：每个 pattern 的概念说明（解决的问题/适用边界/常见坑）+ Mermaid 流程图
- `src/agent_patterns_lab/runtime/`：最小运行时（模型接口、工具、runner、状态、ledger、memory、policy、guardrail、trace）
- `src/agent_patterns_lab/patterns/`：各模式的最小实现（尽量短、小、可组合）
- `examples/`：每个 pattern 一个 demo（默认 `MockLLM`）
- `tests/`：关键控制流与边界条件回归（`unittest`，离线可跑）

**依赖管理**：使用 `uv`（`pyproject.toml` + 可选 extras + `uv run ...`）。

---

## 迭代节奏与“完成标准”

每个 Iteration 都要满足：

1) **输入/输出明确**：本轮新增的模块、示例、文档与测试清单写清楚  
2) **离线可跑**：所有新增 `examples/` 和 `tests/` 默认使用 `MockLLM`  
3) **可观测**：新增/修改控制流需要能通过 `Trace` 看见关键事件  
4) **可组合**：模式实现尽量以“函数/类 + 小接口”拼装，不写隐式魔法

---

## Iter 0 — 脚手架 + 最小 Runtime（地基）

**输入**：空目录 + `AGENT_DESIGN_PATTERNS_REPORT.md`  
**输出**：

- `pyproject.toml`（uv 项目；可选 extras：`openai`、`anthropic`）
- `README.md`（如何用 `uv` 跑 examples/tests；离线优先）
- `src/agent_patterns_lab/runtime/`：
  - `model.py`：`Model` 接口（最小 `complete()`）
  - `mock_model.py`：`MockLLM`（脚本化/规则化返回）
  - `types.py`：消息与运行时类型（`Message`, `ToolCall`, `Action`…）
  - `tracing.py`：`Tracer`（span/event，JSONL 输出）
- `examples/00_single_shot.py`
- `tests/test_mock_model.py`

**验收**：
- `uv run python -m unittest discover -s tests` 通过
- `examples/00_single_shot.py` 能运行并输出结果 + trace

---

## Iter 1 — 结构化输出 + 基础 Workflow（稳定优先）

**输入**：Iter 0 runtime  
**输出**：

- `runtime/structured.py`：Schema 校验（推荐 `pydantic` 或轻量自写）+ repair/retry loop
- `patterns/workflow_chaining.py`：Prompt Chaining
- `patterns/routing.py`：Routing（规则路由 + LLM 路由）
- `examples/10_structured_output.py`
- `examples/11_prompt_chaining.py`
- `examples/12_routing.py`
- `tests/`：校验失败→修复重试、路由分支覆盖

**验收**：
- Structured 输出能稳定解析为类型
- 路由模式能在不同输入下走不同 flow

---

## Iter 2 — Tool Calling + Agent Loop（Reason-Act-Observe）

**输入**：Iter 1  
**输出**：

- `runtime/tools.py`：Tool registry + 调用协议（含参数校验）
- `runtime/runner.py`：通用 runner（max_steps/budget/timeout）
- `patterns/react.py`：ReAct（以 action schema 表达 tool/final/ask）
- `examples/20_tool_calling.py`
- `examples/21_react_loop.py`
- `tests/`：max_steps、工具失败处理、observation 写回

**验收**：
- 工具调用可追踪（trace）
- Agent loop 可控终止（budget/max_steps）

---

## Iter 3 — 验证 + 可靠性横切（让系统“稳”）

**输入**：Iter 2  
**输出**：

- `patterns/maker_checker.py`：Evaluator-Optimizer
- `patterns/voting.py`：Voting / Self-Consistency
- `patterns/cove.py`：Chain-of-Verification（claim→verify→fix）
- `runtime/reliability.py`：retry/backoff、fallback、circuit breaker
- `runtime/cache.py`：缓存（精确 key；语义缓存可后置）
- `examples/30_maker_checker.py`
- `examples/31_voting.py`
- `examples/32_cove.py`
- `tests/`：可恢复错误重试、熔断开关、降级链

**验收**：
- 同一输入多次运行结果可控（在 Mock 模式下确定性）
- 验证失败能驱动修复再输出

---

## Iter 4 — Memory + Agentic RAG（“边检索边写”）

**输入**：Iter 3  
**输出**：

- `runtime/memory/`：summary、KV、session（JSON/SQLite 二选一起步）
- `patterns/retrieval_loop.py`：检索→阅读→改 query→再检索
- `patterns/agentic_rag.py`：Agentic RAG（evidence ledger + stop条件）
- `patterns/reflexion.py`：失败→写入教训→下次读取
- `data/`：小型离线语料（用于 demo；不依赖网络）
- `examples/40_retrieval_loop.py`
- `examples/41_agentic_rag.py`
- `examples/42_reflexion.py`
- `tests/`：记忆读写策略、证据去重、stop 条件

**验收**：
- Agentic RAG 能在证据不足时迭代检索，证据足够时停止
- Session 能恢复运行状态（至少恢复 ledger/notes）

---

## Iter 5 — 规划与搜索类模式（更强推理与执行图）

**输入**：Iter 4  
**输出**：

- `patterns/plan_and_solve.py`
- `patterns/planner_executor_replanner.py`
- `patterns/rewoo.py`
- `patterns/llm_compiler.py`：计划→DAG→执行（含并行可选）
- `patterns/lats.py`：Tree Search（展开/评估/选择）
- `patterns/self_discovery.py`
- `patterns/storm.py`：研究写作（基于离线语料/工具）
- `examples/50_plan_and_solve.py`
- `examples/51_planner_executor_replanner.py`
- `examples/52_rewoo.py`
- `examples/53_llm_compiler.py`
- `examples/54_lats.py`
- `examples/55_self_discovery.py`
- `examples/56_storm.py`
- `tests/`：上述模式的离线回归测试

**验收**：
- replan 触发条件清晰可测（新证据/失败/预算）
- DAG 执行依赖正确

---

## Iter 6 — Multi-Agent + 治理（可协作、可上线）

**输入**：Iter 5  
**输出**：

- `patterns/manager_worker.py`：Orchestrator-Workers
- `patterns/agents_as_tools.py`
- `patterns/group_chat.py`：round-robin / selector
- `patterns/handoff.py`
- `patterns/magentic_orchestration.py`：task ledger + stall detection
- `runtime/guardrails.py`：input/output/tool guardrails + tripwire
- `runtime/hitl.py`：needs_approval、interrupt/resume（离线模拟）
- `runtime/policy.py`：allowlist/param bounds
- `examples/60_manager_worker.py`
- `examples/61_agents_as_tools.py`
- `examples/62_group_chat_round_robin.py`
- `examples/63_group_chat_selector.py`
- `examples/64_handoff.py`
- `examples/65_magentic_orchestration.py`
- `examples/66_governance_hitl_policy_guardrails.py`
- `tests/`：`test_policy.py`、`test_guardrails.py`、`test_hitl.py`、`test_manager_worker.py`、`test_agents_as_tools.py`、`test_group_chat.py`、`test_handoff_pattern.py`、`test_magentic_orchestration.py`

**验收**：
- 多 agent 编排可追踪、可复盘
- 高风险动作可被审批 gate 拦住并恢复

---

## Iter 7（可选）— 真实模型适配 + Eval Harness

**输入**：Iter 6  
**输出**：

- `pyproject.toml`：新增 `[project.optional-dependencies]`（`openai` / `anthropic`）
- `runtime/adapters/openai_model.py`（可选 extras；实现 `Model.complete()`）
- `runtime/adapters/anthropic_model.py`（可选 extras；实现 `Model.complete()`）
- `examples/70_openai_sdk_optional.py`（需要 `OPENAI_API_KEY`）
- `examples/71_anthropic_sdk_optional.py`（需要 `ANTHROPIC_API_KEY`）
- `tests/`：`test_openai_adapter.py`、`test_anthropic_adapter.py`（纯 stub，离线可跑）
- `runtime/evals/`：离线任务集 + 评分器 + 回归报告（含 `python -m agent_patterns_lab.runtime.evals` CLI）
- `tests/`：`test_evals_runner.py`（离线回归）

**验收**：
- 不装 extras 也不影响离线运行
- 装 extras 后可用同一套 runtime 跑真实 LLM

---

## Non-goals（明确不做）

- 不做 Web UI、不做 notebook 优化、不做“端到端产品”
- 不把任何框架（LangChain/LangGraph 等）当作核心依赖
- 不追求覆盖所有论文/冷门 pattern；重点是“大家常用 + 可复用核心代码”

---

## Iter 8（可选）— 文档质量流水线（review → revise → polish）

> 目标：把“写文档”也当作可迭代的工程流程，做到：每页可评分、可回归、可批量润色。

**输入**：`docs/` 现有页面  
**输出**：

- `runtime/editorial/`：review→revise→polish 流水线（每一步按 rubric 打分）
- Rubric（0–5 五维）：清晰度、可操作性、边界、例子质量、术语一致性
- CLI：`python -m agent_patterns_lab.runtime.editorial`
  - offline：启发式评分/建议（不改文档）
  - openai/anthropic：用真实模型做改写 + 复评
- 产物目录：
  - `.editorial/reports/`：每页 JSON 评分与建议
  - `.editorial/REPORT.md`：聚合报表（均分 + 低分页面）
  - `.traces/editorial/`：trace（JSONL）
- 站点页面：写作 Rubric 说明页（双语）

**验收**：
- offline 模式可离线跑通并产出聚合报告
- live 模式可在有 API key 时批量改写并复评
