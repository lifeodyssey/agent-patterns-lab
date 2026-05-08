# 从这里开始：从 Chatbot 到 Agent

如果你第一次读这份材料，先别从模式名开始。

模式名太容易吓人。ReAct、Agentic RAG、Planner-Executor-Replanner、Magentic Orchestration……听起来像一堆新名词，其实背后都是同一个问题：

> 一个普通 Chatbot 在真实任务里哪里撑不住？

这条路线就是按这个问题排的。
先写最小 Chatbot，然后看它在哪里不够，再一步步长出 Agent 设计模式。

## 解决的问题

这一页解决一个很具体的问题：你应该按什么顺序读。

不是按论文发布时间，也不是按框架菜单，而是按“一个 Chatbot 遇到的问题”往下走。

贯穿案例仍然是旅游规划助手，但第一步不要叫它 Agent。第一步只是：

```python
answer = model.complete(messages)
```

## 它是如何运作的

每一章只加一层能力：

- 先让模型回答。
- 再让它记住当前对话。
- 再让它输出稳定结构。
- 再让它调用工具。
- 再把固定步骤串成 workflow。
- 最后进入 agent loop，让模型根据观察结果决定下一步。

前面每一步都能跑，后面每一步都有来由。

## 第一段代码

```python
--8<-- "examples/00_single_shot.py"
```

运行：

```bash
uv run python examples/00_single_shot.py
```

如果你不理解这条命令，先看 [命令解释](run_commands.md)。

## 你会一路遇到这些问题

| 步骤 | 代码形态 | 遇到的问题 | 长出的模式 |
|---|---|---|---|
| 00 | `model.complete(messages)` | 只会一次性回答 | Chatbot |
| 01 | 追加 `messages` | 当前对话要记住偏好 | Conversation History |
| 02 | JSON + parser | 自然语言不好接代码 | Structured Output |
| 03 | Python 函数当工具 | 模型不知道实时世界 | Tool Calling |
| 04 | 固定步骤串起来 | 步骤已知时不该乱跑 | Workflow |
| 05 | 模型决定下一步 | 工具结果会改变下一步 | Agent Loop / ReAct |

前六章只做一件事：把“Chatbot 变成 Agent”这件事拆开。
不是为了显得高级，而是为了让每一层都有来由。

## 什么时候用这条路线

适合你想从零实现、从代码理解模式的时候。

如果你已经知道自己要查某个模式，可以直接去 [选择模式](choose_pattern.md)。
如果你只是想看真实 SDK 怎么接，可以先看 [00：最小 Chatbot](tutorial/00_chatbot.md) 的附录。

## 常见失败模式

读这类材料最容易遇到两个坑：

- 一上来就背模式名，结果不知道每个模式为什么存在。
- 一上来就用大框架，结果看不到 agent loop、工具调用、状态管理这些边界。

所以这里先慢一点，从最小代码开始。

## 建议阅读顺序

1. [00：最小 Chatbot](tutorial/00_chatbot.md)
2. [01：对话历史](tutorial/01_conversation.md)
3. [02：结构化输出](tutorial/02_structured_output.md)
4. [03：工具调用](tutorial/03_tool_calling.md)
5. [04：Workflow](tutorial/04_workflow.md)
6. [05：Agent Loop](tutorial/05_agent_loop.md)

读完这六页，再去看 [选择模式](choose_pattern.md)。那时模式名就不是术语表了，而是你已经亲眼看到的问题。
