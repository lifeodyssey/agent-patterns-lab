# Plan & Solve

## What Problem It Solves

For long-horizon tasks, directly “answer now” often fails. Plan & Solve splits:

1. generate a plan (structured)
2. execute steps
3. synthesize final answer

## Core Flow

```mermaid
flowchart TD
  U["Task"] --> P["Plan (JSON steps)"]
  P --> E["Execute steps"]
  E --> S["Synthesize"]
  S --> O["Final"]
```

## How It Works

Plan & Solve introduces an explicit “planning artifact”:

1. **Plan**: the model outputs a step list (ideally structured) with clear success criteria.
2. **Execute**: run steps in order, collecting intermediate results.
3. **Synthesize**: compose the final answer from verified step outputs.

This helps because planning forces the model to externalize structure and reduces “lost in the middle” reasoning.

## Failure Modes & Mitigations

- **Bad plan** (missing steps, wrong order): add a plan review step; enforce a plan template.
- **Plan not followed**: make execution read the plan step-by-step; log deviations.
- **Reality mismatch** (tool outputs change assumptions): add replanning (PER) or a replanner role.
- **Over-planning**: cap plan length; merge trivial steps.

## Evolution Path

- Comes from: workflow chaining (but steps are model-chosen)
- Leads to: **PER** (replanning when needed), **LLM Compiler** (DAG execution)

## Repo Reference

- Code: [`src/agent_patterns_lab/patterns/plan_and_solve.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/plan_and_solve.py)
- Example: [`examples/50_plan_and_solve.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/50_plan_and_solve.py)
- Tests: [`tests/test_plan_and_solve.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_plan_and_solve.py)
