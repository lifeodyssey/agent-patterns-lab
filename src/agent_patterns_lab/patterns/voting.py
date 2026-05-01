from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence

from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.tracing import Tracer
from agent_patterns_lab.runtime.types import Message


def majority_vote(items: Sequence[str]) -> str:
    if not items:
        raise ValueError("items must be non-empty")
    counts = Counter(items)
    best_count = max(counts.values())
    for item in items:  # stable tie-breaker: first occurrence
        if counts[item] == best_count:
            return item
    return items[0]


def self_consistency(
    model: Model,
    messages: Sequence[Message],
    *,
    n: int = 5,
    normalize: Callable[[str], str] | None = None,
    tracer: Tracer | None = None,
) -> str:
    """
    Sample the same prompt N times and vote.

    `normalize` can be used to canonicalize answers for voting (e.g., strip whitespace).
    """
    if n <= 0:
        raise ValueError("n must be > 0")

    raw: list[str] = []
    for _ in range(n):
        raw.append(model.complete(messages, tracer=tracer))

    if tracer is not None:
        tracer.emit("voting.sampled", n=n)

    if normalize is None:
        return majority_vote(raw)

    normalized = [normalize(x) for x in raw]
    winner_norm = majority_vote(normalized)
    for r, norm in zip(raw, normalized, strict=True):
        if norm == winner_norm:
            return r
    return raw[0]

