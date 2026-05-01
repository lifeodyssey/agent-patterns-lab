from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SessionNotFound(FileNotFoundError):
    pass


@dataclass(frozen=True, slots=True)
class JsonFileSessionStore:
    root: Path

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, session_id: str, state: dict[str, Any]) -> Path:
        path = self._path(session_id)
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def load(self, session_id: str) -> dict[str, Any]:
        path = self._path(session_id)
        if not path.exists():
            raise SessionNotFound(path)
        raw = path.read_text(encoding="utf-8")
        value = json.loads(raw) if raw.strip() else {}
        if not isinstance(value, dict):
            raise RuntimeError(f"expected JSON object in {path}")
        return value

    def _path(self, session_id: str) -> Path:
        safe = "".join(ch for ch in session_id if ch.isalnum() or ch in ("-", "_"))
        if not safe:
            raise ValueError("invalid session_id")
        return self.root / f"{safe}.json"

