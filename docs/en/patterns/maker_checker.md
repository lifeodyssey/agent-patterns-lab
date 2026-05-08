# Maker-Checker (Evaluator-Optimizer)

## What Problem It Solves

Models produce drafts; you often need a **quality gate**:

- correctness rubric
- safety requirements
- formatting constraints

Maker-Checker adds an explicit verification step and revision loop.

## When to Use

- Errors are costly (financial/legal/security/production incidents).
- You can define a **rubric** (what “good” means).
- You want repeatable quality improvement, not just “try again”.

## When NOT to Use

- You have a **deterministic validator** (unit tests, schema validation, rules) that already catches the problem → use that first.
- The checker can’t actually judge quality (no rubric, no ground truth, no way to verify) → the loop becomes “argue with yourself”.
- The task is low-stakes and latency-sensitive → the extra calls rarely pay back.

## Core Flow

```mermaid
flowchart TD
  M["Maker draft"] --> C["Checker evaluate (passed, feedback)"]
  C -->|passed| O["Return draft"]
  C -->|fail| R["Revise using feedback"] --> M
```

## How It Works

1. **Maker** produces a draft.
2. **Checker** evaluates against a rubric and returns:
   - `passed: true/false`
   - feedback items (what’s wrong, what to fix)
3. If failed, the Maker revises using feedback and repeats.

The key design choice is that the checker output is **structured and actionable**, so the revision step is guided.

### Mechanics (what makes it work)

- **Rubric is a contract**: make “pass/fail” depend on specific criteria, not vibes.
- **Separation**: use different prompts (and sometimes different models) to reduce maker/checker echoing.
- **Budgets**: cap revision rounds; define “good enough” thresholds.
- **External checks**: whenever possible, let tools/rules do the checking (LLM as coordinator, not oracle).

## Worked Example

```bash
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python examples/30_maker_checker.py
```

## Failure Modes & Mitigations

- **Maker/Checker “collusion”**: use different prompts, temperatures, or even different models.
- **Vague feedback**: force the checker to output concrete, testable issues.
- **Infinite revisions**: enforce max rounds and “good enough” thresholds.
- **Cost blow-up**: cache checker results; add early-stop and narrower rubrics.

## Evolution Path

- Comes from: “single draft” generation
- Often combined with: **Voting**, **CoVe**, **Retrieval**

## Repo Reference

- Code: [`src/agent_patterns_lab/patterns/maker_checker.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/maker_checker.py)
- Example: [`examples/30_maker_checker.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/30_maker_checker.py)
- Tests: [`tests/test_maker_checker.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_maker_checker.py)

## References

- Self-Refine (iterative feedback → refine loop): https://arxiv.org/abs/2303.17651
- Evaluator–Optimizer (pattern write-up): https://www.theagenticwiki.com/docs/patterns/evaluator-optimizer/
