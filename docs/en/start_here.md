# Start Here: From Chatbot to Agent

This is not mainly a repo manual. It is a learning path: **start with the smallest chatbot, discover what breaks, and grow agent patterns only when needed.**

The recurring example is still a travel planning assistant, but the first version is not an agent. It is just:

```python
answer = model.complete(messages)
```

## First Code

```python
--8<-- "examples/00_single_shot.py"
```

Run:

```bash
uv run python examples/00_single_shot.py
```

If the command is confusing, read [Command Notes](run_commands.md).

## Reading Order

1. [00: Minimal Chatbot](tutorial/00_chatbot.md)
2. [01: Conversation History](tutorial/01_conversation.md)
3. [02: Structured Output](tutorial/02_structured_output.md)
4. [03: Tool Calling](tutorial/03_tool_calling.md)
5. [04: Workflow](tutorial/04_workflow.md)
6. [05: Agent Loop](tutorial/05_agent_loop.md)

After that, read [Choose a Pattern](choose_pattern.md).
