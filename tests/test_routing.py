import unittest

from agent_patterns_lab.patterns.routing import Route, Rule, llm_route, rule_route
from agent_patterns_lab.runtime import MockLLM, Tracer


class TestRouting(unittest.TestCase):
    def test_rule_route_first_match_wins(self) -> None:
        out = rule_route(
            "hello",
            rules=[
                Rule(route="a", predicate=lambda _: True),
                Rule(route="b", predicate=lambda _: True),
            ],
            default="z",
        )
        self.assertEqual(out, "a")

    def test_rule_route_default(self) -> None:
        out = rule_route(
            "hello",
            rules=[Rule(route="a", predicate=lambda _: False)],
            default="z",
        )
        self.assertEqual(out, "z")

    def test_llm_route_retries_on_invalid_choice(self) -> None:
        tracer = Tracer()
        model = MockLLM(['{"route":"invalid"}', '{"route":"writing"}'])
        out = llm_route(
            model,
            text="write a poem",
            routes=[Route(name="math"), Route(name="writing")],
            tracer=tracer,
            max_retries=1,
        )
        self.assertEqual(out, "writing")
        self.assertEqual(model.remaining(), 0)
        self.assertTrue(any(e.name == "structured.failure" for e in tracer.events))


if __name__ == "__main__":
    unittest.main()

