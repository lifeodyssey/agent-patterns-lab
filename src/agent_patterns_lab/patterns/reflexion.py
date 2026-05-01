from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class VerificationResult:
    ok: bool
    feedback: str


LESSON_SCHEMA_HINT = '{ "lesson": "<string>" }'


def reflexion(
    model: Model,
    *,
    task: str,
    verify: Callable[[str], VerificationResult],
    memory_get: Callable[[str], Any],
    memory_set: Callable[[str, Any], None],
    memory_key: str = "reflexion.lessons",
    rounds: int = 3,
    tracer: Tracer | None = None,
) -> str:
    """
    Reflexion: try -> verify -> (if fail) write lesson to memory -> retry with lessons.

    This simplified variant stores a growing list of lessons under a single memory key.
    """
    if rounds <= 0:
        raise ValueError("rounds must be > 0")

    lessons: list[str] = []
    try:
        existing = memory_get(memory_key)
        if isinstance(existing, list):
            lessons = [str(x) for x in existing if str(x).strip()]
    except Exception:
        lessons = []

    last_answer = ""
    for r in range(rounds):
        prompt = _task_with_lessons(task, lessons)
        last_answer = model.complete(
            [
                Message(role="system", content="Solve the task. Follow any lessons provided."),
                Message(role="user", content=prompt),
            ],
            tracer=tracer,
        )

        v = verify(last_answer)
        if tracer is not None:
            tracer.emit("reflexion.verify", round_index=r, ok=v.ok)
        if v.ok:
            return last_answer

        lesson = structured_complete(
            model,
            [
                Message(
                    role="system",
                    content="Write ONE concise lesson to avoid this failure next time. Return ONLY JSON.",
                ),
                Message(role="user", content=_lesson_prompt(task, last_answer, v.feedback)),
            ],
            parser=_parse_lesson,
            schema_hint=LESSON_SCHEMA_HINT,
            tracer=tracer,
        )

        lessons.append(lesson)
        memory_set(memory_key, lessons)
        if tracer is not None:
            tracer.emit("reflexion.lesson", round_index=r, lesson=lesson)

    return last_answer


def _parse_lesson(value: Any) -> str:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    lesson = value.get("lesson")
    if not isinstance(lesson, str) or not lesson.strip():
        raise SchemaValidationError('"lesson" must be non-empty string')
    return lesson.strip()


def _task_with_lessons(task: str, lessons: Sequence[str]) -> str:
    if not lessons:
        return task
    lines = "\n".join(f"- {l}" for l in lessons)
    return f"Task:\n{task}\n\nLessons:\n{lines}"


def _lesson_prompt(task: str, answer: str, feedback: str) -> str:
    return f"Task:\n{task}\n\nAnswer:\n{answer}\n\nFailure feedback:\n{feedback}"

