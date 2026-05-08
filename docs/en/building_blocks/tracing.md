# Tracing (Replayable Observability)

## What Problem It Solves

Without traces, agent systems are hard to debug:

- what did the model see?
- which tool calls were made?
- where did it get stuck?

Tracing turns a run into a **JSONL event log**.

## How It Works (in This Repo)

`Tracer` is intentionally boring:

- `tracer.emit(name, **data)` appends an event with a timestamp
- `tracer.export_jsonl(path)` writes JSONL so you can diff runs and replay them

No spans, no exporters, no OpenTelemetry. Start with a log you can read.

## What to Trace

- model calls (input + output)
- tool calls and results
- loop steps and termination
- governance blocks (policy/guardrail/HITL)

## When to Use / When NOT to Use

Use tracing when:

- you have any loop (ReAct, retrieval loop, PER, multi-agent)
- you want debuggable failures (what happened at step 7?)
- you want regression diffs (did a refactor change tool usage?)

Be careful when:

- you might log secrets/PII (redact or don't record raw content)
- traces are large (log metadata, not full payloads)

## Worked Example

```python
from agent_patterns_lab.runtime import Tracer

tracer = Tracer()
tracer.emit("run.start", run_id="demo-001")
tracer.emit("tool.call", tool="search", args={"q": "react agent loop"})
tracer.emit("tool.result", tool="search", chars=1234)
tracer.emit("run.done", status="ok")

tracer.export_jsonl(".traces/demo.jsonl")
```

If you pass `tracer=...` into patterns (ReAct / RAG / etc.), you’ll get events for model calls, tool calls, and loop steps.

## Failure Modes & Mitigations

- **Too verbose**: in live adapters, set `trace_content=False` (only record sizes/metadata).
- **PII/secrets in logs**: treat traces as sensitive; redact or avoid logging raw content.
- **Hard to compare**: keep event names stable and structured (avoid free-form strings).

## Repo Reference

- Implementation: [`src/agent_patterns_lab/runtime/tracing.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/tracing.py)
- Traces output: `.traces/*.jsonl`
