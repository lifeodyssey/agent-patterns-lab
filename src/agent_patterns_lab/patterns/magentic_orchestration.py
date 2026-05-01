from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Literal, Sequence

from agent_patterns_lab.runtime import Message, RunLimits, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.runner import run_loop
from agent_patterns_lab.runtime.structured import SchemaValidationError


@dataclass(frozen=True, slots=True)
class Specialist:
    name: str
    description: str
    model: Model
    system_prompt: str | None = None


@dataclass(frozen=True, slots=True)
class Delegate:
    type: Literal["delegate"]
    agent: str
    task: str


@dataclass(frozen=True, slots=True)
class Final:
    type: Literal["final"]
    answer: str


OrchestrationAction = Delegate | Final


ORCH_SCHEMA_HINT = """{
  "type": "delegate" | "final",
  "agent": "<specialist_name>",   // when type="delegate"
  "task": "<subtask>",            // when type="delegate"
  "answer": "<string>"            // when type="final"
}"""


def parse_orch_action(value: Any, *, valid_agents: set[str]) -> OrchestrationAction:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected JSON object")
    t = value.get("type")
    if t == "final":
        ans = value.get("answer")
        if not isinstance(ans, str) or not ans.strip():
            raise SchemaValidationError('final requires non-empty string "answer"')
        return Final(type="final", answer=ans)
    if t == "delegate":
        agent = value.get("agent")
        task = value.get("task")
        if not isinstance(agent, str) or not agent.strip():
            raise SchemaValidationError('delegate requires non-empty string "agent"')
        if agent not in valid_agents:
            raise SchemaValidationError(f"unknown specialist: {agent}")
        if not isinstance(task, str) or not task.strip():
            raise SchemaValidationError('delegate requires non-empty string "task"')
        return Delegate(type="delegate", agent=agent, task=task)
    raise SchemaValidationError('type must be "delegate" or "final"')


def run_magentic_orchestration(
    orchestrator: Model,
    specialists: Sequence[Specialist],
    *,
    task: str,
    limits: RunLimits = RunLimits(max_steps=8),
    stall_limit: int = 2,
    tracer: Tracer | None = None,
) -> str:
    """
    A small "task ledger + stall detection" orchestrator.

    The orchestrator repeatedly delegates to specialists until it returns a final answer.
    If it repeats the exact same delegation `stall_limit` times in a row, we inject a
    STALL signal into the conversation to encourage replanning.
    """
    if not specialists:
        raise ValueError("specialists must be non-empty")
    if stall_limit <= 0:
        raise ValueError("stall_limit must be > 0")

    by_name = {s.name: s for s in specialists}
    valid = set(by_name.keys())
    roster = "\n".join(f"- {s.name}: {s.description}" for s in specialists)

    system = (
        "You are an orchestrator coordinating specialists.\n"
        "Use the specialists to make progress, then return a final answer.\n"
        "Return ONLY JSON matching the schema.\n\n"
        f"Specialists:\n{roster}\n\nSchema:\n{ORCH_SCHEMA_HINT}"
    )
    messages: list[Message] = [
        Message(role="system", content=system),
        Message(role="user", content=task),
    ]

    last_delegate: tuple[str, str] | None = None
    stall_count = 0

    def step(_step_index: int) -> str | None:
        nonlocal last_delegate, stall_count

        action = structured_complete(
            orchestrator,
            messages,
            parser=lambda v: parse_orch_action(v, valid_agents=valid),
            schema_hint=ORCH_SCHEMA_HINT,
            tracer=tracer,
        )
        if tracer is not None:
            tracer.emit("magentic.action", type=action.type)

        if isinstance(action, Final):
            return action.answer

        delegate_key = (action.agent, action.task)
        if delegate_key == last_delegate:
            stall_count += 1
        else:
            stall_count = 0
        last_delegate = delegate_key

        specialist = by_name[action.agent]
        sys = specialist.system_prompt or f"You are {specialist.name}. {specialist.description}"
        output = specialist.model.complete(
            [
                Message(role="system", content=sys),
                Message(role="user", content=f"Main task: {task}\n\nYour subtask: {action.task}"),
            ],
            tracer=tracer,
        )

        messages.append(Message(role="assistant", content=json.dumps(asdict(action), ensure_ascii=False)))
        messages.append(Message(role="tool", name=specialist.name, content=output))

        if stall_count >= stall_limit:
            stall_count = 0
            messages.append(
                Message(
                    role="user",
                    content="STALL DETECTED: the last delegation was repeated. Change strategy, pick a different specialist/task, or finish.",
                )
            )
            if tracer is not None:
                tracer.emit("magentic.stall_detected", agent=action.agent)

        return None

    return run_loop(step, limits=limits, tracer=tracer)
