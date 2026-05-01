import unittest

from agent_patterns_lab.patterns.workflow_chaining import PromptStep, run_prompt_chain
from agent_patterns_lab.runtime import MockLLM, Tracer


class TestPromptChaining(unittest.TestCase):
    def test_runs_steps_in_order_and_traces(self) -> None:
        tracer = Tracer()
        model = MockLLM(["a", "b", "c"])
        steps = [
            PromptStep(name="s1", user_prompt="1: {input}"),
            PromptStep(name="s2", user_prompt="2: {input}"),
            PromptStep(name="s3", user_prompt="3: {input}"),
        ]
        out = run_prompt_chain(model, initial_input="x", steps=steps, tracer=tracer)
        self.assertEqual(out, "c")
        self.assertEqual([e.name for e in tracer.events if e.name == "workflow.step"], ["workflow.step"] * 3)


if __name__ == "__main__":
    unittest.main()

