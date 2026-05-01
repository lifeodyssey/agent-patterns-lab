from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class SelfDiscoveryResult:
    modules: list[str]
    answer: str


MODULES_SCHEMA_HINT = '{ "modules": ["<module>", "..."] }'


def self_discovery(
    model: Model,
    *,
    task: str,
    available_modules: Sequence[str],
    max_modules: int = 4,
    tracer: Tracer | None = None,
) -> SelfDiscoveryResult:
    """
    Self-Discovery (simplified):
    1) choose reasoning "modules"/strategies
    2) solve the task using the selected modules as guidance
    """
    if not available_modules:
        raise ValueError("available_modules must be non-empty")

    module_list = "\n".join(f"- {m}" for m in available_modules)

    modules = structured_complete(
        model,
        [
            Message(
                role="system",
                content=(
                    "Select the most appropriate reasoning modules.\n"
                    "Return ONLY JSON matching the schema."
                ),
            ),
            Message(
                role="user",
                content=f"Task:\n{task}\n\nAvailable modules:\n{module_list}",
            ),
        ],
        parser=lambda v: _parse_modules(v, allowed=set(available_modules), max_n=max_modules),
        schema_hint=MODULES_SCHEMA_HINT,
        tracer=tracer,
    )

    if tracer is not None:
        tracer.emit("self_discovery.modules", n=len(modules))

    answer = model.complete(
        [
            Message(
                role="system",
                content="Solve the task, following the selected reasoning modules.",
            ),
            Message(role="user", content=_solve_prompt(task, modules)),
        ],
        tracer=tracer,
    )

    return SelfDiscoveryResult(modules=modules, answer=answer)


def _parse_modules(value: Any, *, allowed: set[str], max_n: int) -> list[str]:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    modules = value.get("modules")
    if not isinstance(modules, list):
        raise SchemaValidationError('"modules" must be a list')
    out: list[str] = []
    for m in modules:
        if not isinstance(m, str):
            continue
        m2 = m.strip()
        if not m2:
            continue
        if m2 not in allowed:
            raise SchemaValidationError(f"unknown module: {m2}")
        if m2 not in out:
            out.append(m2)
        if len(out) >= max_n:
            break
    if not out:
        raise SchemaValidationError("modules must contain at least one item")
    return out


def _solve_prompt(task: str, modules: Sequence[str]) -> str:
    lines = "\n".join(f"- {m}" for m in modules)
    return f"Task:\n{task}\n\nSelected modules:\n{lines}\n\nAnswer now."

