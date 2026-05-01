from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from agent_patterns_lab.runtime.tracing import Tracer
from agent_patterns_lab.runtime.types import Message


class MissingOptionalDependency(ImportError):
    pass


@dataclass(frozen=True, slots=True)
class AnthropicMessagesModel:
    """
    Thin adapter for the Anthropic Python SDK that implements `runtime.model.Model`.

    Notes:
    - Anthropic Messages API uses `system=...` plus `messages=[{role,user|assistant,content}]`
    - Our runtime also has `role="tool"` messages; we convert them into user messages.
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

        if self.client is not None:
            object.__setattr__(self, "_client", self.client)
            return

        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is not set and api_key was not provided")

        try:
            from anthropic import Anthropic  # type: ignore[import-not-found]
        except Exception as e:
            raise MissingOptionalDependency(
                'Anthropic SDK not installed. Install with: `uv sync --extra anthropic` (or add "anthropic" extra).'
            ) from e

        kwargs: dict[str, Any] = {"api_key": key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.timeout_s is not None:
            kwargs["timeout"] = self.timeout_s

        object.__setattr__(self, "_client", Anthropic(**kwargs))

    def complete(self, messages: Sequence[Message], *, tracer: Tracer | None = None) -> str:
        system, payload = _to_anthropic(messages)

        if tracer is not None:
            tracer.emit(
                "llm.complete",
                model=f"anthropic:{self.model}",
                input=_messages_for_trace(messages, include_content=self.trace_content),
            )

        try:
            resp = self._client.messages.create(  # type: ignore[attr-defined]
                model=self.model,
                system=system,
                messages=payload,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            if tracer is not None:
                tracer.emit("llm.error", model=f"anthropic:{self.model}", error=str(e))
            raise

        text = _extract_text(resp)
        if tracer is not None:
            tracer.emit(
                "llm.result",
                model=f"anthropic:{self.model}",
                output=text if self.trace_content else {"chars": len(text)},
            )
        return text


def _to_anthropic(messages: Sequence[Message]) -> tuple[str | None, list[dict[str, Any]]]:
    system_parts: list[str] = []
    out: list[dict[str, Any]] = []
    for m in messages:
        if m.role == "system":
            system_parts.append(m.content)
            continue

        if m.role == "tool":
            tool_name = m.name or "tool"
            out.append({"role": "user", "content": f"[tool:{tool_name}] {m.content}"})
            continue

        if m.role not in ("user", "assistant"):
            out.append({"role": "user", "content": m.content})
            continue

        out.append({"role": m.role, "content": m.content})

    system = "\n\n".join([p for p in system_parts if p.strip()]) or None
    return system, out


def _extract_text(resp: Any) -> str:
    # Common shape: resp.content is a list of blocks with `.text`
    content = getattr(resp, "content", None)
    if content is None and isinstance(resp, Mapping):
        content = resp.get("content")

    if isinstance(content, list) and content:
        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if text is None and isinstance(block, Mapping):
                text = block.get("text")
            if text is not None:
                parts.append(str(text))
        if parts:
            return "".join(parts)

    # Some shapes have `resp.completion` (older)
    completion = getattr(resp, "completion", None)
    if completion is None and isinstance(resp, Mapping):
        completion = resp.get("completion")
    if completion is not None:
        return str(completion)

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

