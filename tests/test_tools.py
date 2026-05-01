import unittest

from agent_patterns_lab.runtime import Tool, ToolExecutionError, ToolNotFoundError, ToolRegistry, Tracer


class TestTools(unittest.TestCase):
    def test_call_success(self) -> None:
        tools = ToolRegistry([Tool(name="echo", description="echo", handler=lambda a: str(a["x"]))])
        out = tools.call("echo", {"x": 1})
        self.assertEqual(out, "1")

    def test_call_missing_tool_raises(self) -> None:
        tools = ToolRegistry([])
        with self.assertRaises(ToolNotFoundError):
            tools.call("missing", {})

    def test_call_error_returns_error_string_by_default(self) -> None:
        tracer = Tracer()

        def boom(_args: dict) -> str:
            raise ValueError("nope")

        tools = ToolRegistry([Tool(name="boom", description="boom", handler=boom)])
        out = tools.call("boom", {}, tracer=tracer)
        self.assertIn("TOOL_ERROR[boom]", out)
        self.assertTrue(any(e.name == "tool.error" for e in tracer.events))

    def test_call_error_can_raise(self) -> None:
        def boom(_args: dict) -> str:
            raise ValueError("nope")

        tools = ToolRegistry([Tool(name="boom", description="boom", handler=boom)])
        with self.assertRaises(ToolExecutionError):
            tools.call("boom", {}, raise_on_error=True)


if __name__ == "__main__":
    unittest.main()

