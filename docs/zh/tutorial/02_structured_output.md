# 02：结构化输出

Chatbot 的自然语言回答很好读，但不好接代码。旅游计划如果要给前端渲染，最好是稳定的结构。

```python
--8<-- "examples/10_structured_output.py"
```

运行：

```bash
uv run python examples/10_structured_output.py
```

## 新问题

我们希望模型输出：

```json
{
  "city": "Hangzhou",
  "morning": "...",
  "afternoon": "...",
  "evening": "...",
  "packing": ["..."]
}
```

但模型可能少字段、字段类型不对，或者在 JSON 外面多说几句。

## 新模式：Structured Output

`structured_complete(...)` 做三件事：

1. 从模型输出里提取 JSON。
2. 用 `parse_itinerary(...)` 校验字段。
3. 如果失败，把错误反馈给模型，让它重试修复。

这一步之后，旅游助手不只是“会说”，而是能给代码一个稳定对象。

## 它还是不够

结构化输出只能保证格式，不保证事实。

如果模型说“明天晴天”，它可能只是猜的。旅游规划需要天气、路线、开放时间这些外部信息。

下一步：让代码提供工具。看 [03：工具调用](03_tool_calling.md)。
