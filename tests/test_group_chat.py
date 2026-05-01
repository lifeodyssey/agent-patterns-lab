import unittest

from agent_patterns_lab.patterns.group_chat import ChatAgent, run_group_chat_round_robin, run_group_chat_selector
from agent_patterns_lab.runtime import MockLLM


class TestGroupChat(unittest.TestCase):
    def test_round_robin_stops_on_final(self) -> None:
        a1 = ChatAgent(name="a1", description="d1", model=MockLLM(['{"type":"speak","content":"hi"}']))
        a2 = ChatAgent(name="a2", description="d2", model=MockLLM(['{"type":"final","answer":"done"}']))
        out = run_group_chat_round_robin([a1, a2], task="t", max_rounds=2)
        self.assertEqual(out, "done")

    def test_selector_stops_on_final(self) -> None:
        selector = MockLLM(['{"speaker":"a1"}', '{"speaker":"a2"}'])
        a1 = ChatAgent(name="a1", description="d1", model=MockLLM(['{"type":"speak","content":"step"}']))
        a2 = ChatAgent(name="a2", description="d2", model=MockLLM(['{"type":"final","answer":"final"}']))
        out = run_group_chat_selector(selector, [a1, a2], task="t", max_turns=4)
        self.assertEqual(out, "final")


if __name__ == "__main__":
    unittest.main()

