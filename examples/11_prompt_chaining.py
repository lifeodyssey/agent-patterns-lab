from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.workflow_chaining import PromptStep, run_prompt_chain
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(
        [
            "Preferences: tea, local food, easy walking. Constraint: relaxed one-day trip.",
            "Draft: Morning West Lake, afternoon Tea Museum, evening Hefang Street.",
            "Final itinerary: West Lake -> China National Tea Museum -> Hefang Street.",
        ]
    )

    steps = [
        PromptStep(name="extract_preferences", user_prompt="Extract travel preferences from: {input}"),
        PromptStep(name="draft_itinerary", user_prompt="Draft an itinerary from these preferences:\n{input}"),
        PromptStep(name="format_final", user_prompt="Format this itinerary as a concise final answer:\n{input}"),
    ]

    out = run_prompt_chain(
        model,
        initial_input="Plan a relaxed one-day Hangzhou trip. I like tea, local food, and easy walking.",
        steps=steps,
        tracer=tracer,
    )
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "11_prompt_chaining.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()
