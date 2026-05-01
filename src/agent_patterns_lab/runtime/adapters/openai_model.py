from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from agent_patterns_lab.runtime.tracing import Tracer
from agent_patterns_lab.runtime.types import Message


class MissingOptionalDependency(ImportError):
    pass


@dataclass(frozen=True, slots=True)
class OpenAIChatModel:
    """
    Thin adapter for the OpenAI Python SDK that implements `runtime.model.Model`.

    Design goals:
    - Keep the core runtime offline-first (no hard dependency on the SDK)
    - Avoid importing `openai` at module import time
    - Be compatible with common OpenAI SDK response shapes
    """

    model: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.0
    max_tokens: int = 512
    timeout_s: float | None = None
    trace_content: bool = False
    client: Any | None = None
    _client: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be > 0")

        # NOTE: We keep the actual client in a private attribute via object.__setattr__
        # to preserve the frozen dataclass ergonomics.
        if self.client is not None:
            object.__setattr__(self, "_client", self.client)
            return

        key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set and api_key was not provided")

        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except Exception as e:
            raise MissingOptionalDependency(
                'OpenAI SDK not installed. Install with: `uv sync --extra openai` (or add "openai" extra).'
            ) from e

        kwargs: dict[str, Any] = {"api_key": key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.timeout_s is not None:
            # OpenAI SDK accepts `timeout` in many versions.
            kwargs["timeout"] = self.timeout_s

        object.__setattr__(self, "_client", OpenAI(**kwargs))

    def complete(self, messages: Sequence[Message], *, tracer: Tracer | None = None) -> str:
        payload = _to_openai_messages(messages)
        if tracer is not None:
            tracer.emit(
                "llm.complete",
                model=f"openai:{self.model}",
                input=_messages_for_trace(messages, include_content=self.trace_content),
            )

        try:
            create = self._client.chat.completions.create  # type: ignore[attr-defined]
            resp = create(
                model=self.model,
                messages=payload,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            if tracer is not None:
                tracer.emit("llm.error", model=f"openai:{self.model}", error=str(e))
            raise

        text = _extract_text(resp)
        if tracer is not None:
            tracer.emit(
                "llm.result",
                model=f"openai:{self.model}",
                output=text if self.trace_content else {"chars": len(text)},
            )
        return text


def _to_openai_messages(messages: Sequence[Message]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in messages:
        if m.role == "tool":
            tool_name = m.name or "tool"
            out.append({"role": "user", "content": f"[tool:{tool_name}] {m.content}"})
            continue
        d: dict[str, Any] = {"role": m.role, "content": m.content}
        if m.name:
            d["name"] = m.name
        out.append(d)
    return out


def _extract_text(resp: Any) -> str:
    # Common SDK object shape: resp.choices[0].message.content
    choices = getattr(resp, "choices", None)
    if choices is None and isinstance(resp, Mapping):
        choices = resp.get("choices")
    if choices:
        first = choices[0]
        message = getattr(first, "message", None)
        if message is None and isinstance(first, Mapping):
            message = first.get("message")
        if message is not None:
            content = getattr(message, "content", None)
            if content is None and isinstance(message, Mapping):
                content = message.get("content")
            if content is not None:
                return str(content)

        # Some legacy shapes: choice.text
        text = getattr(first, "text", None)
        if text is None and isinstance(first, Mapping):
            text = first.get("text")
        if text is not None:
            return str(text)

    # Last resort: stringification.
    return str(resp)


def _messages_for_trace(messages: Sequence[Message], *, include_content: bool) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in messages:
        item: dict[str, Any] = {"role": m.role}
        if m.name:
            item["name"] = m.name
        if include_content:
            item["content"] = m.content
        else:
            item["chars"] = len(m.content)
        out.append(item)
    return out
