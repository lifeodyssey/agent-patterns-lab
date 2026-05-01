from __future__ import annotations

import os
from pathlib import Path

from agent_patterns_lab.runtime import Message, Tracer
from agent_patterns_lab.runtime.adapters.anthropic_model import AnthropicMessagesModel, MissingOptionalDependency


def main() -> None:
    tracer = Tracer()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY to run this example.")
        return

    model_name = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

    try:
        model = AnthropicMessagesModel(model=model_name, api_key=api_key, trace_content=False, max_tokens=256)
    except MissingOptionalDependency as e:
        print(str(e))
        print('Install with: `uv sync --extra anthropic`')
        return

    out = model.complete(
        [
            Message(role="system", content="You are a helpful assistant. Reply in one sentence."),
            Message(role="user", content="Say hello."),
        ],
        tracer=tracer,
    )

    print(out)
    trace_path = tracer.export_jsonl(Path(".traces") / "71_anthropic_sdk_optional.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

