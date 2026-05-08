from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_patterns_lab.patterns.react import run_react
from agent_patterns_lab.runtime import MockLLM, RunLimits, Tool, ToolRegistry, Tracer


def as_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> None:
    tracer = Tracer()

    def get_weather(args: dict[str, Any]) -> str:
        city = args["city"]
        date = args["date"]
        return as_json(
            {
                "city": city,
                "date": date,
                "forecast": "light rain after 15:00",
                "temperature_c": "18-23",
                "packing_hint": "umbrella and light jacket",
            }
        )

    def search_places(args: dict[str, Any]) -> str:
        return as_json(
            {
                "city": args["city"],
                "matches": [
                    "West Lake: best before the afternoon rain",
                    "China National Tea Museum: indoor-friendly and good for tea lovers",
                    "Hefang Street: local snacks and easy evening walk",
                ],
            }
        )

    def estimate_route(args: dict[str, Any]) -> str:
        places = args["places"]
        return as_json(
            {
                "route": places,
                "total_transit_minutes": 55,
                "note": "Keep West Lake first, move indoor after rain starts.",
            }
        )

    tools = ToolRegistry(
        [
            Tool(
                name="get_weather",
                description="Get a simple weather forecast for a city and date",
                handler=get_weather,
            ),
            Tool(
                name="search_places",
                description="Find travel places based on city, interests, and constraints",
                handler=search_places,
            ),
            Tool(
                name="estimate_route",
                description="Estimate travel time for a short list of places",
                handler=estimate_route,
            ),
        ]
    )

    model = MockLLM(
        [
            as_json(
                {
                    "type": "tool",
                    "tool": "get_weather",
                    "args": {"city": "Hangzhou", "date": "tomorrow"},
                }
            ),
            as_json(
                {
                    "type": "tool",
                    "tool": "search_places",
                    "args": {
                        "city": "Hangzhou",
                        "interests": ["tea", "local food", "easy walking"],
                        "constraint": "light rain after 15:00",
                    },
                }
            ),
            as_json(
                {
                    "type": "tool",
                    "tool": "estimate_route",
                    "args": {
                        "places": [
                            "West Lake",
                            "China National Tea Museum",
                            "Hefang Street",
                        ]
                    },
                }
            ),
            as_json(
                {
                    "type": "final",
                    "answer": (
                        "Plan: West Lake in the morning, China National Tea Museum after "
                        "the rain starts, then Hefang Street for snacks. Pack an umbrella, "
                        "a light jacket, and comfortable shoes."
                    ),
                }
            ),
        ]
    )

    out = run_react(
        model,
        task=(
            "Plan a relaxed one-day Hangzhou trip for tomorrow. "
            "I like tea, local food, and easy walking. Tell me what to pack."
        ),
        tools=tools,
        limits=RunLimits(max_steps=6),
        tracer=tracer,
    )

    print(out)
    trace_path = tracer.export_jsonl(Path(".traces") / "21_react_loop.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()
