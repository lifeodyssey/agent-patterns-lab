# 03：工具调用

模型自己不知道实时世界。要让旅游助手不乱猜天气，就要把“查天气”做成一个 Python 工具。

```python
--8<-- "examples/20_tool_calling.py"
```

运行：

```bash
uv run python examples/20_tool_calling.py
```

## 新模式：Tool Calling

工具调用的本质很简单：

```text
工具名 + 参数 -> Python 函数 -> 工具返回
```

在这个例子里：

- 工具名：`get_weather`
- 参数：`{"city": "Hangzhou", "date": "tomorrow"}`
- 返回：下午 3 点后小雨，18–23°C

`ToolRegistry` 是工具白名单。模型以后可以请求工具，但真正能调用什么，由 Python 这层决定。

## 它还是不够

到这里，我们有了：

- Chatbot
- 对话历史
- 结构化输出
- 工具

但还有一个重要问题：**谁决定下一步？**

如果步骤固定，比如“先提取偏好，再生成行程，再格式化”，那就不要让模型自由发挥。代码控制路径更稳。

下一步：固定流程。看 [04：Workflow](04_workflow.md)。
