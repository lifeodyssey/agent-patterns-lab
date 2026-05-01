import unittest

from agent_patterns_lab.patterns.retrieval_loop import retrieval_loop
from agent_patterns_lab.runtime import Document, MockLLM, SimpleSearchIndex


class TestRetrievalLoop(unittest.TestCase):
    def test_retrieval_loop_done(self) -> None:
        index = SimpleSearchIndex([Document(doc_id="paris", text="Paris is the capital of France.")])
        model = MockLLM(['{"query":"paris"}', '{"done": true, "answer": "Paris. [paris]"}'])
        out = retrieval_loop(model, question="capital?", index=index, rounds=1)
        self.assertEqual(out.answer, "Paris. [paris]")
        self.assertEqual(len(out.evidence), 1)


if __name__ == "__main__":
    unittest.main()

