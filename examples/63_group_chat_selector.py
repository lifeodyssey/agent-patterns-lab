from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.group_chat import ChatAgent, run_group_chat_selector
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()

    selector = MockLLM(['{"speaker":"researcher"}', '{"speaker":"writer"}'])

    researcher = ChatAgent(
        name="researcher",
        description="Provides key facts and evidence.",
        model=MockLLM(['{"type":"speak","content":"Fact: 2+2 equals 4."}']),
    )
    writer = ChatAgent(
        name="writer",
        description="Produces the final user-facing answer.",
        model=MockLLM(['{"type":"final","answer":"2+2=4."}']),
    )

    out = run_group_chat_selector(selector, [researcher, writer], task="Compute 2+2.", max_turns=4, tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "63_group_chat_selector.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

