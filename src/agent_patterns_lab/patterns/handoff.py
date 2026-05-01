from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence

from agent_patterns_lab.runtime import Message, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.structured import SchemaValidationError


@dataclass(frozen=True, slots=True)
class HandoffAgent:
    name: str
    description: str
    model: Model
    system_prompt: str | None = None


@dataclass(frozen=True, slots=True)
class Handle:
    type: Literal["handle"]
    answer: str


@dataclass(frozen=True, slots=True)
class Handoff:
    type: Literal["handoff"]
    to: str
    summary: str


HandoffDecision = Handle | Handoff


HANDOFF_SCHEMA_HINT = """{
  "type": "handle" | "handoff",
  "answer": "<string>",   // when type="handle"
  "to": "<agent_name>",   // when type="handoff"
  "summary": "<string>"   // when type="handoff"
}"""


def _parse_handoff(value: Any, *, valid_agents: set[str]) -> HandoffDecision:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected JSON object")
    t = value.get("type")
    if t == "handle":
        ans = value.get("answer")
        if not isinstance(ans, str) or not ans.strip():
            raise SchemaValidationError('handle requires non-empty string "answer"')
        return Handle(type="handle", answer=ans)
    if t == "handoff":
        to = value.get("to")
        summary = value.get("summary")
        if not isinstance(to, str) or not to.strip():
            raise SchemaValidationError('handoff requires non-empty string "to"')
        if to not in valid_agents:
            raise SchemaValidationError(f"unknown agent: {to}")
        if not isinstance(summary, str) or not summary.strip():
            raise SchemaValidationError('handoff requires non-empty string "summary"')
        return Handoff(type="handoff", to=to, summary=summary)
    raise SchemaValidationError('type must be "handle" or "handoff"')


def run_handoff(
    router: Model,
    agents: Sequence[HandoffAgent],
    *,
    task: str,
    tracer: Tracer | None = None,
) -> str:
    """
    Router decides: handle directly or hand off to a specialized agent.
    """
    if not agents:
        raise ValueError("agents must be non-empty")

    by_name = {a.name: a for a in agents}
    valid = set(by_name.keys())
    roster = "\n".join(f"- {a.name}: {a.description}" for a in agents)

    router_system = (
        "You are a router. Decide whether to answer yourself or hand off to the best agent.\n"
        "Return ONLY JSON.\n\n"
        f"Agents:\n{roster}\n\nSchema:\n{HANDOFF_SCHEMA_HINT}"
    )
    decision = structured_complete(
        router,
        [Message(role="system", content=router_system), Message(role="user", content=task)],
        parser=lambda v: _parse_handoff(v, valid_agents=valid),
        schema_hint=HANDOFF_SCHEMA_HINT,
        tracer=tracer,
    )

    if tracer is not None:
        tracer.emit("handoff.decision", type=decision.type)

    if isinstance(decision, Handle):
        return decision.answer

    target = by_name[decision.to]
    sys = target.system_prompt or f"You are {target.name}. {target.description}"
    messages = [
        Message(role="system", content=sys),
        Message(
            role="user",
            content=(
                "You received a handoff.\n\n"
                f"User task:\n{task}\n\n"
                f"Handoff summary:\n{decision.summary}"
            ),
        ),
    ]
    out = target.model.complete(messages, tracer=tracer)
    if tracer is not None:
        tracer.emit("handoff.completed", to=target.name)
    return out

