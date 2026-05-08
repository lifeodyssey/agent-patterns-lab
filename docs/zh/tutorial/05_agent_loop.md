# 05：Agent Loop：当下一步取决于工具返回

现在终于到 Agent 了。

Agent 不是“更长的 Prompt”，而是一种控制流：模型每一轮决定下一步动作，Python 执行动作，把结果写回状态，再让模型继续决定。

```python
--8<-- "examples/21_react_loop.py"
```

运行：

```bash
uv run python examples/21_react_loop.py
```

## 这一次发生了什么

旅游助手不是一次性回答，而是：

1. 调 `get_weather`：发现下午有雨。
2. 调 `search_places`：按兴趣和天气找地点。
3. 调 `estimate_route`：估路线顺序和耗时。
4. 输出 `final`：给出计划和打包建议。

这就是 ReAct 风格的 Agent Loop。

## 为什么这是 Agent

关键不是工具数量，而是谁决定下一步：

| 形态 | 谁决定路径 |
|---|---|
| Workflow | Python 代码提前写死 |
| Agent Loop | 模型根据当前状态动态决定 |

旅游助手看到“下午下雨”后，下一步变成“找室内友好的地点”。这就是 Agent Loop 的价值。

## 但 Agent 不是终点

Agent Loop 会带来新问题：

- 它可能无限循环。
- 它可能选错工具。
- 它可能伪造工具结果。
- 它可能给出看似合理但实际很差的路线。

所以后面的模式才会出现：可靠性验证、检索、规划、多 Agent、权限护栏、评测。

下一步可以读 [ReAct 模式页](../patterns/react.md)，再去 [选择模式](../choose_pattern.md) 看完整地图。
