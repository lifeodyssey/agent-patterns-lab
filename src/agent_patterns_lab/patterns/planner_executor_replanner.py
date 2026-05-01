from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from agent_patterns_lab.runtime import (
    Message,
    RunLimits,
    SchemaValidationError,
    Tracer,
    structured_complete,
)
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.runner import run_loop


@dataclass(frozen=True, slots=True)
class PERResult:
    answer: str
    plan: list[str]
    step_outputs: list[str]
    replans: int


PLAN_SCHEMA_HINT = '{ "plan": ["<step 1>", "<step 2>", "..."] }'
DECISION_SCHEMA_HINT = '{ "action":"continue|replan|final", "plan":[...], "answer":"..." }'


def planner_executor_replanner(
    planner: Model,
    executor: Model,
    replanner: Model,
    *,
    task: str,
    limits: RunLimits = RunLimits(max_steps=10),
    tracer: Tracer | None = None,
    max_plan_steps: int = 8,
) -> PERResult:
    """
    Planner-Executor-Replanner:
    - Planner creates a plan
    - Executor executes steps
    - Replanner decides whether to continue, replan, or finish

    This pattern is useful when the environment is dynamic: new evidence or failures may require
    updating the plan mid-run.
    """
    plan = _make_plan(planner, task=task, max_plan_steps=max_plan_steps, tracer=tracer)
    if tracer is not None:
        tracer.emit("per.plan", steps=len(plan))

    state = _PERState(plan=list(plan))
    replans = 0

    def step(step_index: int) -> PERResult | None:
        nonlocal replans

        if not state.plan:
            # No remaining steps; ask replanner for a final answer.
            final = replanner.complete(
                [
                    Message(role="system", content="Provide the final answer given the work so far."),
                    Message(role="user", content=_final_prompt(task, state.completed_steps, state.step_outputs)),
                ],
                tracer=tracer,
            )
            return PERResult(answer=final, plan=state.completed_steps, step_outputs=state.step_outputs, replans=replans)

        current_step = state.plan.pop(0)
        out = executor.complete(
            [
                Message(role="system", content="Execute the next step and return the result."),
                Message(
                    role="user",
                    content=_execute_prompt(task, current_step, state.completed_steps, state.step_outputs),
                ),
            ],
            tracer=tracer,
        )
        state.completed_steps.append(current_step)
        state.step_outputs.append(out)

        if tracer is not None:
            tracer.emit("per.step", step_index=step_index, step=current_step)

        decision = structured_complete(
            replanner,
            [
                Message(
                    role="system",
                    content=(
                        "Decide what to do next given the latest step output.\n"
                        "Return ONLY JSON matching the schema."
                    ),
                ),
                Message(
                    role="user",
                    content=_decide_prompt(task, state.plan, state.completed_steps, state.step_outputs),
                ),
            ],
            parser=_parse_decision,
            schema_hint=DECISION_SCHEMA_HINT,
            tracer=tracer,
        )

        if decision.action == "final":
            return PERResult(
                answer=decision.answer,
                plan=state.completed_steps + state.plan,
                step_outputs=state.step_outputs,
                replans=replans,
            )

        if decision.action == "replan":
            replans += 1
            state.plan = decision.plan
            if tracer is not None:
                tracer.emit("per.replan", replans=replans, steps=len(state.plan))
            return None

        # continue
        return None

    return run_loop(step, limits=limits, tracer=tracer)


@dataclass
class _PERState:
    plan: list[str]
    completed_steps: list[str] = field(default_factory=list)
    step_outputs: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class _Decision:
    action: str
    plan: list[str]
    answer: str


def _make_plan(
    planner: Model,
    *,
    task: str,
    max_plan_steps: int,
    tracer: Tracer | None,
) -> list[str]:
    return structured_complete(
        planner,
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


def _parse_decision(value: Any) -> _Decision:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    action = value.get("action")
    if action not in ("continue", "replan", "final"):
        raise SchemaValidationError('"action" must be "continue", "replan", or "final"')

    plan_val = value.get("plan", [])
    plan: list[str] = []
    if plan_val is None:
        plan_val = []
    if not isinstance(plan_val, list):
        raise SchemaValidationError('"plan" must be a list when provided')
    for s in plan_val:
        if isinstance(s, str) and s.strip():
            plan.append(s.strip())

    answer = value.get("answer", "")
    if not isinstance(answer, str):
        raise SchemaValidationError('"answer" must be a string')

    if action == "replan" and not plan:
        raise SchemaValidationError('replan requires a non-empty "plan"')
    if action == "final" and not answer.strip():
        raise SchemaValidationError('final requires a non-empty "answer"')

    return _Decision(action=action, plan=plan, answer=answer)


def _execute_prompt(task: str, step: str, completed_steps: Sequence[str], outputs: Sequence[str]) -> str:
    done = "\n".join(f"{i+1}. {s}" for i, s in enumerate(completed_steps)) if completed_steps else "(none)"
    out = "\n".join(f"{i+1}. {o}" for i, o in enumerate(outputs)) if outputs else "(none)"
    return f"Task:\n{task}\n\nCompleted steps:\n{done}\n\nOutputs so far:\n{out}\n\nNow execute:\n{step}"


def _decide_prompt(task: str, remaining_plan: Sequence[str], completed_steps: Sequence[str], outputs: Sequence[str]) -> str:
    remaining = "\n".join(f"- {s}" for s in remaining_plan) if remaining_plan else "(none)"
    done = "\n".join(f"- {s}" for s in completed_steps) if completed_steps else "(none)"
    out = "\n".join(f"- {o}" for o in outputs[-3:]) if outputs else "(none)"
    return (
        f"Task:\n{task}\n\nCompleted:\n{done}\n\nRemaining plan:\n{remaining}\n\n"
        f"Recent outputs:\n{out}\n\n"
        "Return JSON decision."
    )


def _final_prompt(task: str, completed_steps: Sequence[str], outputs: Sequence[str]) -> str:
    done = "\n".join(f"- {s}" for s in completed_steps) if completed_steps else "(none)"
    out = "\n".join(f"- {o}" for o in outputs) if outputs else "(none)"
    return f"Task:\n{task}\n\nCompleted steps:\n{done}\n\nOutputs:\n{out}"
