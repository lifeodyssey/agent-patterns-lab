import unittest

from agent_patterns_lab.patterns.manager_worker import Worker, run_manager_worker
from agent_patterns_lab.runtime import MockLLM


class TestManagerWorker(unittest.TestCase):
    def test_manager_worker_happy_path(self) -> None:
        manager = MockLLM(
            [
                '{"assignments":[{"worker":"w1","task":"Do A"},{"worker":"w2","task":"Do B"}]}',
                "FINAL",
            ]
        )
        w1 = MockLLM(["A_DONE"])
        w2 = MockLLM(["B_DONE"])

        out = run_manager_worker(
            manager,
            [
                Worker(name="w1", description="worker 1", model=w1),
                Worker(name="w2", description="worker 2", model=w2),
            ],
            task="T",
        )
        self.assertEqual(out, "FINAL")
        self.assertEqual(w1.remaining(), 0)
        self.assertEqual(w2.remaining(), 0)

    def test_manager_worker_unknown_worker_raises(self) -> None:
        manager = MockLLM(['{"assignments":[{"worker":"missing","task":"x"}]}', "ignored"])
        with self.assertRaises(KeyError):
            run_manager_worker(manager, [Worker(name="w1", description="w", model=MockLLM(["x"]))], task="T")


if __name__ == "__main__":
    unittest.main()

