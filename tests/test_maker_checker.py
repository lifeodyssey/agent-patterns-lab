import unittest

from agent_patterns_lab.patterns.maker_checker import maker_checker
from agent_patterns_lab.runtime import MockLLM


class TestMakerChecker(unittest.TestCase):
    def test_returns_improved_draft(self) -> None:
        maker = MockLLM(["v1", "v2"])
        checker = MockLLM(['{"passed": false, "feedback": "fix"}', '{"passed": true, "feedback": ""}'])
        out = maker_checker(maker, checker, task="x", max_rounds=2)
        self.assertEqual(out, "v2")


if __name__ == "__main__":
    unittest.main()

