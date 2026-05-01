import unittest

from agent_patterns_lab.patterns.lats import lats_beam_search
from agent_patterns_lab.runtime import MockLLM


class TestLats(unittest.TestCase):
    def test_selects_best_scored_candidate(self) -> None:
        proposer = MockLLM(['{"candidates":["a","b"]}'])
        evaluator = MockLLM(['{"score": 1}', '{"score": 9}'])
        out = lats_beam_search(proposer, evaluator, task="x", depth=1, branch_factor=2, beam_size=1)
        self.assertEqual(out.best, "b")
        self.assertEqual(out.score, 9.0)


if __name__ == "__main__":
    unittest.main()

