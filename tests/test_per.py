import unittest

from agent_patterns_lab.patterns.planner_executor_replanner import planner_executor_replanner
from agent_patterns_lab.runtime import MockLLM, RunLimits


class TestPER(unittest.TestCase):
    def test_continue_then_final(self) -> None:
        planner = MockLLM(['{"plan":["a","b"]}'])
        executor = MockLLM(["A", "B"])
        replanner = MockLLM(
            [
                '{"action":"continue","plan":[],"answer":""}',
                '{"action":"final","plan":[],"answer":"done"}',
            ]
        )
        result = planner_executor_replanner(
            planner,
            executor,
            replanner,
            task="x",
            limits=RunLimits(max_steps=5),
        )
        self.assertEqual(result.answer, "done")
        self.assertEqual(result.replans, 0)

    def test_replan(self) -> None:
        planner = MockLLM(['{"plan":["a"]}'])
        executor = MockLLM(["A", "B"])
        replanner = MockLLM(
            [
                '{"action":"replan","plan":["b"],"answer":""}',
                '{"action":"final","plan":[],"answer":"done"}',
            ]
        )
        result = planner_executor_replanner(
            planner,
            executor,
            replanner,
            task="x",
            limits=RunLimits(max_steps=5),
        )
        self.assertEqual(result.answer, "done")
        self.assertEqual(result.replans, 1)


if __name__ == "__main__":
    unittest.main()

