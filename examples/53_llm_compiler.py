from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.llm_compiler import llm_compiler
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(
        [
            '{"tasks":[{"id":"t1","instruction":"Write X","deps":[]},{"id":"t2","instruction":"Write Y","deps":["t1"]}],"final":{"instruction":"Combine t1 and t2"}}',
            "X",
            "Y (using X)",
            "Final: X + Y",
        ]
    )

    out = llm_compiler(model, task="Produce X then Y, then combine.", tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "53_llm_compiler.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

