from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class TraceEvent:
    name: str
    ts: float
    data: dict[str, Any] = field(default_factory=dict)


class Tracer:
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def emit(self, name: str, **data: Any) -> None:
        self.events.append(TraceEvent(name=name, ts=time.time(), data=dict(data)))

    def export_jsonl(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for event in self.events:
                f.write(
                    json.dumps(
                        {"name": event.name, "ts": event.ts, "data": event.data},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return path

