import unittest

from agent_patterns_lab.patterns.react import NeedUserInput, run_react
from agent_patterns_lab.runtime import MaxStepsExceeded, MockLLM, RunLimits, Tool, ToolRegistry


class TestReAct(unittest.TestCase):
    def test_react_calls_tool_then_finishes(self) -> None:
        calls = {"n": 0}

        def add(args: dict) -> str:
            calls["n"] += 1
            return str(int(args["a"]) + int(args["b"]))

        tools = ToolRegistry([Tool(name="add", description="add", handler=add)])
        model = MockLLM(
            [
                '{"type":"tool","tool":"add","args":{"a":2,"b":2}}',
                '{"type":"final","answer":"4"}',
            ]
        )

        out = run_react(model, task="Compute 2+2", tools=tools, limits=RunLimits(max_steps=5))
        self.assertEqual(out, "4")
        self.assertEqual(calls["n"], 1)

    def test_react_ask_raises_need_user_input(self) -> None:
        tools = ToolRegistry([])
        model = MockLLM(['{"type":"ask","question":"Which format?"}'])
        with self.assertRaises(NeedUserInput):
            run_react(model, task="x", tools=tools, limits=RunLimits(max_steps=1))

    def test_react_respects_max_steps(self) -> None:
        def noop(_args: dict) -> str:
            return "ok"

        tools = ToolRegistry([Tool(name="noop", description="noop", handler=noop)])
        model = MockLLM(
            [
                '{"type":"tool","tool":"noop","args":{}}',
                '{"type":"tool","tool":"noop","args":{}}',
            ]
        )
        with self.assertRaises(MaxStepsExceeded):
            run_react(model, task="x", tools=tools, limits=RunLimits(max_steps=2))


if __name__ == "__main__":
    unittest.main()

