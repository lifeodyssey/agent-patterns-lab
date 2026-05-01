import unittest

from agent_patterns_lab.runtime import Message, MockLLM, Tracer
from agent_patterns_lab.runtime.types import ScriptedResponsesExhausted


class TestMockLLM(unittest.TestCase):
    def test_scripted_responses_are_consumed_in_order(self) -> None:
        model = MockLLM(["a", "b"])
        self.assertEqual(model.complete([Message(role="user", content="x")]), "a")
        self.assertEqual(model.complete([Message(role="user", content="y")]), "b")
        self.assertEqual(model.remaining(), 0)

    def test_exhaustion_raises(self) -> None:
        model = MockLLM([])
        with self.assertRaises(ScriptedResponsesExhausted):
            model.complete([Message(role="user", content="x")])

    def test_tracer_records_events(self) -> None:
        tracer = Tracer()
        model = MockLLM(["ok"])
        out = model.complete([Message(role="user", content="x")], tracer=tracer)
        self.assertEqual(out, "ok")
        self.assertEqual(len(tracer.events), 1)
        self.assertEqual(tracer.events[0].name, "llm.complete")


if __name__ == "__main__":
    unittest.main()

