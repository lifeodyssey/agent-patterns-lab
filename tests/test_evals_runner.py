import tempfile
import unittest
from pathlib import Path

from agent_patterns_lab.runtime.evals import all_tasks, run_eval_suite


class TestEvalHarness(unittest.TestCase):
    def test_offline_eval_suite_passes_and_writes_reports(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        data_dir = repo_root / "data"

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            trace_dir = Path(tmp) / "traces"

            summary, outcomes, _meta = run_eval_suite(
                all_tasks(),
                out_dir=out_dir,
                trace_dir=trace_dir,
                data_dir=data_dir,
                mode="offline",
                write_markdown=True,
                write_json=True,
            )

            self.assertGreaterEqual(summary.total, 10)
            self.assertEqual(summary.failed, 0)
            self.assertEqual(summary.errored, 0)

            self.assertTrue(any(p.name.endswith(".md") for p in out_dir.iterdir()))
            self.assertTrue(any(p.name.endswith(".json") for p in out_dir.iterdir()))

            # Every task should have a trace.
            for o in outcomes:
                self.assertIsNotNone(o.trace_path)


if __name__ == "__main__":
    unittest.main()

