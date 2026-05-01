import unittest

from agent_patterns_lab.patterns.reflexion import VerificationResult, reflexion
from agent_patterns_lab.runtime import InMemoryKV, MockLLM


class TestReflexion(unittest.TestCase):
    def test_writes_lesson_and_succeeds(self) -> None:
        kv = InMemoryKV()
        model = MockLLM(["bad", '{"lesson":"be correct"}', "good"])

        def verify(answer: str) -> VerificationResult:
            return VerificationResult(ok=answer == "good", feedback="wrong")

        out = reflexion(
            model,
            task="x",
            verify=verify,
            memory_get=kv.get,
            memory_set=kv.set,
            rounds=2,
        )
        self.assertEqual(out, "good")
        self.assertIsInstance(kv.get("reflexion.lessons"), list)


if __name__ == "__main__":
    unittest.main()

