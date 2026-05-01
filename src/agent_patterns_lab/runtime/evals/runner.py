from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from agent_patterns_lab.runtime import MockLLM, Tracer

from .report import diff_against_baseline, render_json, render_markdown
from .types import EvalContext, EvalRunResult, EvalSummary, EvalTask, TaskOutcome, TaskStatus


def run_eval_suite(
    tasks: Sequence[EvalTask],
    *,
    out_dir: str | Path = ".evals",
    trace_dir: str | Path = ".traces/evals",
    data_dir: str | Path = "data",
    mode: str = "offline",
    live_model_factory: Callable[[str], Any] | None = None,
    write_markdown: bool = True,
    write_json: bool = True,
    baseline_json: str | Path | None = None,
) -> tuple[EvalSummary, list[TaskOutcome], dict[str, Any]]:
    """
    Run the eval suite and optionally write:
    - a Markdown report
    - a JSON artifact for regression comparisons
    """
    started = time.time()
    out_path = Path(out_dir)
    traces_path = Path(trace_dir)
    corpus_path = Path(data_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    traces_path.mkdir(parents=True, exist_ok=True)

    meta = {
        "mode": mode,
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "cwd": str(Path.cwd()),
    }

    baseline: dict[str, Any] | None = None
    if baseline_json is not None:
        try:
            baseline = json.loads(Path(baseline_json).read_text(encoding="utf-8"))
        except Exception:
            baseline = None

    outcomes: list[TaskOutcome] = []

    for task in tasks:
        task_started = time.time()
        tracer = Tracer()

        make_model = _make_model_factory(task, mode=mode, live_model_factory=live_model_factory)

        work_dir = out_path / "work" / task.task_id
        work_dir.mkdir(parents=True, exist_ok=True)
        ctx = EvalContext(
            task_id=task.task_id,
            category=task.category,
            work_dir=work_dir,
            data_dir=corpus_path,
            trace_dir=traces_path,
            tracer=tracer,
            make_model=make_model,
        )

        status: TaskStatus = "error"
        score_val = 0.0
        reason = ""
        output = ""
        meta_out: dict[str, Any] = {}

        # Requirements (e.g., env vars) -> skip.
        req_missing = _missing_requirements(task.requirements)
        if req_missing:
            status = "skip"
            reason = "missing requirements: " + ", ".join(req_missing)
        else:
            try:
                result = task.run(ctx)
                score = task.score(result)
                status = "pass" if score.passed else "fail"
                score_val = float(score.score)
                reason = score.reason
                output = str(result.output)
                meta_out = dict(result.meta)
            except Exception as e:
                status = "error"
                reason = str(e)

        trace_path: str | None = None
        try:
            trace_file = traces_path / f"{task.task_id}.jsonl"
            tracer.export_jsonl(trace_file)
            trace_path = str(trace_file)
        except Exception:
            trace_path = None

        outcomes.append(
            TaskOutcome(
                task_id=task.task_id,
                category=task.category,
                name=task.name,
                status=status,
                score=score_val,
                reason=reason,
                output=output,
                meta=meta_out,
                trace_path=trace_path,
                duration_s=time.time() - task_started,
            )
        )

    total = len(outcomes)
    passed = sum(1 for o in outcomes if o.status == "pass")
    failed = sum(1 for o in outcomes if o.status == "fail")
    errored = sum(1 for o in outcomes if o.status == "error")
    skipped = sum(1 for o in outcomes if o.status == "skip")
    summary = EvalSummary(
        total=total,
        passed=passed,
        failed=failed,
        errored=errored,
        skipped=skipped,
        duration_s=time.time() - started,
    )

    baseline_diff: str | None = None
    if baseline is not None:
        baseline_diff = diff_against_baseline(baseline=baseline, current_outcomes=outcomes)

    json_obj = render_json(summary=summary, outcomes=outcomes, meta=meta)
    md_text = render_markdown(summary=summary, outcomes=outcomes, meta=meta, baseline_diff=baseline_diff)

    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(summary.generated_at))
    if write_json:
        (out_path / f"eval-results-{timestamp}.json").write_text(json.dumps(json_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    if write_markdown:
        (out_path / f"eval-report-{timestamp}.md").write_text(md_text, encoding="utf-8")

    return summary, outcomes, meta


def _make_model_factory(
    task: EvalTask,
    *,
    mode: str,
    live_model_factory: Callable[[str], Any] | None,
) -> Callable[[str], Any]:
    if mode == "offline":
        if task.offline_scripts is None:
            raise ValueError(f"task {task.task_id} missing offline_scripts")
        scripts = dict(task.offline_scripts)

        def make(role: str):  # type: ignore[no-untyped-def]
            scripted = scripts.get(role)
            if scripted is None:
                raise KeyError(f"offline script missing for role={role} in task={task.task_id}")
            return MockLLM(scripted)

        return make

    if live_model_factory is None:
        raise ValueError("live_model_factory must be provided when mode != offline")
    return live_model_factory


def _missing_requirements(requirements: Sequence[str]) -> list[str]:
    missing: list[str] = []
    for req in requirements:
        if req.startswith("env:"):
            key = req.removeprefix("env:")
            if not os.environ.get(key):
                missing.append(req)
            continue
        # Unknown requirement type: treat as missing.
        if req:
            missing.append(req)
    return missing
