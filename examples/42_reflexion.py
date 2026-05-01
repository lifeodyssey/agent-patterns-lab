from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.reflexion import VerificationResult, reflexion
from agent_patterns_lab.runtime import InMemoryKV, MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    kv = InMemoryKV()

    model = MockLLM(
        [
            "bad answer",
            '{"lesson":"State the answer as a single number."}',
            "42",
        ]
    )

    def verify(answer: str) -> VerificationResult:
        ok = answer.strip() == "42"
        return VerificationResult(ok=ok, feedback="Expected exactly: 42" if not ok else "")

    out = reflexion(
        model,
        task="What is 6 * 7?",
        verify=verify,
        memory_get=kv.get,
        memory_set=kv.set,
        tracer=tracer,
        rounds=2,
    )

    print(out)
    trace_path = tracer.export_jsonl(Path(".traces") / "42_reflexion.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

