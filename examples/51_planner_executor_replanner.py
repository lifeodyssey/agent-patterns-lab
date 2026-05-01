from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.planner_executor_replanner import planner_executor_replanner
from agent_patterns_lab.runtime import MockLLM, RunLimits, Tracer


def main() -> None:
    tracer = Tracer()

    planner = MockLLM(['{"plan":["Step A","Step B"]}'])
    executor = MockLLM(["did A", "did B"])
    replanner = MockLLM(
        [
            '{"action":"continue","plan":[],"answer":""}',
            '{"action":"final","plan":[],"answer":"All done"}',
        ]
    )

    result = planner_executor_replanner(
        planner,
        executor,
        replanner,
        task="Do A then B.",
        limits=RunLimits(max_steps=5),
        tracer=tracer,
    )

    print(result.answer)
    trace_path = tracer.export_jsonl(Path(".traces") / "51_planner_executor_replanner.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

