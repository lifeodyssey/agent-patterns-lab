from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.runtime import Tool, ToolRegistry, Tracer


def main() -> None:
    tracer = Tracer()

    def add(args: dict) -> str:
        a = int(args.get("a", 0))
        b = int(args.get("b", 0))
        return str(a + b)

    tools = ToolRegistry([Tool(name="add", description="Add two numbers", handler=add)])

    out = tools.call("add", {"a": 2, "b": 2}, tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "20_tool_calling.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

