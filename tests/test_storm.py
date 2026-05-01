import unittest

from agent_patterns_lab.patterns.storm import storm_write_article
from agent_patterns_lab.runtime import Document, MockLLM, SimpleSearchIndex


class TestStorm(unittest.TestCase):
    def test_storm_pipeline(self) -> None:
        index = SimpleSearchIndex([Document(doc_id="d1", text="Agent loop decide act observe.")])
        model = MockLLM(
            [
                '{"sections":["S1"]}',
                '{"query":"agent loop"}',
                "section content [d1]",
                "final article",
            ]
        )
        article = storm_write_article(model, topic="x", index=index, sections_rounds=1, top_k=1)
        self.assertEqual(article.sections[0].title, "S1")
        self.assertIn("final", article.article)


if __name__ == "__main__":
    unittest.main()

