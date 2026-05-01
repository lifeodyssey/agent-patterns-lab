import unittest

from agent_patterns_lab.patterns.self_discovery import self_discovery
from agent_patterns_lab.runtime import MockLLM


class TestSelfDiscovery(unittest.TestCase):
    def test_selects_modules_and_answers(self) -> None:
        model = MockLLM(['{"modules":["a"]}', "ok"])
        res = self_discovery(model, task="x", available_modules=["a", "b"])
        self.assertEqual(res.modules, ["a"])
        self.assertEqual(res.answer, "ok")


if __name__ == "__main__":
    unittest.main()

