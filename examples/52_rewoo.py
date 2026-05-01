from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.rewoo import rewoo
from agent_patterns_lab.runtime import MockLLM, Tool, ToolRegistry, Tracer


def main() -> None:
    tracer = Tracer()

    def add(args: dict) -> str:
        return str(int(args["a"]) + int(args["b"]))

    tools = ToolRegistry([Tool(name="add", description="Add two integers", handler=add)])

    model = MockLLM(
        [
            '{"tool_calls":[{"tool":"add","args":{"a":2,"b":2},"purpose":"compute 2+2"}]}',
            "Answer: 4",
        ]
    )

    result = rewoo(model, task="Compute 2+2.", tools=tools, tracer=tracer)
    print(result.answer)

    trace_path = tracer.export_jsonl(Path(".traces") / "52_rewoo.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

