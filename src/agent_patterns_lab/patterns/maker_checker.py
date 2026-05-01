from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class CheckResult:
    passed: bool
    feedback: str


CHECK_SCHEMA_HINT = '{ "passed": true|false, "feedback": "<string>" }'


def maker_checker(
    maker: Model,
    checker: Model,
    *,
    task: str,
    max_rounds: int = 2,
    tracer: Tracer | None = None,
) -> str:
    """
    Evaluator-Optimizer / Maker-Checker loop.

    1) maker drafts
    2) checker returns {passed, feedback}
    3) if not passed -> maker revises using feedback (repeat)
    """
    if max_rounds <= 0:
        raise ValueError("max_rounds must be > 0")

    draft: str | None = None
    for round_idx in range(max_rounds):
        maker_messages = [
            Message(role="system", content="You are the maker. Produce the best possible draft."),
            Message(role="user", content=task if draft is None else _revise_prompt(task, draft)),
        ]
        draft = maker.complete(maker_messages, tracer=tracer)

        check_messages = [
            Message(
                role="system",
                content=(
                    "You are the checker. Evaluate the draft strictly.\n"
                    "Return ONLY JSON matching the schema."
                ),
            ),
            Message(role="user", content=_check_prompt(task, draft)),
        ]
        result = structured_complete(
            checker,
            check_messages,
            parser=_parse_check,
            schema_hint=CHECK_SCHEMA_HINT,
            tracer=tracer,
        )

        if tracer is not None:
            tracer.emit(
                "maker_checker.check",
                round_index=round_idx,
                passed=result.passed,
            )

        if result.passed:
            return draft

    # If all rounds failed, return the last draft (common in practice).
    return draft or ""


def _parse_check(value: Any) -> CheckResult:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    passed = value.get("passed")
    feedback = value.get("feedback", "")
    if not isinstance(passed, bool):
        raise SchemaValidationError('"passed" must be boolean')
    if not isinstance(feedback, str):
        raise SchemaValidationError('"feedback" must be string')
    return CheckResult(passed=passed, feedback=feedback)


def _check_prompt(task: str, draft: str) -> str:
    return f"Task:\n{task}\n\nDraft:\n{draft}\n\nReturn JSON with passed+feedback."


def _revise_prompt(task: str, draft: str) -> str:
    return (
        f"Task:\n{task}\n\n"
        "Revise and improve the following draft.\n"
        f"Draft:\n{draft}\n"
    )

