# Memory (KV / Session)

## The Problem It Solves

Long-running agents need **state**:

- lessons learned (Reflexion)
- user preferences
- partial work products
- recovery after interruption

This repo starts with small, explicit memory stores (KV + session JSON files).

## Repo Reference

- KV store: [`src/agent_patterns_lab/runtime/memory/kv.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/memory/kv.py)
- Session store: [`src/agent_patterns_lab/runtime/memory/session.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/memory/session.py)
- Tests: [`tests/test_memory.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_memory.py)

