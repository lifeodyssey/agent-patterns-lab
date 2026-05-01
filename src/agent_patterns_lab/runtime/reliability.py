from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TypeVar

from .tracing import Tracer

T = TypeVar("T")


class RetryExceeded(RuntimeError):
    pass


def retry(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    backoff_s: float = 0.1,
    sleep: Callable[[float], None] = time.sleep,
    tracer: Tracer | None = None,
) -> T:
    if attempts <= 0:
        raise ValueError("attempts must be > 0")

    last: Exception | None = None
    for attempt in range(attempts):
        try:
            if tracer is not None:
                tracer.emit("retry.attempt", attempt_index=attempt, attempts=attempts)
            return fn()
        except Exception as e:
            last = e
            if tracer is not None:
                tracer.emit("retry.error", attempt_index=attempt, error=str(e))
            if attempt == attempts - 1:
                break
            if backoff_s > 0:
                sleep(backoff_s)

    raise RetryExceeded(str(last) if last else "retry exceeded") from last


class FallbackExhausted(RuntimeError):
    pass


def fallback_chain(
    fns: Sequence[Callable[[], T]],
    *,
    tracer: Tracer | None = None,
) -> T:
    errors: list[str] = []
    for idx, fn in enumerate(fns):
        try:
            if tracer is not None:
                tracer.emit("fallback.try", index=idx)
            return fn()
        except Exception as e:
            errors.append(str(e))
            if tracer is not None:
                tracer.emit("fallback.error", index=idx, error=str(e))
            continue
    raise FallbackExhausted("; ".join(errors))


class CircuitOpenError(RuntimeError):
    pass


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    reset_timeout_s: float = 30.0
    time_fn: Callable[[], float] = time.time

    _failures: int = 0
    _opened_at: float | None = None

    def state(self) -> str:
        if self._opened_at is None:
            return "closed"
        if self.time_fn() - self._opened_at >= self.reset_timeout_s:
            return "half_open"
        return "open"

    def call(self, fn: Callable[[], T], *, tracer: Tracer | None = None) -> T:
        st = self.state()
        if tracer is not None:
            tracer.emit("circuit.state", state=st, failures=self._failures)

        if st == "open":
            raise CircuitOpenError("circuit breaker is open")

        try:
            out = fn()
        except Exception as e:
            self._failures += 1
            if tracer is not None:
                tracer.emit("circuit.error", error=str(e), failures=self._failures)
            if self._failures >= self.failure_threshold:
                self._opened_at = self.time_fn()
                if tracer is not None:
                    tracer.emit("circuit.open", opened_at=self._opened_at)
            raise

        # success
        self._failures = 0
        self._opened_at = None
        if tracer is not None:
            tracer.emit("circuit.close")
        return out

