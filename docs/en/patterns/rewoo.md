# REWOO (Reasoning Without Observation)

## What Problem It Solves

Tool loops can be slow/expensive due to multiple round-trips. REWOO reduces this by:

- planning tool calls up front
- executing tools in batch
- synthesizing once

## Core Flow

```mermaid
flowchart TD
  U["Task"] --> P["Plan tool_calls (JSON)"]
  P --> T["Run tools (batch)"]
  T --> S["Synthesize"]
  S --> O["Final"]
```

## How It Works

REWOO trades adaptivity for fewer LLM round-trips:

1. The model plans all (or most) tool calls up front as a structured list.
2. The system executes tool calls in batch (possibly in parallel).
3. The model synthesizes a final answer using all observations at once.

This is useful when tool calling latency dominates and the task can be decomposed reliably.

## Failure Modes & Mitigations

- **Plan is wrong without observations**: keep plans short; allow a second planning round; fall back to ReAct when needed.
- **Missing intermediate decisions**: restrict REWOO to tasks where tool calls are independent.
- **Tool errors break the batch**: add per-tool retries and partial results handling.
- **Over-fetching**: add budgets and pruning for redundant tool calls.

## Evolution Path

- A “workflow” alternative to ReAct when tool costs dominate
- Often combined with: **verification** after synthesis

## References

- REWOO (Reasoning Without Observation): Xu et al., 2023. citeturn3search3

## Repo Reference

- Code: [`src/agent_patterns_lab/patterns/rewoo.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/rewoo.py)
- Example: [`examples/52_rewoo.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/52_rewoo.py)
- Tests: [`tests/test_rewoo.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_rewoo.py)
