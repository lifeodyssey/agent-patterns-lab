from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, TypeVar

from .model import Model
from .tracing import Tracer
from .types import Message

T = TypeVar("T")


class StructuredOutputError(RuntimeError):
    pass


class JsonExtractionError(StructuredOutputError):
    pass


class SchemaValidationError(StructuredOutputError):
    pass


@dataclass(frozen=True, slots=True)
class StructuredOutputResult:
    raw_text: str
    json_value: Any


def structured_complete(
    model: Model,
    messages: Sequence[Message],
    *,
    parser: Callable[[Any], T],
    schema_hint: str | None = None,
    max_retries: int = 2,
    tracer: Tracer | None = None,
) -> T:
    """
    Ask the model for JSON, parse it, validate it, and retry with a repair prompt if needed.

    - `parser` is responsible for turning the parsed JSON into a typed result (and raising on errors).
    - `schema_hint` (optional) is appended to the repair prompt to help the model self-correct.
    """
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    base_messages = list(messages)
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        if tracer is not None:
            tracer.emit("structured.attempt", attempt=attempt, max_retries=max_retries)

        raw = model.complete(base_messages, tracer=tracer)
        try:
            extracted = extract_json_value(raw)
            result = parser(extracted.json_value)
        except StructuredOutputError as e:
            last_error = e
            if tracer is not None:
                tracer.emit("structured.failure", attempt=attempt, error=str(e))

            if attempt >= max_retries:
                raise

            base_messages = list(messages)
            base_messages.append(Message(role="assistant", content=raw))
            base_messages.append(
                Message(
                    role="user",
                    content=_repair_prompt(error=str(e), schema_hint=schema_hint),
                )
            )
            continue
        except Exception as e:  # parser raised non-StructuredOutputError
            last_error = e
            if tracer is not None:
                tracer.emit("structured.failure", attempt=attempt, error=str(e))

            if attempt >= max_retries:
                raise SchemaValidationError(str(e)) from e

            base_messages = list(messages)
            base_messages.append(Message(role="assistant", content=raw))
            base_messages.append(
                Message(
                    role="user",
                    content=_repair_prompt(error=str(e), schema_hint=schema_hint),
                )
            )
            continue

        if tracer is not None:
            tracer.emit("structured.success", attempt=attempt)
        return result

    # Unreachable, but keeps type-checkers happy.
    raise StructuredOutputError(str(last_error) if last_error else "structured_complete failed")


def extract_json_value(text: str) -> StructuredOutputResult:
    """
    Best-effort JSON extraction for typical LLM outputs:
    - Accepts raw JSON
    - Accepts fenced blocks (```json ... ```)
    - Accepts extra prose around the JSON (extracts the first parsable JSON value)
    """
    candidate = _strip_code_fence(text).strip()
    if not candidate:
        raise JsonExtractionError("empty response; expected JSON")

    decoder = json.JSONDecoder()

    # Fast path: entire string is JSON.
    try:
        return StructuredOutputResult(raw_text=text, json_value=json.loads(candidate))
    except json.JSONDecodeError:
        pass

    # Slow path: find the first parsable JSON value within the text.
    for idx, ch in enumerate(candidate):
        if ch not in "{[":
            continue
        try:
            value, _end = decoder.raw_decode(candidate[idx:])
            return StructuredOutputResult(raw_text=text, json_value=value)
        except json.JSONDecodeError:
            continue

    raise JsonExtractionError("could not extract a JSON value from model output")


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return text

    # Very small, pragmatic fence stripper.
    # Supports:
    # ```json
    # {...}
    # ```
    lines = stripped.splitlines()
    if len(lines) < 3:
        return text

    if not lines[-1].strip().startswith("```"):
        return text

    inner = "\n".join(lines[1:-1])
    return inner


def _repair_prompt(*, error: str, schema_hint: str | None) -> str:
    prompt = (
        "Your previous response could not be parsed/validated as the required JSON.\n"
        f"Error: {error}\n\n"
        "Return ONLY a JSON value (no markdown, no code fences, no extra text)."
    )
    if schema_hint:
        prompt += "\n\nSchema / constraints:\n" + schema_hint.strip()
    return prompt

