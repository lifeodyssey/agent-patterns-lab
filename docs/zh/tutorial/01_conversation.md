# 01：对话历史

最小 Chatbot 只有一次调用。用户下一句再问时，它不知道前面发生了什么，除非我们把历史消息传回去。

```python
--8<-- "examples/01_conversation_history.py"
```

运行：

```bash
uv run python examples/01_conversation_history.py
```

## 代码怎么变了

关键变化是这几行：

```python
messages.append(Message(role="user", content=user_text))
answer = model.complete(messages, tracer=tracer)
messages.append(Message(role="assistant", content=answer))
```

每轮对话后，我们都把用户消息和助手回答放回 `messages`。下一轮模型看到的就不是孤立问题，而是完整上下文。

## 它解决了什么

旅游助手现在能记住当前会话里的偏好，例如“我喜欢茶、本地小吃、轻松步行”。

## 它还是不够

对话历史只是“把文本带上”。它不能保证输出格式稳定。

如果你要把行程渲染到页面上，或者交给下一段代码处理，纯文本就很麻烦：今天模型写成列表，明天写成段落，后天漏掉打包建议。

下一步要解决：让模型输出可解析的数据。看 [02：结构化输出](02_structured_output.md)。
