import unittest

from agent_patterns_lab.patterns.agentic_rag import agentic_rag
from agent_patterns_lab.runtime import Document, MockLLM, SimpleSearchIndex


class TestAgenticRag(unittest.TestCase):
    def test_agentic_rag_collects_evidence(self) -> None:
        index = SimpleSearchIndex([Document(doc_id="paris", text="Paris is the capital of France.")])
        model = MockLLM(
            [
                '{"type":"tool","tool":"search","args":{"query":"paris","k":1}}',
                '{"type":"final","answer":"Paris. [paris]"}',
            ]
        )
        result = agentic_rag(model, question="capital?", index=index)
        self.assertEqual(result.answer, "Paris. [paris]")
        self.assertEqual(len(result.evidence), 1)
        self.assertEqual(result.evidence[0].doc.doc_id, "paris")


if __name__ == "__main__":
    unittest.main()

