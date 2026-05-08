# Voting / Self-Consistency

## What Problem It Solves

For many prompts, the model is stochastic. Voting reduces variance by sampling multiple answers and selecting a winner.

## When to Use

- Answers are short and easy to normalize.
- The task is cheap enough to sample N times.
- You want robustness more than latency.

## When NOT to Use

- The task needs **external truth** (fresh facts, tool outputs) → add retrieval/verification, not more samples.
- Normalization is impossible (long essays with no clear “answer key”) → consider **maker-checker** instead of voting.
- You’re already budget-limited → voting is a cost multiplier by design.

## Core Flow

```mermaid
flowchart TD
  P["Same prompt"] --> S1["Sample 1"]
  P --> S2["Sample 2"]
  P --> S3["Sample 3"]
  S1 --> V["Vote/majority"]
  S2 --> V
  S3 --> V
  V --> O["Winner"]
```

## How It Works

Voting exploits diversity across samples:

1. Generate `N` candidates from the same input (often with higher temperature).
2. **Normalize** outputs if possible (e.g., extract final answer, parse JSON).
3. Select the best candidate via:
   - majority vote on identical normalized answers, or
   - a separate “judge” model / rubric, or
   - pairwise tournament (A vs B vs C…)

### Mechanics (what to decide up front)

- **What you vote on**: final answer string, parsed JSON, or a derived key (e.g., “route id”).
- **How you normalize**: strict parsing beats regex; avoid voting on raw prose if you can.
- **How you break ties**: judge rubric, prefer cheaper-to-verify candidates, or fall back to a checker.
- **When to spend the votes**: route only hard/ambiguous cases to voting; keep easy cases single-shot.

## Worked Example

```bash
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python examples/31_voting.py
```

## Failure Modes & Mitigations

- **No clear majority**: use a judge rubric; increase N; fall back to maker-checker.
- **Systematic bias** (all samples wrong): add retrieval / verification, not more voting.
- **Hard to normalize**: enforce structured outputs; vote on derived metrics.
- **Cost**: vote only on hard inputs (route easy ones to single-shot).

## Evolution Path

- Often paired with: **Maker-Checker**, **CoVe** (verify claims after voting)
- In production: add **evals** to detect regressions

## Repo Reference

- Code: [`src/agent_patterns_lab/patterns/voting.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/voting.py)
- Example: [`examples/31_voting.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/31_voting.py)
- Tests: [`tests/test_voting.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_voting.py)

## References

- Self-Consistency (sampling multiple reasoning paths → choose the most consistent): https://arxiv.org/abs/2203.11171
