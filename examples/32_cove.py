from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.cove import ClaimVerification, chain_of_verification
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()

    model = MockLLM(
        [
            "Paris is the capital of France. Paris has 3 moons.",
            '{"claims":["Paris is the capital of France","Paris has 3 moons"]}',
            "Paris is the capital of France.",
        ]
    )

    def verify(claim: str) -> ClaimVerification:
        if "capital of France" in claim:
            return ClaimVerification(claim=claim, ok=True, evidence="widely known")
        if "3 moons" in claim:
            return ClaimVerification(claim=claim, ok=False, evidence="unsupported")
        return ClaimVerification(claim=claim, ok=False, evidence="unknown")

    out = chain_of_verification(model, question="Tell me about Paris.", verify_claim=verify, tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "32_cove.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

