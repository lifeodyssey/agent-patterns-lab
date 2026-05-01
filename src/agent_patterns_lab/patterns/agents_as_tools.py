from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from agent_patterns_lab.runtime import Message, Tool, Tracer
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class AgentToolSpec:
    name: str
    description: str
    model: Model
    system_prompt: str
    input_key: str = "task"


def agent_as_tool(spec: AgentToolSpec, *, tracer: Tracer | None = None) -> Tool:
    """
    Wrap a specialized agent as a Tool.

    The returned tool handler expects JSON args like:
      { "<input_key>": "<string>" }
    """

    def handler(args: dict[str, Any]) -> str:
        raw = args.get(spec.input_key)
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f'expected non-empty string arg "{spec.input_key}"')
        messages = [
            Message(role="system", content=spec.system_prompt),
            Message(role="user", content=raw),
        ]
        return spec.model.complete(messages, tracer=tracer)

    return Tool(name=spec.name, description=spec.description, handler=handler)


def agent_tool_result(name: str, output: str) -> str:
    """
    Small helper to make agent-tool outputs easier to read in demos.
    """
    return f"[{name}] {output}"

