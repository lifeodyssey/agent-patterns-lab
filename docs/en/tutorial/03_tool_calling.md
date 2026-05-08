# 03: Tool Calling

The model does not know the live world. If the travel assistant needs weather, Python should provide a weather tool.

```python
--8<-- "examples/20_tool_calling.py"
```

Run:

```bash
uv run python examples/20_tool_calling.py
```

Tool calling is just:

```text
tool name + args -> Python function -> tool result
```

`ToolRegistry` is the tool allowlist. The model may request a tool later, but Python decides what can actually run.

Next: [04: Workflow](04_workflow.md).
