from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, TypeAlias

from .tracing import Tracer
from .types import Message, ScriptedResponsesExhausted

MockResponse: TypeAlias = str | Callable[[Sequence[Message]], str]


class MockLLM:
    """
    Offline-first scripted model.

    Use it to make `examples/` and `tests/` deterministic:
    each `complete()` consumes one scripted response (string or callable).
    """

    def __init__(self, scripted: Sequence[MockResponse]) -> None:
        self._scripted: list[MockResponse] = list(scripted)

    def remaining(self) -> int:
        return len(self._scripted)

    def complete(self, messages: Sequence[Message], *, tracer: Tracer | None = None) -> str:
        if not self._scripted:
            raise ScriptedResponsesExhausted("MockLLM scripted responses exhausted")

        step = self._scripted.pop(0)
        text = step(messages) if callable(step) else step

        if tracer is not None:
            tracer.emit(
                "llm.complete",
                model="mock",
                input=[_msg_for_trace(m) for m in messages],
                output=text,
                remaining=len(self._scripted),
            )

        return text


def _msg_for_trace(message: Message) -> dict[str, Any]:
    out: dict[str, Any] = {"role": message.role, "content": message.content}
    if message.name:
        out["name"] = message.name
    if message.meta:
        out["meta"] = message.meta
    return out

