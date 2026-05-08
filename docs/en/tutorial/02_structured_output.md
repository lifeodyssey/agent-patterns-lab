# 02: Structured Output

Free-form text is pleasant to read, but hard for code to consume. A travel plan often needs a stable shape.

```python
--8<-- "examples/10_structured_output.py"
```

Run:

```bash
uv run python examples/10_structured_output.py
```

`structured_complete(...)` extracts JSON, validates it with a parser, and retries with a repair prompt when validation fails.

This gives code a reliable object. It does not guarantee the facts are true.

Next: [03: Tool Calling](03_tool_calling.md).
