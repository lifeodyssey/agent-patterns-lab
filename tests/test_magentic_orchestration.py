import unittest

from agent_patterns_lab.patterns.magentic_orchestration import Specialist, run_magentic_orchestration
from agent_patterns_lab.runtime import MockLLM, RunLimits


class TestMagenticOrchestration(unittest.TestCase):
    def test_delegate_then_final(self) -> None:
        orchestrator = MockLLM(
            [
                '{"type":"delegate","agent":"calc","task":"Compute 1+1"}',
                '{"type":"final","answer":"2"}',
            ]
        )
        specialists = [Specialist(name="calc", description="d", model=MockLLM(["2"]))]
        out = run_magentic_orchestration(orchestrator, specialists, task="t", limits=RunLimits(max_steps=4))
        self.assertEqual(out, "2")


if __name__ == "__main__":
    unittest.main()

