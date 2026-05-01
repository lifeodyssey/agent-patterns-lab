# LLM Compiler (Compile to DAG)

## What Problem It Solves

Some tasks have **dependencies** and can be parallelized. LLM Compiler:

- compiles a plan into a DAG (tasks + deps)
- executes nodes topologically
- assembles the final result

## Core Flow

```mermaid
flowchart TD
  U["Task"] --> C["Compile to DAG"]
  C --> N1["Node 1"]
  C --> N2["Node 2 (depends)"]
  N1 --> N2
  N1 --> J["Join/Assemble"]
  N2 --> J
  J --> O["Final"]
```

## How It Works

LLM Compiler externalizes execution structure:

1. **Compile**: the model emits a DAG spec:
   - node id / description
   - inputs/outputs
   - dependencies
2. **Execute**: run nodes in topological order (or parallelize independent nodes).
3. **Join**: assemble node outputs into a final artifact (report, code, decision).

The benefit over linear plans is concurrency and explicit dependency tracking.

## Failure Modes & Mitigations

- **Wrong dependencies**: add a “graph review” pass; enforce schemas and invariants.
- **Cycles / invalid graphs**: validate DAG; fall back to linear execution if needed.
- **Join step loses context**: use a stable output schema per node; store summaries.
- **Non-determinism**: cache node outputs; add evals at the DAG level.

## Evolution Path

- Extends: Plan & Solve into an explicit execution graph
- Pairs well with: **caching** and **evals** (graph regressions are subtle)

## Repo Reference

- Code: [`src/agent_patterns_lab/patterns/llm_compiler.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/patterns/llm_compiler.py)
- Example: [`examples/53_llm_compiler.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/examples/53_llm_compiler.py)
- Tests: [`tests/test_llm_compiler.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_llm_compiler.py)
