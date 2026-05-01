from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.tools import ToolRegistry


@dataclass(frozen=True, slots=True)
class ToolCallSpec:
    tool: str
    args: dict[str, Any]
    purpose: str = ""


@dataclass(frozen=True, slots=True)
class RewooResult:
    answer: str
    tool_calls: list[ToolCallSpec]
    tool_results: list[str]


PLAN_SCHEMA_HINT = '{ "tool_calls": [{"tool":"<name>","args":{...},"purpose":"..."}] }'


def rewoo(
    model: Model,
    *,
    task: str,
    tools: ToolRegistry,
    tracer: Tracer | None = None,
    max_tool_calls: int = 8,
) -> RewooResult:
    """
    REWOO (Reasoning Without Observation), simplified:
    1) Plan all tool calls up front (no intermediate observations)
    2) Execute tools in batch
    3) Synthesize final answer from tool results
    """
    if max_tool_calls <= 0:
        raise ValueError("max_tool_calls must be > 0")

    tool_list = "\n".join(f"- {t.name}: {t.description}" for t in tools.list()) or "(none)"
    plan = structured_complete(
        model,
        [
            Message(
                role="system",
                content=(
                    "Plan the tool calls you need.\n"
                    "Return ONLY JSON matching the schema."
                ),
            ),
            Message(role="user", content=f"Task:\n{task}\n\nAvailable tools:\n{tool_list}"),
        ],
        parser=lambda v: _parse_plan(v, max_tool_calls=max_tool_calls),
        schema_hint=PLAN_SCHEMA_HINT,
        tracer=tracer,
    )

    if tracer is not None:
        tracer.emit("rewoo.plan", tool_calls=len(plan))

    results: list[str] = []
    for call in plan:
        results.append(tools.call(call.tool, call.args, tracer=tracer))

    answer = model.complete(
        [
            Message(
                role="system",
                content="Write the final answer using the tool results provided.",
            ),
            Message(role="user", content=_synthesis_prompt(task, plan, results)),
        ],
        tracer=tracer,
    )
    return RewooResult(answer=answer, tool_calls=plan, tool_results=results)


def _parse_plan(value: Any, *, max_tool_calls: int) -> list[ToolCallSpec]:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    calls = value.get("tool_calls")
    if not isinstance(calls, list):
        raise SchemaValidationError('"tool_calls" must be a list')

    out: list[ToolCallSpec] = []
    for item in calls:
        if not isinstance(item, dict):
            continue
        tool = item.get("tool")
        args = item.get("args", {})
        purpose = item.get("purpose", "")
        if not isinstance(tool, str) or not tool.strip():
            continue
        if not isinstance(args, dict):
            raise SchemaValidationError('"args" must be an object')
        if not isinstance(purpose, str):
            purpose = str(purpose)
        out.append(ToolCallSpec(tool=tool.strip(), args=dict(args), purpose=purpose))
        if len(out) >= max_tool_calls:
            break

    if not out:
        raise SchemaValidationError("tool_calls must contain at least one call")
    return out


def _synthesis_prompt(task: str, calls: Sequence[ToolCallSpec], results: Sequence[str]) -> str:
    lines: list[str] = [f"Task:\n{task}\n", "Tool results:"]
    for call, res in zip(calls, results, strict=True):
        lines.append(f"- tool={call.tool} purpose={call.purpose}\n  result={res}")
    return "\n".join(lines)

