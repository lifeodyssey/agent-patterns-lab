from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.plan_and_solve import plan_and_solve
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(
        [
            '{"plan":["Compute 2+2","Return the result"]}',
            "2+2=4",
            "Result is 4",
            "Final answer: 4",
        ]
    )

    result = plan_and_solve(model, task="Compute 2+2.", tracer=tracer)
    print(result.answer)

    trace_path = tracer.export_jsonl(Path(".traces") / "50_plan_and_solve.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

