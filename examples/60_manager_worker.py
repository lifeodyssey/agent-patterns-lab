from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.manager_worker import Worker, run_manager_worker
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()

    manager = MockLLM(
        [
            '{"assignments":[{"worker":"math","task":"Compute 2+2"},{"worker":"writer","task":"Explain the result in one sentence"}]}',
            "2+2=4. It is the sum of two and two.",
        ]
    )

    workers = [
        Worker(
            name="math",
            description="Fast arithmetic and exact calculations.",
            model=MockLLM(["4"]),
        ),
        Worker(
            name="writer",
            description="Clear, concise explanations.",
            model=MockLLM(["Because adding 2 and 2 yields 4."]),
        ),
    ]

    out = run_manager_worker(manager, workers, task="What is 2+2? Explain briefly.", tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "60_manager_worker.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

