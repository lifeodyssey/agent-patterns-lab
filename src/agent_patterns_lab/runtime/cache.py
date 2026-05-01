from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from .tracing import Tracer

T = TypeVar("T")


class CacheMiss(KeyError):
    pass


@dataclass(frozen=True, slots=True)
class CacheEntry(Generic[T]):
    value: T
    expires_at: float | None = None

    def expired(self, *, now: float) -> bool:
        return self.expires_at is not None and now >= self.expires_at


class InMemoryCache(Generic[T]):
    def __init__(self, *, time_fn: Callable[[], float] = time.time) -> None:
        self._store: dict[str, CacheEntry[T]] = {}
        self._time_fn = time_fn

    def get(self, key: str) -> T:
        now = self._time_fn()
        entry = self._store.get(key)
        if entry is None:
            raise CacheMiss(key)
        if entry.expired(now=now):
            self._store.pop(key, None)
            raise CacheMiss(key)
        return entry.value

    def set(self, key: str, value: T, *, ttl_s: float | None = None) -> None:
        expires_at = None if ttl_s is None else (self._time_fn() + ttl_s)
        self._store[key] = CacheEntry(value=value, expires_at=expires_at)

    def clear(self) -> None:
        self._store.clear()


def cached(
    cache: InMemoryCache[T],
    *,
    key: str,
    compute: Callable[[], T],
    ttl_s: float | None = None,
    tracer: Tracer | None = None,
) -> T:
    try:
        value = cache.get(key)
    except CacheMiss:
        if tracer is not None:
            tracer.emit("cache.miss", key=key)
        value = compute()
        cache.set(key, value, ttl_s=ttl_s)
        if tracer is not None:
            tracer.emit("cache.set", key=key)
        return value

    if tracer is not None:
        tracer.emit("cache.hit", key=key)
    return value

