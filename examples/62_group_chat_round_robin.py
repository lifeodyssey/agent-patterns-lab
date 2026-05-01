from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.group_chat import ChatAgent, run_group_chat_round_robin
from agent_patterns_lab.runtime import MockLLM, Tracer


def main() -> None:
    tracer = Tracer()

    planner = ChatAgent(
        name="planner",
        description="Breaks down the task and proposes a solution.",
        model=MockLLM(['{"type":"speak","content":"We can compute 2+2 = 4."}']),
    )
    critic = ChatAgent(
        name="critic",
        description="Checks the solution and finalizes.",
        model=MockLLM(['{"type":"final","answer":"2+2=4."}']),
    )

    out = run_group_chat_round_robin([planner, critic], task="Compute 2+2.", max_rounds=2, tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "62_group_chat_round_robin.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

