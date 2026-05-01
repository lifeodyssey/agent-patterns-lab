from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.lats import lats_beam_search
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()

    proposer = MockLLM(['{"candidates":["draft A","draft B"]}'])
    evaluator = MockLLM(['{"score": 3}', '{"score": 8}'])

    result = lats_beam_search(
        proposer,
        evaluator,
        task="Write the best draft.",
        depth=1,
        branch_factor=2,
        beam_size=1,
        tracer=tracer,
    )

    print({"best": result.best, "score": result.score})
    trace_path = tracer.export_jsonl(Path(".traces") / "54_lats.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

