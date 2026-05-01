from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.runtime import Message, MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(["Hello from MockLLM (single-shot)"])

    messages = [Message(role="user", content="Say hello.")]
    answer = model.complete(messages, tracer=tracer)

    print(answer)
    trace_path = tracer.export_jsonl(Path(".traces") / "00_single_shot.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()
