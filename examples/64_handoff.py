from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.handoff import HandoffAgent, run_handoff
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()

    router = MockLLM(['{"type":"handoff","to":"math","summary":"This is a simple arithmetic question: compute 9+1."}'])

    agents = [
        HandoffAgent(
            name="math",
            description="Arithmetic specialist.",
            model=MockLLM(["10"]),
        ),
        HandoffAgent(
            name="writer",
            description="Writing specialist.",
            model=MockLLM(["(unused)"]),
        ),
    ]

    out = run_handoff(router, agents, task="What is 9+1?", tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "64_handoff.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

