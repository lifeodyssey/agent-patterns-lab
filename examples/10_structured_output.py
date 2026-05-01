from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_patterns_lab.runtime import Message, MockLLM, SchemaValidationError, Tracer, structured_complete


def main() -> None:
    tracer = Tracer()

    # First response is valid JSON but fails schema validation; second fixes it.
    model = MockLLM(
        [
            '{"answer": 123}',
            '{"answer": "hello"}',
        ]
    )

    messages = [
        Message(role="system", content='Return ONLY JSON like: {"answer": "<string>"}'),
        Message(role="user", content="Say hello."),
    ]

    def parse_answer(value: Any) -> str:
        if not isinstance(value, dict):
            raise SchemaValidationError("expected a JSON object")
        answer = value.get("answer")
        if not isinstance(answer, str):
            raise SchemaValidationError('expected key "answer" to be a string')
        return answer

    answer = structured_complete(
        model,
        messages,
        parser=parse_answer,
        schema_hint='{"answer":"<string>"}',
        tracer=tracer,
    )

    print(answer)
    trace_path = tracer.export_jsonl(Path(".traces") / "10_structured_output.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

