from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .tracing import Tracer


class GuardrailViolation(RuntimeError):
    def __init__(self, *, stage: str, rail: str, reason: str) -> None:
        super().__init__(f"[{stage}] {rail}: {reason}")
        self.stage = stage
        self.rail = rail
        self.reason = reason


class TripwireTriggered(RuntimeError):
    def __init__(self, *, stage: str, rail: str, reason: str) -> None:
        super().__init__(f"[{stage}] {rail}: {reason}")
        self.stage = stage
        self.rail = rail
        self.reason = reason


class TextGuardrail(Protocol):
    name: str

    def check(self, text: str) -> None: ...


class ToolCallGuardrail(Protocol):
    name: str

    def check(self, tool: str, args: Mapping[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class MaxChars:
    max_chars: int
    name: str = "max_chars"

    def check(self, text: str) -> None:
        if len(text) > self.max_chars:
            raise GuardrailViolation(
                stage="text",
                rail=self.name,
                reason=f"length {len(text)} exceeds {self.max_chars}",
            )


@dataclass(frozen=True, slots=True)
class BannedRegexTripwire:
    patterns: Sequence[str]
    name: str = "banned_regex_tripwire"
    flags: int = re.IGNORECASE

    def check(self, text: str) -> None:
        for pat in self.patterns:
            if re.search(pat, text, flags=self.flags) is not None:
                raise TripwireTriggered(
                    stage="text",
                    rail=self.name,
                    reason=f"matched /{pat}/",
                )


@dataclass(frozen=True, slots=True)
class ToolDenylist:
    denied: set[str]
    name: str = "tool_denylist"

    def check(self, tool: str, args: Mapping[str, Any]) -> None:
        _ = args
        if tool in self.denied:
            raise GuardrailViolation(
                stage="tool",
                rail=self.name,
                reason=f"tool {tool} is denied",
            )


@dataclass(frozen=True, slots=True)
class Guardrails:
    """
    Minimal guardrail hooks for agent loops / orchestrators.

    Stages:
    - input_text: before sending a user task to a model
    - output_text: before returning a final answer
    - tool_call: before executing a tool
    - tool_output_text: after executing a tool, before feeding it back to a model
    """

    input_text: Sequence[TextGuardrail] = field(default_factory=tuple)
    output_text: Sequence[TextGuardrail] = field(default_factory=tuple)
    tool_call: Sequence[ToolCallGuardrail] = field(default_factory=tuple)
    tool_output_text: Sequence[TextGuardrail] = field(default_factory=tuple)

    def check_input(self, text: str, *, tracer: Tracer | None = None) -> None:
        self._run_text("input_text", text, self.input_text, tracer=tracer)

    def check_output(self, text: str, *, tracer: Tracer | None = None) -> None:
        self._run_text("output_text", text, self.output_text, tracer=tracer)

    def check_tool_call(
        self,
        tool: str,
        args: Mapping[str, Any],
        *,
        tracer: Tracer | None = None,
    ) -> None:
        for rail in self.tool_call:
            if tracer is not None:
                tracer.emit("guardrail.check", stage="tool_call", rail=rail.name, tool=tool)
            try:
                rail.check(tool, args)
            except (TripwireTriggered, GuardrailViolation) as e:
                if tracer is not None:
                    tracer.emit("guardrail.blocked", stage="tool_call", rail=rail.name, error=str(e))
                raise

    def check_tool_output(self, text: str, *, tracer: Tracer | None = None) -> None:
        self._run_text("tool_output_text", text, self.tool_output_text, tracer=tracer)

    def _run_text(
        self,
        stage: str,
        text: str,
        rails: Sequence[TextGuardrail],
        *,
        tracer: Tracer | None,
    ) -> None:
        for rail in rails:
            if tracer is not None:
                tracer.emit("guardrail.check", stage=stage, rail=rail.name)
            try:
                rail.check(text)
            except (TripwireTriggered, GuardrailViolation) as e:
                if tracer is not None:
                    tracer.emit("guardrail.blocked", stage=stage, rail=rail.name, error=str(e))
                # Re-raise with the stage the caller cares about (not "text"/"tool").
                if isinstance(e, TripwireTriggered):
                    raise TripwireTriggered(stage=stage, rail=rail.name, reason=e.reason) from e
                raise GuardrailViolation(stage=stage, rail=rail.name, reason=e.reason) from e

