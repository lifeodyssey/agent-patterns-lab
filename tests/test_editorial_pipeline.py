import json
import unittest
from pathlib import Path

from agent_patterns_lab.runtime import MockLLM
from agent_patterns_lab.runtime.editorial.pipeline import EditorialPipeline
from agent_patterns_lab.runtime.editorial.rubric import parse_rubric_review


class TestEditorialRubricParsing(unittest.TestCase):
    def test_parse_valid_review(self) -> None:
        payload = {
            "scores": {
                "clarity": 4,
                "actionability": 3,
                "boundaries": 2,
                "example_quality": 5,
                "terminology_consistency": 4,
            },
            "summary": "ok",
            "top_fixes": ["a", "b"],
            "term_notes": [],
            "style_notes": ["c"],
        }
        review = parse_rubric_review(payload)
        self.assertEqual(review.scores.clarity, 4)
        self.assertEqual(review.scores.example_quality, 5)
        self.assertEqual(review.summary, "ok")
        self.assertEqual(review.top_fixes, ["a", "b"])


class TestEditorialPipeline(unittest.TestCase):
    def test_offline_pipeline_skips_rewrite(self) -> None:
        pipe = EditorialPipeline(mode="offline", locale="en")
        md = "# Title\n\n## What Problem It Solves\n\nx\n"
        out = pipe.run(path=Path("docs/en/x.md"), markdown=md)
        self.assertEqual(out.final_markdown, md)
        self.assertIn("skipped: offline mode", out.revise.summary)
        self.assertIn("skipped: offline mode", out.polish.summary)

    def test_live_pipeline_calls_models_in_order(self) -> None:
        reviewer = MockLLM(
            [
                json.dumps(
                    {
                        "scores": {
                            "clarity": 2,
                            "actionability": 1,
                            "boundaries": 1,
                            "example_quality": 1,
                            "terminology_consistency": 2,
                        },
                        "summary": "v0",
                        "top_fixes": ["add example"],
                        "term_notes": [],
                        "style_notes": [],
                    }
                ),
                json.dumps(
                    {
                        "scores": {
                            "clarity": 3,
                            "actionability": 3,
                            "boundaries": 2,
                            "example_quality": 2,
                            "terminology_consistency": 3,
                        },
                        "summary": "v1",
                        "top_fixes": [],
                        "term_notes": [],
                        "style_notes": [],
                    }
                ),
                json.dumps(
                    {
                        "scores": {
                            "clarity": 4,
                            "actionability": 4,
                            "boundaries": 3,
                            "example_quality": 3,
                            "terminology_consistency": 4,
                        },
                        "summary": "v2",
                        "top_fixes": [],
                        "term_notes": [],
                        "style_notes": [],
                    }
                ),
            ]
        )
        writer = MockLLM(["# Revised\n\nSome content.\n"])
        polisher = MockLLM(["# Polished\n\nSome content, but nicer.\n"])

        pipe = EditorialPipeline(mode="live", locale="en", writer=writer, reviewer=reviewer, polisher=polisher)
        out = pipe.run(path=Path("docs/en/x.md"), markdown="# Original\n")
        self.assertTrue(out.final_markdown.startswith("# Polished"))
        self.assertEqual(out.review.summary, "v0")
        self.assertEqual(out.revise.summary, "v1")
        self.assertEqual(out.polish.summary, "v2")


if __name__ == "__main__":
    unittest.main()

