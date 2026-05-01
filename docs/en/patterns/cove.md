# Chain-of-Verification (CoVe)

## What Problem It Solves

Even if a draft “sounds right”, factual claims may be wrong. CoVe turns verification into a first-class step:

1. draft
2. extract checkable claims
3. verify each claim (tool/rules/human)
4. revise the draft

## Core Flow

```mermaid
flowchart TD
  D["Draft answer"] --> X["Extract claims"]
  X --> V["Verify claims"]
  V --> R["Revise answer"]
  R --> O["Final"]
```

## How It Works

The key move is to treat “verification” as its own workflow:

- **Claim extraction**: convert a free-form draft into a list of checkable items.
  - good claim = specific, testable, and has a clear success/failure condition
- **Verification**: for each claim, gather evidence via:
  - retrieval/search
  - deterministic checks (math, unit conversions, constraints)
  - human approval (HITL) for high stakes
- **Revision**: update the draft so every claim is either supported or removed.

## Failure Modes & Mitigations

- **Missed claims**: force structured claim lists; add second-pass extraction.
- **Weak verification** (“sounds plausible”): require evidence artifacts (doc IDs, quotes, calculations).
- **Over-verification cost**: only verify high-risk claims; route simple queries to cheaper flows.
- **Stale evidence**: timestamp sources; re-check when freshness matters.

## Evolution Path

- Extends: **Maker-Checker** by focusing on factual claims
- Often combined with: **Retrieval / Agentic RAG** for evidence gathering

## Repo Reference

- Code: [`src/agent_patterns_lab/patterns/cove.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/cove.py)
- Example: [`examples/32_cove.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/32_cove.py)
- Tests: [`tests/test_cove.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_cove.py)
