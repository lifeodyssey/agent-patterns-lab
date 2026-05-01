import unittest

from agent_patterns_lab.patterns.voting import majority_vote, self_consistency
from agent_patterns_lab.runtime import Message, MockLLM


class TestVoting(unittest.TestCase):
    def test_majority_vote_tie_breaks_by_first(self) -> None:
        self.assertEqual(majority_vote(["a", "b"]), "a")

    def test_self_consistency_votes(self) -> None:
        model = MockLLM(["A", "B", "A"])
        out = self_consistency(model, [Message(role="user", content="x")], n=3)
        self.assertEqual(out, "A")


if __name__ == "__main__":
    unittest.main()

