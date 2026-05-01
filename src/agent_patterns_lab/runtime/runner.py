from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .tracing import Tracer

T = TypeVar("T")


class MaxStepsExceeded(RuntimeError):
    def __init__(self, max_steps: int) -> None:
        super().__init__(f"max_steps exceeded: {max_steps}")
        self.max_steps = max_steps


@dataclass(frozen=True, slots=True)
class RunLimits:
    max_steps: int = 10


def run_loop(
    step_fn: Callable[[int], T | None],
    *,
    limits: RunLimits,
    tracer: Tracer | None = None,
) -> T:
    """
    Generic loop controller.

    `step_fn(step_index)` returns:
    - a value (T) to stop the loop
    - or None to continue
    """
    if limits.max_steps <= 0:
        raise ValueError("limits.max_steps must be > 0")

    for step in range(limits.max_steps):
        if tracer is not None:
            tracer.emit("loop.step", step_index=step)
        out = step_fn(step)
        if out is not None:
            if tracer is not None:
                tracer.emit("loop.done", step_index=step)
            return out

    if tracer is not None:
        tracer.emit("loop.max_steps", max_steps=limits.max_steps)
    raise MaxStepsExceeded(limits.max_steps)

