# Loop Controller (Budgeted Termination)

## The Problem It Solves

Agent loops can run forever. A loop controller provides:

- `max_steps` budget
- a single “stop when result exists” contract
- consistent trace events

```mermaid
flowchart TD
  S["step(i)"] --> R{"Result?"}
  R -->|yes| DONE["Return result"]
  R -->|no| NEXT["i++ (until max_steps)"] --> S
```

## Repo Reference

- Implementation: `src/agent_patterns_lab/runtime/runner.py`
- Tests: `tests/test_runner.py`

