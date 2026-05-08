from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.runtime import Message, MockLLM, Tracer


def main() -> None:
    tracer = Tracer()
    model = MockLLM(
        [
            "Got it: you like tea, local food, and easy walking.",
            "I still remember your preferences: tea, local food, and easy walking.",
        ]
    )

    messages: list[Message] = []

    def chat(user_text: str) -> str:
        messages.append(Message(role="user", content=user_text))
        answer = model.complete(messages, tracer=tracer)
        messages.append(Message(role="assistant", content=answer))
        return answer

    print(chat("Remember this: I like tea, local food, and easy walking."))
    print(chat("What preferences did I just give you?"))

    trace_path = tracer.export_jsonl(Path(".traces") / "01_conversation_history.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()
