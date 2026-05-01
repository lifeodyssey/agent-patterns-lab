from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.runtime import MockLLM, Tracer
from agent_patterns_lab.patterns.workflow_chaining import PromptStep, run_prompt_chain


def main() -> None:
    tracer = Tracer()
    model = MockLLM(
        [
            "1) Intro\n2) Key points\n3) Conclusion",
            "Summary: This is a short summary based on the outline.",
        ]
    )

    steps = [
        PromptStep(name="outline", user_prompt="Create an outline for: {input}"),
        PromptStep(name="summarize", user_prompt="Summarize this outline:\n{input}"),
    ]

    out = run_prompt_chain(model, initial_input="Agent design patterns", steps=steps, tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "11_prompt_chaining.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

