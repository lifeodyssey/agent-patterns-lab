from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class PlanAndSolveResult:
    plan: list[str]
    step_outputs: list[str]
    answer: str


PLAN_SCHEMA_HINT = '{ "plan": ["<step 1>", "<step 2>", "..."] }'


def plan_and_solve(
    model: Model,
    *,
    task: str,
    max_plan_steps: int = 8,
    tracer: Tracer | None = None,
) -> PlanAndSolveResult:
    """
    Plan & Solve:
    1) ask for a step-by-step plan (structured)
    2) execute each step (unstructured)
    3) synthesize a final answer from the step outputs
    """
    if max_plan_steps <= 0:
        raise ValueError("max_plan_steps must be > 0")

    plan = structured_complete(
        model,
        [
            Message(
                role="system",
                content="Write a concise, executable plan. Return ONLY JSON matching the schema.",
            ),
            Message(role="user", content=task),
        ],
        parser=lambda v: _parse_plan(v, max_plan_steps=max_plan_steps),
        schema_hint=PLAN_SCHEMA_HINT,
        tracer=tracer,
    )
    if tracer is not None:
        tracer.emit("plan_and_solve.plan", steps=len(plan))

    step_outputs: list[str] = []
    for i, step in enumerate(plan):
        out = model.complete(
            [
                Message(role="system", content="Execute the next step and return the result."),
                Message(role="user", content=_step_prompt(task, plan, step_outputs, step)),
            ],
            tracer=tracer,
        )
        step_outputs.append(out)
        if tracer is not None:
            tracer.emit("plan_and_solve.step", step_index=i, step=step)

    answer = model.complete(
        [
            Message(role="system", content="Synthesize a final answer using the step outputs."),
            Message(role="user", content=_final_prompt(task, plan, step_outputs)),
        ],
        tracer=tracer,
    )

    if tracer is not None:
        tracer.emit("plan_and_solve.done")

    return PlanAndSolveResult(plan=plan, step_outputs=step_outputs, answer=answer)


def _parse_plan(value: Any, *, max_plan_steps: int) -> list[str]:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    plan = value.get("plan")
    if not isinstance(plan, list):
        raise SchemaValidationError('"plan" must be a list')
    steps: list[str] = []
    for s in plan:
        if isinstance(s, str) and s.strip():
            steps.append(s.strip())
    if not steps:
        raise SchemaValidationError("plan must contain at least one non-empty step")
    return steps[:max_plan_steps]


def _step_prompt(task: str, plan: Sequence[str], outputs: Sequence[str], step: str) -> str:
    done_lines = "\n".join(f"- {o}" for o in outputs) if outputs else "(none)"
    plan_lines = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan))
    return f"Task:\n{task}\n\nPlan:\n{plan_lines}\n\nCompleted step outputs:\n{done_lines}\n\nNow execute:\n{step}"


def _final_prompt(task: str, plan: Sequence[str], outputs: Sequence[str]) -> str:
    plan_lines = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan))
    out_lines = "\n".join(f"{i+1}. {o}" for i, o in enumerate(outputs))
    return f"Task:\n{task}\n\nPlan:\n{plan_lines}\n\nStep outputs:\n{out_lines}\n\nWrite the final answer now."

