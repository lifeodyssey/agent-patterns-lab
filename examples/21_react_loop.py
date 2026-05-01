from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.react import run_react
from agent_patterns_lab.runtime import MockLLM, RunLimits, Tool, ToolRegistry, Tracer


def main() -> None:
    tracer = Tracer()

    def add(args: dict) -> str:
        return str(int(args["a"]) + int(args["b"]))

    tools = ToolRegistry([Tool(name="add", description="Add two integers", handler=add)])

    model = MockLLM(
        [
            '{"type":"tool","tool":"add","args":{"a":2,"b":2}}',
            '{"type":"final","answer":"4"}',
        ]
    )

    out = run_react(
        model,
        task="Compute 2+2.",
        tools=tools,
        limits=RunLimits(max_steps=5),
        tracer=tracer,
    )

    print(out)
    trace_path = tracer.export_jsonl(Path(".traces") / "21_react_loop.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

