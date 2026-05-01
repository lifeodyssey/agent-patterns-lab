from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.routing import Route, Rule, llm_route, rule_route
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(['{"route":"writing"}'])

    text1 = "Compute 2+2."
    picked1 = rule_route(
        text1,
        rules=[
            Rule(route="math", predicate=lambda t: any(ch.isdigit() for ch in t)),
            Rule(route="writing", predicate=lambda t: "poem" in t.lower()),
        ],
        default="general",
    )

    text2 = "Write a short poem about the ocean."
    picked2 = llm_route(
        model,
        text=text2,
        routes=[
            Route(name="math", description="Solve math problems"),
            Route(name="writing", description="Write or edit text"),
        ],
        tracer=tracer,
    )

    print({"rule_route": picked1, "llm_route": picked2})

    trace_path = tracer.export_jsonl(Path(".traces") / "12_routing.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

