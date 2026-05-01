# Runtime Overview (The “Lego Bricks”)

Most patterns are **compositions** of a few reusable runtime capabilities:

1. **Messages**: a minimal chat format (`system/user/assistant/tool`).
2. **Model interface**: a single `complete(messages) -> str`.
3. **Structured output**: parse + validate JSON with repair retries.
4. **Tool calling**: register tools and call them with tracing.
5. **Loop controller**: `max_steps` budget and deterministic termination.
6. **Retrieval**: a local index for offline RAG demos/tests.
7. **Memory**: KV + session stores (offline-first).
8. **Reliability wrappers**: retry/backoff, fallback, circuit breaker.
9. **Governance**: tool policy, guardrails, HITL approval.
10. **Observability**: tracing + eval harness.

## Why a Minimal Runtime Matters

- Makes patterns **comparable** (same input/output discipline).
- Makes testing **offline and deterministic** (via `MockLLM`).
- Keeps the repo **framework-free** (no LangChain/LangGraph).

## Where It Lives in This Repo

- Types + messages: `src/agent_patterns_lab/runtime/types.py`
- Model protocol + MockLLM: `src/agent_patterns_lab/runtime/model.py`, `src/agent_patterns_lab/runtime/mock_model.py`
- Structured output: `src/agent_patterns_lab/runtime/structured.py`
- Tools: `src/agent_patterns_lab/runtime/tools.py`
- Loop controller: `src/agent_patterns_lab/runtime/runner.py`
- Tracing: `src/agent_patterns_lab/runtime/tracing.py`
- Reliability: `src/agent_patterns_lab/runtime/reliability.py`
- Cache: `src/agent_patterns_lab/runtime/cache.py`
- Memory: `src/agent_patterns_lab/runtime/memory/`
- Governance: `src/agent_patterns_lab/runtime/policy.py`, `src/agent_patterns_lab/runtime/guardrails.py`, `src/agent_patterns_lab/runtime/hitl.py`
- Eval harness: `src/agent_patterns_lab/runtime/evals/`

