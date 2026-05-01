from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str
    name: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


class ModelError(RuntimeError):
    pass


class ScriptedResponsesExhausted(ModelError):
    pass

