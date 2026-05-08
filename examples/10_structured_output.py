from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_patterns_lab.runtime import Message, MockLLM, SchemaValidationError, Tracer, structured_complete


def main() -> None:
    tracer = Tracer()

    model = MockLLM(
        [
            '{"city":"Hangzhou","items":["West Lake","Tea Museum"]}',
            '{"city":"Hangzhou","morning":"West Lake","afternoon":"China National Tea Museum","evening":"Hefang Street","packing":["umbrella","light jacket","comfortable shoes"]}',
        ]
    )

    messages = [
        Message(
            role="system",
            content=(
                "Return ONLY JSON with keys: city, morning, afternoon, evening, packing. "
                "packing must be a list of strings."
            ),
        ),
        Message(role="user", content="Create a one-day Hangzhou itinerary."),
    ]

    def parse_itinerary(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise SchemaValidationError("expected a JSON object")
        required = ["city", "morning", "afternoon", "evening", "packing"]
        for key in required:
            if key not in value:
                raise SchemaValidationError(f'missing key "{key}"')
        if not isinstance(value["packing"], list) or not all(isinstance(x, str) for x in value["packing"]):
            raise SchemaValidationError('"packing" must be a list of strings')
        return value

    itinerary = structured_complete(
        model,
        messages,
        parser=parse_itinerary,
        schema_hint='{"city":"...","morning":"...","afternoon":"...","evening":"...","packing":["..."]}',
        tracer=tracer,
    )

    print(itinerary)
    trace_path = tracer.export_jsonl(Path(".traces") / "10_structured_output.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()
