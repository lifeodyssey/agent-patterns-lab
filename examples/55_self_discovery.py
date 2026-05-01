from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.self_discovery import self_discovery
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(['{"modules":["decompose","verify"]}', "Answer using decompose+verify"])

    result = self_discovery(
        model,
        task="Solve something.",
        available_modules=["decompose", "verify", "analogy"],
        tracer=tracer,
    )

    print(result.answer)
    trace_path = tracer.export_jsonl(Path(".traces") / "55_self_discovery.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

