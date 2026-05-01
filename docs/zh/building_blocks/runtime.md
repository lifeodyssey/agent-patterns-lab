# 运行时总览（可复用的“乐高积木”）

绝大多数模式，本质都是在复用一组运行时能力：

1. **消息格式**：最小对话结构（`system/user/assistant/tool`）。
2. **模型接口**：统一 `complete(messages) -> str`。
3. **结构化输出**：JSON 提取 + schema 校验 + 修复重试。
4. **工具调用**：注册工具与调用协议（可追踪、可审计）。
5. **loop 控制器**：`max_steps` 预算与确定性终止。
6. **检索**：离线语料索引，支撑 RAG demo/test。
7. **记忆**：KV + session store（离线优先）。
8. **可靠性**：重试/降级/熔断。
9. **治理**：Policy/Guardrails/HITL 审批。
10. **可观测与评测**：Tracing + Eval Harness。

## 为什么要“最小运行时”

- 让模式 **可组合**、可比较（同一套输入输出约束）
- 让测试 **离线确定性**（MockLLM）
- 保持 **无框架依赖**（不靠 LangChain/LangGraph）

## 本仓库对应代码

- Types/messages：`src/agent_patterns_lab/runtime/types.py`
- Model + MockLLM：`src/agent_patterns_lab/runtime/model.py`、`src/agent_patterns_lab/runtime/mock_model.py`
- Structured：`src/agent_patterns_lab/runtime/structured.py`
- Tools：`src/agent_patterns_lab/runtime/tools.py`
- Runner：`src/agent_patterns_lab/runtime/runner.py`
- Tracing：`src/agent_patterns_lab/runtime/tracing.py`
- Reliability：`src/agent_patterns_lab/runtime/reliability.py`
- Cache：`src/agent_patterns_lab/runtime/cache.py`
- Memory：`src/agent_patterns_lab/runtime/memory/`
- Governance：`src/agent_patterns_lab/runtime/policy.py`、`src/agent_patterns_lab/runtime/guardrails.py`、`src/agent_patterns_lab/runtime/hitl.py`
- Eval：`src/agent_patterns_lab/runtime/evals/`

