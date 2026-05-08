from __future__ import annotations

import json
from pathlib import Path

from agent_patterns_lab.runtime import Tool, ToolRegistry, Tracer


def main() -> None:
    tracer = Tracer()

    def get_weather(args: dict) -> str:
        return json.dumps(
            {
                "city": args["city"],
                "date": args["date"],
                "forecast": "light rain after 15:00",
                "temperature_c": "18-23",
            },
            ensure_ascii=False,
        )

    tools = ToolRegistry(
        [
            Tool(
                name="get_weather",
                description="Get a simple weather forecast for a city and date",
                handler=get_weather,
            )
        ]
    )

    out = tools.call("get_weather", {"city": "Hangzhou", "date": "tomorrow"}, tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "20_tool_calling.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()
