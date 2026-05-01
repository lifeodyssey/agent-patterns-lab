from __future__ import annotations

from typing import Protocol, Sequence

from .tracing import Tracer
from .types import Message


class Model(Protocol):
    def complete(self, messages: Sequence[Message], *, tracer: Tracer | None = None) -> str: ...

