from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping, Sequence

from agent_patterns_lab.runtime import Message, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.structured import SchemaValidationError


@dataclass(frozen=True, slots=True)
class Worker:
    name: str
    description: str
    model: Model
    system_prompt: str | None = None


@dataclass(frozen=True, slots=True)
class Assignment:
    worker: str
    task: str


ASSIGNMENTS_SCHEMA_HINT = """{
  "assignments": [
    { "worker": "<worker_name>", "task": "<subtask>" }
  ]
}"""


def _parse_assignments(value: Any) -> list[Assignment]:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object with assignments")
    raw = value.get("assignments")
    if not isinstance(raw, list) or not raw:
        raise SchemaValidationError('"assignments" must be a non-empty list')
    out: list[Assignment] = []
    for item in raw:
        if not isinstance(item, dict):
            raise SchemaValidationError("assignment must be an object")
        worker = item.get("worker")
        task = item.get("task")
        if not isinstance(worker, str) or not worker.strip():
            raise SchemaValidationError('assignment "worker" must be non-empty string')
        if not isinstance(task, str) or not task.strip():
            raise SchemaValidationError('assignment "task" must be non-empty string')
        out.append(Assignment(worker=worker, task=task))
    return out


def run_manager_worker(
    manager: Model,
    workers: Sequence[Worker],
    *,
    task: str,
    tracer: Tracer | None = None,
) -> str:
    """
    Manager → plan assignments → workers solve subtasks → manager synthesizes final answer.

    Offline-friendly: all models can be MockLLM in tests/examples.
    """
    worker_by_name = {w.name: w for w in workers}
    roster = "\n".join(f"- {w.name}: {w.description}" for w in workers)

    plan_system = (
        "You are a manager agent. Decompose the task into subtasks and assign them to workers.\n"
        "Return ONLY JSON matching the schema.\n\n"
        "Workers:\n"
        f"{roster}\n\n"
        "Schema:\n"
        f"{ASSIGNMENTS_SCHEMA_HINT}"
    )
    plan_messages = [
        Message(role="system", content=plan_system),
        Message(role="user", content=task),
    ]

    assignments = structured_complete(
        manager,
        plan_messages,
        parser=_parse_assignments,
        schema_hint=ASSIGNMENTS_SCHEMA_HINT,
        tracer=tracer,
    )
    if tracer is not None:
        tracer.emit("manager_worker.plan", assignments=[asdict(a) for a in assignments])

    results: list[dict[str, str]] = []
    for a in assignments:
        worker = worker_by_name.get(a.worker)
        if worker is None:
            raise KeyError(f"unknown worker: {a.worker}")

        sys = worker.system_prompt or f"You are worker {worker.name}. {worker.description}"
        msgs = [
            Message(role="system", content=sys),
            Message(role="user", content=f"Main task: {task}\n\nYour subtask: {a.task}"),
        ]
        out = worker.model.complete(msgs, tracer=tracer)
        results.append({"worker": worker.name, "task": a.task, "result": out})
        if tracer is not None:
            tracer.emit("manager_worker.worker_done", worker=worker.name)

    synth_system = (
        "You are the manager. Synthesize a final answer for the user.\n"
        "Use worker results as supporting evidence. Be concise.\n"
        "Return ONLY the final answer text."
    )
    synth_messages = [
        Message(role="system", content=synth_system),
        Message(role="user", content=f"User task:\n{task}\n\nWorker results:\n{json.dumps(results, ensure_ascii=False)}"),
    ]
    final = manager.complete(synth_messages, tracer=tracer)
    if tracer is not None:
        tracer.emit("manager_worker.final")
    return final
