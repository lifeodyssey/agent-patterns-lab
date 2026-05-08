# 04: Workflow

Not everything needs an agent. If the steps are known, use a workflow.

```python
--8<-- "examples/11_prompt_chaining.py"
```

Run:

```bash
uv run python examples/11_prompt_chaining.py
```

This example uses Prompt Chaining:

```text
extract preferences -> draft itinerary -> format final answer
```

Workflows are easier to test and cheaper to control. They break down when the next step depends on a fresh tool result.

Next: [05: Agent Loop](05_agent_loop.md).
