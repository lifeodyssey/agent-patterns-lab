from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.voting import self_consistency
from agent_patterns_lab.runtime import Message, MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(["A", "B", "A", "A", "B"])

    messages = [Message(role="user", content="Choose A or B.")]
    out = self_consistency(model, messages, n=5, normalize=lambda s: s.strip(), tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "31_voting.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

