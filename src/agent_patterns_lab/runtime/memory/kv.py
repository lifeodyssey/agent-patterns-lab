from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class KeyNotFound(KeyError):
    pass


class InMemoryKV:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        if key not in self._data:
            raise KeyNotFound(key)
        return self._data[key]

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def items(self) -> dict[str, Any]:
        return dict(self._data)


@dataclass
class JsonFileKV:
    path: Path

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def get(self, key: str) -> Any:
        data = self._read()
        if key not in data:
            raise KeyNotFound(key)
        return data[key]

    def set(self, key: str, value: Any) -> None:
        data = self._read()
        data[key] = value
        self._write(data)

    def delete(self, key: str) -> None:
        data = self._read()
        data.pop(key, None)
        self._write(data)

    def items(self) -> dict[str, Any]:
        return self._read()

    def _read(self) -> dict[str, Any]:
        raw = self.path.read_text(encoding="utf-8")
        if not raw.strip():
            return {}
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"invalid JSON in {self.path}") from e
        if not isinstance(value, dict):
            raise RuntimeError(f"expected JSON object in {self.path}")
        return value

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

