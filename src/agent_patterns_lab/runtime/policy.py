from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


class PolicyViolation(RuntimeError):
    def __init__(self, message: str, *, tool: str | None = None) -> None:
        super().__init__(message)
        self.tool = tool


@dataclass(frozen=True, slots=True)
class ParamBound:
    """
    Minimal argument bounds for tool policies.

    This is intentionally small and pragmatic:
    - numeric min/max for ints/floats
    - max_len for strings/sequences
    - regex pattern for strings (fullmatch)
    - allowed values list (exact match)
    """

    minimum: float | None = None
    maximum: float | None = None
    max_len: int | None = None
    pattern: str | None = None
    allowed: Sequence[Any] | None = None

    def check(self, value: Any, *, tool: str, param: str) -> None:
        if self.allowed is not None and value not in self.allowed:
            raise PolicyViolation(
                f"tool {tool} param {param} must be one of {list(self.allowed)}; got {value!r}",
                tool=tool,
            )

        if self.pattern is not None:
            if not isinstance(value, str):
                raise PolicyViolation(
                    f"tool {tool} param {param} must be a string to match /{self.pattern}/; got {type(value).__name__}",
                    tool=tool,
                )
            if re.fullmatch(self.pattern, value) is None:
                raise PolicyViolation(
                    f"tool {tool} param {param} must match /{self.pattern}/; got {value!r}",
                    tool=tool,
                )

        if self.max_len is not None:
            try:
                n = len(value)  # type: ignore[arg-type]
            except Exception as e:
                raise PolicyViolation(
                    f"tool {tool} param {param} must be sized (len) for max_len={self.max_len}; got {type(value).__name__}",
                    tool=tool,
                ) from e
            if n > self.max_len:
                raise PolicyViolation(
                    f"tool {tool} param {param} length must be <= {self.max_len}; got {n}",
                    tool=tool,
                )

        if self.minimum is not None or self.maximum is not None:
            if not isinstance(value, (int, float)):
                raise PolicyViolation(
                    f"tool {tool} param {param} must be numeric for min/max bounds; got {type(value).__name__}",
                    tool=tool,
                )
            if self.minimum is not None and value < self.minimum:
                raise PolicyViolation(
                    f"tool {tool} param {param} must be >= {self.minimum}; got {value}",
                    tool=tool,
                )
            if self.maximum is not None and value > self.maximum:
                raise PolicyViolation(
                    f"tool {tool} param {param} must be <= {self.maximum}; got {value}",
                    tool=tool,
                )


@dataclass(frozen=True, slots=True)
class ToolArgsPolicy:
    required_keys: set[str] = field(default_factory=set)
    allowed_keys: set[str] | None = None
    allow_unknown_keys: bool = True
    bounds: Mapping[str, ParamBound] = field(default_factory=dict)

    def check(self, tool: str, args: Mapping[str, Any]) -> None:
        missing = [k for k in self.required_keys if k not in args]
        if missing:
            raise PolicyViolation(
                f"tool {tool} missing required args: {sorted(missing)}",
                tool=tool,
            )

        if self.allowed_keys is not None and not self.allow_unknown_keys:
            unknown = [k for k in args.keys() if k not in self.allowed_keys]
            if unknown:
                raise PolicyViolation(
                    f"tool {tool} has unknown args not in allowlist: {sorted(unknown)}",
                    tool=tool,
                )

        for key, bound in self.bounds.items():
            if key in args:
                bound.check(args[key], tool=tool, param=key)


@dataclass(frozen=True, slots=True)
class ToolPolicy:
    """
    Tool governance policy:
    - tool allowlist/denylist
    - optional per-tool argument constraints (bounds / required keys)
    """

    allowed_tools: set[str] | None = None
    denied_tools: set[str] = field(default_factory=set)
    per_tool: Mapping[str, ToolArgsPolicy] = field(default_factory=dict)

    def check_tool_call(self, tool: str, args: Mapping[str, Any] | None = None) -> None:
        if self.allowed_tools is not None and tool not in self.allowed_tools:
            raise PolicyViolation(f"tool {tool} not in allowlist", tool=tool)
        if tool in self.denied_tools:
            raise PolicyViolation(f"tool {tool} is denylisted", tool=tool)

        rule = self.per_tool.get(tool)
        if rule is not None:
            safe_args = dict(args or {})
            rule.check(tool, safe_args)

