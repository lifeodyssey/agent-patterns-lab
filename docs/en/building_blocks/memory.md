# Memory (KV / Session)

## What Problem It Solves

Long-running agents need **state**. Otherwise every run is amnesia:

- lessons learned (Reflexion)
- user preferences
- partial work products
- recovery after interruption

This repo starts with small, explicit memory stores (KV + session JSON files).
No magic “agent memory”. Just data structures you can reason about.

## How It Works (in This Repo)

Two building blocks:

- **KV store**: “give me a value by key”
  - `InMemoryKV`: process-local, easy for tests/examples
  - `JsonFileKV`: persistent KV backed by a single JSON file
- **Session store**: “save/restore a run snapshot”
  - `JsonFileSessionStore`: `save(session_id, state)` and `load(session_id)`

## When to Use / When NOT to Use

Use KV when you want:

- stable user preferences (`timezone`, `tone`, `tool_allowlist`)
- learned lessons you want to retrieve later (Reflexion “do / don’t”)

Use session storage when you need:

- resume after interruption (HITL approval, crashes, timeouts)
- reproduce/debug a run (“what was the state at step 7?”)

Avoid storing:

- secrets/PII without a clear policy (and encryption if persisted)
- huge blobs in a JSON file KV (you’ll regret it)
- unvalidated “model thoughts” as truth (store facts/evidence, not vibes)

## Worked Example

```python
from pathlib import Path

from agent_patterns_lab.runtime.memory import InMemoryKV, JsonFileSessionStore

kv = InMemoryKV()
kv.set("user.tone", "direct")
kv.set("user.timezone", "Asia/Shanghai")

sessions = JsonFileSessionStore(root=Path(".sessions"))
sessions.save(
    "run-001",
    {
        "step": 7,
        "ledger": [{"id": "t1", "status": "done"}],
        "notes": "waiting for approval",
    },
)

state = sessions.load("run-001")
assert state["step"] == 7
```

## Failure Modes & Mitigations

- **Stale memory**: version your keys (`v1/user.tone`), or store timestamps and expire.
- **Schema drift**: treat persisted JSON like an API; migrate intentionally.
- **Prompt injection via memory**: store “facts” separate from “instructions” (same idea as evidence ledgers).

## Repo Reference

- KV store: [`src/agent_patterns_lab/runtime/memory/kv.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/memory/kv.py)
- Session store: [`src/agent_patterns_lab/runtime/memory/session.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/memory/session.py)
- Tests: [`tests/test_memory.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_memory.py)
