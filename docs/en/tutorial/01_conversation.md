# 01: Conversation History

A one-shot chatbot forgets unless we pass history back in.

```python
--8<-- "examples/01_conversation_history.py"
```

Run:

```bash
uv run python examples/01_conversation_history.py
```

The important change is that each user and assistant message is appended to `messages`. The next call sees the conversation so far.

This helps the travel assistant remember preferences, but it still returns free-form text.

Next: [02: Structured Output](02_structured_output.md).
