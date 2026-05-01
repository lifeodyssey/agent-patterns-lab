from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.maker_checker import maker_checker
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()

    maker = MockLLM(["draft v1 (bad)", "draft v2 (better)"])
    checker = MockLLM(
        [
            '{"passed": false, "feedback": "Too vague. Add concrete details."}',
            '{"passed": true, "feedback": ""}',
        ]
    )

    out = maker_checker(maker, checker, task="Write a short project summary.", max_rounds=2, tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "30_maker_checker.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

