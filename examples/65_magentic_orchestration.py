from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.magentic_orchestration import Specialist, run_magentic_orchestration
from agent_patterns_lab.runtime import MockLLM, RunLimits, Tracer


def main() -> None:
    tracer = Tracer()

    orchestrator = MockLLM(
        [
            '{"type":"delegate","agent":"calc","task":"Compute 3+4"}',
            '{"type":"delegate","agent":"calc","task":"Compute 3+4"}',
            '{"type":"final","answer":"3+4=7."}',
        ]
    )

    specialists = [
        Specialist(
            name="calc",
            description="Arithmetic specialist.",
            model=MockLLM(["7", "7"]),
        )
    ]

    out = run_magentic_orchestration(
        orchestrator,
        specialists,
        task="Compute 3+4.",
        limits=RunLimits(max_steps=5),
        stall_limit=1,
        tracer=tracer,
    )
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "65_magentic_orchestration.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

