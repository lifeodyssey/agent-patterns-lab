# 05: Agent Loop

Now we finally need an agent loop: the model chooses the next action, Python executes it, appends the result, and the model decides again.

```python
--8<-- "examples/21_react_loop.py"
```

Run:

```bash
uv run python examples/21_react_loop.py
```

The travel assistant checks weather, searches places, estimates a route, and only then returns a final plan.

The key difference:

| Shape | Who controls the path |
|---|---|
| Workflow | Python code predefines it |
| Agent Loop | The model decides from current state |

Next: [ReAct](../patterns/react.md) and [Choose a Pattern](../choose_pattern.md).
