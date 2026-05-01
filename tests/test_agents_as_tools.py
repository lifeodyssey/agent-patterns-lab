import unittest

from agent_patterns_lab.patterns.agents_as_tools import AgentToolSpec, agent_as_tool
from agent_patterns_lab.patterns.react import run_react
from agent_patterns_lab.runtime import MockLLM, RunLimits, ToolRegistry


class TestAgentsAsTools(unittest.TestCase):
    def test_agent_as_tool_in_react_loop(self) -> None:
        subagent = MockLLM(["42"])
        tool = agent_as_tool(
            AgentToolSpec(
                name="math_agent",
                description="math",
                model=subagent,
                system_prompt="You are math.",
            )
        )
        tools = ToolRegistry([tool])

        controller = MockLLM(
            [
                '{"type":"tool","tool":"math_agent","args":{"task":"Compute 7*6"}}',
                '{"type":"final","answer":"42"}',
            ]
        )
        out = run_react(controller, task="x", tools=tools, limits=RunLimits(max_steps=3))
        self.assertEqual(out, "42")


if __name__ == "__main__":
    unittest.main()

