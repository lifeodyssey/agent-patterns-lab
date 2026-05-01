import unittest

from agent_patterns_lab.patterns.rewoo import rewoo
from agent_patterns_lab.runtime import MockLLM, Tool, ToolRegistry


class TestRewoo(unittest.TestCase):
    def test_rewoo(self) -> None:
        tools = ToolRegistry([Tool(name="echo", description="echo", handler=lambda a: a["x"])])
        model = MockLLM(
            [
                '{"tool_calls":[{"tool":"echo","args":{"x":"ok"},"purpose":""}]}',
                "final",
            ]
        )
        result = rewoo(model, task="x", tools=tools)
        self.assertEqual(result.tool_results, ["ok"])
        self.assertEqual(result.answer, "final")


if __name__ == "__main__":
    unittest.main()

