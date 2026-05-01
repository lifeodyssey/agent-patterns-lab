import unittest

from agent_patterns_lab.patterns.plan_and_solve import plan_and_solve
from agent_patterns_lab.runtime import MockLLM


class TestPlanAndSolve(unittest.TestCase):
    def test_plan_and_solve(self) -> None:
        model = MockLLM(
            [
                '{"plan":["s1","s2"]}',
                "o1",
                "o2",
                "final",
            ]
        )
        result = plan_and_solve(model, task="x")
        self.assertEqual(result.plan, ["s1", "s2"])
        self.assertEqual(result.step_outputs, ["o1", "o2"])
        self.assertEqual(result.answer, "final")


if __name__ == "__main__":
    unittest.main()

