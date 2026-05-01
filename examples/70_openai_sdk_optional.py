from __future__ import annotations

import os
from pathlib import Path

from agent_patterns_lab.runtime import Message, Tracer
from agent_patterns_lab.runtime.adapters.openai_model import MissingOptionalDependency, OpenAIChatModel


def main() -> None:
    tracer = Tracer()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY to run this example.")
        return

    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    try:
        model = OpenAIChatModel(model=model_name, api_key=api_key, trace_content=False)
    except MissingOptionalDependency as e:
        print(str(e))
        print('Install with: `uv sync --extra openai`')
        return

    out = model.complete(
        [
            Message(role="system", content="You are a helpful assistant. Reply in one sentence."),
            Message(role="user", content="Say hello and tell me today's date format is YYYY-MM-DD."),
        ],
        tracer=tracer,
    )

    print(out)
    trace_path = tracer.export_jsonl(Path(".traces") / "70_openai_sdk_optional.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

