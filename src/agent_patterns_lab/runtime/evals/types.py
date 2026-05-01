from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Mapping, Protocol, Sequence

from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.tracing import Tracer

TaskStatus = Literal["pass", "fail", "error", "skip"]


class ModelFactory(Protocol):
    def __call__(self, role: str) -> Model: ...


@dataclass(frozen=True, slots=True)
class EvalContext:
    """
    Per-task context passed to task runners.
    """

    task_id: str
    category: str
    work_dir: Path
    data_dir: Path
    trace_dir: Path
    tracer: Tracer
    make_model: ModelFactory


@dataclass(frozen=True, slots=True)
class EvalRunResult:
    output: str
    meta: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EvalScore:
    passed: bool
    score: float
    reason: str = ""


@dataclass(frozen=True, slots=True)
class EvalTask:
    task_id: str
    category: str
    name: str
    description: str
    run: Callable[[EvalContext], EvalRunResult]
    score: Callable[[EvalRunResult], EvalScore]
    offline_scripts: Mapping[str, Sequence[Any]] | None = None
    requirements: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class TaskOutcome:
    task_id: str
    category: str
    name: str
    status: TaskStatus
    score: float
    reason: str
    output: str
    meta: dict[str, Any]
    trace_path: str | None
    duration_s: float


@dataclass(frozen=True, slots=True)
class EvalSummary:
    total: int
    passed: int
    failed: int
    errored: int
    skipped: int
    duration_s: float
    generated_at: float = field(default_factory=time.time)

