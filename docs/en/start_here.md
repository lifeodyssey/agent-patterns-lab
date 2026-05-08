# Start Here: From Chatbot to Agent

If this is your first pass, do not start with pattern names.

Names are noisy. ReAct, Agentic RAG, Planner-Executor-Replanner, Magentic Orchestration — they sound like a pile of concepts. Underneath, they answer one question:

> Where does a normal chatbot break in a real task?

This learning path is ordered by that question.
Start with the smallest chatbot, discover what breaks, and grow agent patterns only when needed.

## What Problem It Solves

This page answers one practical question: what should you read first?

The order is not based on paper dates or framework menus. It follows the failures a chatbot hits as the task becomes real.

The recurring example is still a travel planning assistant, but the first version is not an agent. It is just:

```python
answer = model.complete(messages)
```

## How It Works

Each chapter adds one layer:

- First the model answers.
- Then it remembers the current conversation.
- Then it returns stable structure.
- Then it calls tools.
- Then fixed steps become a workflow.
- Finally, an agent loop lets the model choose the next step from observations.

Each step runs on its own. Each layer earns its place.

## First Code

```python
--8<-- "examples/00_single_shot.py"
```

Run:

```bash
uv run python examples/00_single_shot.py
```

If the command is confusing, read [Command Notes](run_commands.md).

## What You Will See Break

| Step | Code shape | Failure | Pattern |
|---|---|---|---|
| 00 | `model.complete(messages)` | It only answers once. | Chatbot |
| 01 | append to `messages` | The current conversation has preferences. | Conversation History |
| 02 | JSON + parser | Natural language is hard to wire into code. | Structured Output |
| 03 | Python functions as tools | The model lacks live facts. | Tool Calling |
| 04 | fixed steps | Known steps should not be improvised. | Workflow |
| 05 | model chooses next step | Tool results change what should happen next. | Agent Loop / ReAct |

The first six chapters do one job: make “chatbot to agent” visible in code.
Each layer earns its place.

## When to Use This Path

Use it when you want to understand patterns from code, not just definitions.

If you already know which pattern you need, jump to [Choose a Pattern](choose_pattern.md).
If you mainly want real SDK wiring, read the appendix in [00: Minimal Chatbot](tutorial/00_chatbot.md).

## Common Failure Modes

Two traps are common:

- Memorizing pattern names before knowing why they exist.
- Starting with a large framework and losing sight of the agent loop, tools, and state boundaries.

So this path starts small.

## Reading Order

1. [00: Minimal Chatbot](tutorial/00_chatbot.md)
2. [01: Conversation History](tutorial/01_conversation.md)
3. [02: Structured Output](tutorial/02_structured_output.md)
4. [03: Tool Calling](tutorial/03_tool_calling.md)
5. [04: Workflow](tutorial/04_workflow.md)
6. [05: Agent Loop](tutorial/05_agent_loop.md)

After that, read [Choose a Pattern](choose_pattern.md).
