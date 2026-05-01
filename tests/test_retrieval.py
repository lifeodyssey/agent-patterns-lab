import unittest

from agent_patterns_lab.runtime import Document, SimpleSearchIndex


class TestRetrieval(unittest.TestCase):
    def test_search_scores_and_sorts(self) -> None:
        index = SimpleSearchIndex(
            [
                Document(doc_id="a", text="Paris is the capital of France."),
                Document(doc_id="b", text="France has many cities."),
            ]
        )
        results = index.search("Paris France", k=10)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].doc.doc_id, "a")


if __name__ == "__main__":
    unittest.main()

