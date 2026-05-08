# 从这里开始：从 Chatbot 到 Agent

这不是一份“repo 使用说明”。更准确地说，它是一条学习路线：**先写最小 Chatbot，然后看它在哪里不够，再一步步长出 Agent 设计模式。**

贯穿案例仍然是旅游规划助手，但第一步不要叫它 Agent。第一步只是：

```python
answer = model.complete(messages)
```

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

## 建议阅读顺序

1. [00：最小 Chatbot](tutorial/00_chatbot.md)
2. [01：对话历史](tutorial/01_conversation.md)
3. [02：结构化输出](tutorial/02_structured_output.md)
4. [03：工具调用](tutorial/03_tool_calling.md)
5. [04：Workflow](tutorial/04_workflow.md)
6. [05：Agent Loop](tutorial/05_agent_loop.md)

读完这六页，再去看 [选择模式](choose_pattern.md)。那时模式名就不是术语表了，而是你已经亲眼看到的问题。
