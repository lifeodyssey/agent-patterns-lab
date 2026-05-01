import unittest

from agent_patterns_lab.patterns.cove import ClaimVerification, chain_of_verification
from agent_patterns_lab.runtime import MockLLM


class TestCoVe(unittest.TestCase):
    def test_revises_using_verification(self) -> None:
        model = MockLLM(
            [
                "A. B is true.",
                '{"claims":["B is true"]}',
                "A.",
            ]
        )

        def verify(claim: str) -> ClaimVerification:
            return ClaimVerification(claim=claim, ok=False, evidence="no")

        out = chain_of_verification(model, question="x", verify_claim=verify)
        self.assertEqual(out, "A.")


if __name__ == "__main__":
    unittest.main()

