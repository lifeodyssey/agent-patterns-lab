import unittest

from agent_patterns_lab.patterns.llm_compiler import compile_to_dag, execute_dag, llm_compiler
from agent_patterns_lab.runtime import MockLLM
from agent_patterns_lab.runtime.structured import SchemaValidationError


class TestLlmCompiler(unittest.TestCase):
    def test_compiles_and_executes(self) -> None:
        model = MockLLM(
            [
                '{"tasks":[{"id":"t1","instruction":"x","deps":[]}],"final":{"instruction":"assemble"}}',
                "out1",
                "final",
            ]
        )
        out = llm_compiler(model, task="x")
        self.assertEqual(out, "final")

    def test_cycle_rejected(self) -> None:
        model = MockLLM(
            [
                '{"tasks":[{"id":"t1","instruction":"x","deps":["t2"]},{"id":"t2","instruction":"y","deps":["t1"]}],"final":{"instruction":"assemble"}}'
            ]
        )
        with self.assertRaises(SchemaValidationError):
            compile_to_dag(model, task="x", max_retries=0)

    def test_execute_order(self) -> None:
        model = MockLLM(
            [
                "out1",
                "out2",
                "final",
            ]
        )
        compiled = compile_to_dag(
            MockLLM(
                [
                    '{"tasks":[{"id":"t1","instruction":"x","deps":[]},{"id":"t2","instruction":"y","deps":["t1"]}],"final":{"instruction":"assemble"}}'
                ]
            ),
            task="x",
        )
        outputs = execute_dag(model, compiled)
        self.assertEqual(outputs["t1"], "out1")
        self.assertEqual(outputs["t2"], "out2")
        self.assertEqual(outputs["__final__"], "final")


if __name__ == "__main__":
    unittest.main()
