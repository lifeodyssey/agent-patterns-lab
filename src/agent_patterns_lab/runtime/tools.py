from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .tracing import Tracer


class ToolNotFoundError(KeyError):
    pass


class ToolExecutionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Tool:
    name: str
    description: str
    handler: Callable[[dict[str, Any]], str]


class ToolRegistry:
    def __init__(self, tools: Sequence[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in tools or ():
            self.register(tool)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as e:
            raise ToolNotFoundError(name) from e

    def list(self) -> list[Tool]:
        return list(self._tools.values())

    def call(
        self,
        name: str,
        args: Mapping[str, Any] | None = None,
        *,
        tracer: Tracer | None = None,
        raise_on_error: bool = False,
    ) -> str:
        tool = self.get(name)
        safe_args = dict(args or {})

        if tracer is not None:
            tracer.emit("tool.call", tool_name=tool.name, args=safe_args)

        try:
            out = tool.handler(safe_args)
        except Exception as e:
            if tracer is not None:
                tracer.emit("tool.error", tool_name=tool.name, error=str(e))
            if raise_on_error:
                raise ToolExecutionError(f"tool {tool.name} failed: {e}") from e
            return f"TOOL_ERROR[{tool.name}]: {e}"

        if tracer is not None:
            tracer.emit("tool.result", tool_name=tool.name, output=out)
        return out

