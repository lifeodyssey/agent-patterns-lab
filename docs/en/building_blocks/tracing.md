# Tracing (Replayable Observability)

## The Problem It Solves

Without traces, agent systems are hard to debug:

- what did the model see?
- which tool calls were made?
- where did it get stuck?

Tracing turns a run into a **JSONL event log**.

## What to Trace

- model calls (input + output)
- tool calls and results
- loop steps and termination
- governance blocks (policy/guardrail/HITL)

## Repo Reference

- Implementation: `src/agent_patterns_lab/runtime/tracing.py`
- Traces output: `.traces/*.jsonl`

