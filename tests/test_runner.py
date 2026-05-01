import unittest

from agent_patterns_lab.runtime import MaxStepsExceeded, RunLimits, Tracer, run_loop


class TestRunner(unittest.TestCase):
    def test_run_loop_stops_on_value(self) -> None:
        tracer = Tracer()

        def step(i: int):
            return "ok" if i == 2 else None

        out = run_loop(step, limits=RunLimits(max_steps=10), tracer=tracer)
        self.assertEqual(out, "ok")
        self.assertTrue(any(e.name == "loop.done" for e in tracer.events))

    def test_run_loop_raises_on_max_steps(self) -> None:
        def step(_i: int):
            return None

        with self.assertRaises(MaxStepsExceeded):
            run_loop(step, limits=RunLimits(max_steps=3))


if __name__ == "__main__":
    unittest.main()

