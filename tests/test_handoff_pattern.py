import unittest

from agent_patterns_lab.patterns.handoff import HandoffAgent, run_handoff
from agent_patterns_lab.runtime import MockLLM


class TestHandoff(unittest.TestCase):
    def test_router_handles(self) -> None:
        router = MockLLM(['{"type":"handle","answer":"ok"}'])
        agents = [HandoffAgent(name="a", description="d", model=MockLLM(["x"]))]
        out = run_handoff(router, agents, task="t")
        self.assertEqual(out, "ok")

    def test_router_handoffs(self) -> None:
        router = MockLLM(['{"type":"handoff","to":"a","summary":"do it"}'])
        agents = [HandoffAgent(name="a", description="d", model=MockLLM(["agent_answer"]))]
        out = run_handoff(router, agents, task="t")
        self.assertEqual(out, "agent_answer")


if __name__ == "__main__":
    unittest.main()

