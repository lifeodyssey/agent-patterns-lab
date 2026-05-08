# Reflexion (Learn From Failures via Memory)

## What Problem It Solves

When a system fails repeatedly in similar ways, you want it to **write lessons** and reuse them on retry.

## When to Use

- You see repeat failures with similar root causes.
- You can verify success/failure (tests, checkers, constraints).
- You want improvements to persist across attempts (not just one run).

## When NOT to Use

- You can’t tell success from failure (no checker, no tests, no rubric) → lessons will be made up.
- The task is one-off (no repeated attempts) → a single maker-checker loop is cheaper.
- Failures are mostly due to missing knowledge → add retrieval first; don’t “reflect” on ignorance.

## Core Flow

```mermaid
flowchart TD
  A["Attempt"] --> V{"Verify OK?"}
  V -->|yes| O["Return"]
  V -->|no| L["Write lesson"]
  L --> M["Store in memory"]
  M --> A
```

## How It Works

Reflexion turns “a failed run” into a reusable artifact:

1. Run the agent/pipeline for an attempt.
2. Verify the outcome (checker, tests, constraints, retrieval evidence).
3. If it fails, ask the model to write a **lesson**:
   - what went wrong
   - what to do differently next time
   - a concrete checklist / rule of thumb
4. Store lessons in memory and retrieve them at the start of the next attempt.

The “lesson” is often more valuable than the raw conversation because it is compact and portable.

### Mechanics (what makes lessons usable)

- **Lesson schema**: store `{symptom, root_cause, fix, checklist, scope}`; avoid vague “be careful”.
- **Apply-at-start**: retrieve top-K relevant lessons before attempt #2 (don’t wait until the end).
- **Guard against rationalization**: require linking the lesson to observed evidence (tool logs, failed checks).
- **Decay**: keep memory small (TTL / top-K) so old lessons don’t dominate.

## Worked Example

```bash
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python examples/42_reflexion.py
```

## Failure Modes & Mitigations

- **Wrong lessons** (the model rationalizes): require evidence for the diagnosis; keep lessons short and testable.
- **Over-general lessons** (“be careful”): enforce a template (symptom → cause → fix).
- **Memory bloat**: deduplicate lessons; keep top-K relevant; add TTL.
- **Applying irrelevant lessons**: retrieve by similarity + add a relevance score; allow the agent to ignore low-confidence lessons.

## Evolution Path

- Extends: Maker-Checker/CoVe by persisting lessons across runs
- In production: pair with **session memory** + **evals** to prevent regressions

## Repo Reference

- Code: [`src/agent_patterns_lab/patterns/reflexion.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/reflexion.py)
- Example: [`examples/42_reflexion.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/42_reflexion.py)
- Tests: [`tests/test_reflexion.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_reflexion.py)

## References

- Shinn et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning*. https://arxiv.org/abs/2303.11366
