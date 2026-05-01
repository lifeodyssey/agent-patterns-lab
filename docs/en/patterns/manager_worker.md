# Manager-Worker (Orchestrator-Workers)

## What Problem It Solves

When tasks require multiple specialties, a single agent struggles.  
Manager-Worker introduces:

- a manager to decompose/assign
- workers to execute subtasks
- a manager synthesis step

## Core Flow

```mermaid
flowchart TD
  U["Task"] --> M["Manager: assign subtasks"]
  M --> W1["Worker A"]
  M --> W2["Worker B"]
  W1 --> M
  W2 --> M
  M --> O["Final"]
```

## Evolution Path

- Comes from: routing + specialization
- Often combined with: **agents-as-tools**, **group chat**, **handoff**

## Repo Reference

- Code: `src/agent_patterns_lab/patterns/manager_worker.py`
- Example: `examples/60_manager_worker.py`
- Tests: `tests/test_manager_worker.py`

