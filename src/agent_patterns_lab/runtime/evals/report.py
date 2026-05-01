from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Mapping, Sequence

from .types import EvalSummary, TaskOutcome


def render_markdown(
    *,
    summary: EvalSummary,
    outcomes: Sequence[TaskOutcome],
    meta: Mapping[str, Any] | None = None,
    baseline_diff: str | None = None,
) -> str:
    meta = dict(meta or {})
    lines: list[str] = []
    lines.append("# Agent Patterns Lab — Eval Report")
    lines.append("")
    lines.append(f"- Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(summary.generated_at))}")
    lines.append(f"- Duration: {summary.duration_s:.3f}s")
    lines.append(f"- Total: {summary.total}  Passed: {summary.passed}  Failed: {summary.failed}  Error: {summary.errored}  Skipped: {summary.skipped}")
    if meta:
        for k in sorted(meta.keys()):
            lines.append(f"- {k}: {meta[k]}")
    if baseline_diff:
        lines.append("")
        lines.append("## Regression")
        lines.append("")
        lines.append(baseline_diff.strip())

    lines.append("")
    lines.append("## By Category")
    lines.append("")
    lines.extend(_render_by_category(outcomes))

    lines.append("")
    lines.append("## Task Results")
    lines.append("")
    for o in outcomes:
        lines.append(f"### {o.task_id} — {o.name}")
        lines.append("")
        lines.append(f"- Category: {o.category}")
        lines.append(f"- Status: {o.status}  Score: {o.score:.2f}")
        if o.reason:
            lines.append(f"- Reason: {o.reason}")
        if o.trace_path:
            lines.append(f"- Trace: `{o.trace_path}`")
        if o.output:
            lines.append("")
            lines.append("Output (truncated):")
            lines.append("")
            lines.append("```")
            lines.append(_truncate(o.output, 800))
            lines.append("```")
        if o.meta:
            lines.append("")
            lines.append("Meta:")
            lines.append("")
            lines.append("```json")
            lines.append(_truncate(json.dumps(o.meta, ensure_ascii=False, sort_keys=True, indent=2), 800))
            lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_json(
    *,
    summary: EvalSummary,
    outcomes: Sequence[TaskOutcome],
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "meta": dict(meta or {}),
        "summary": asdict(summary),
        "results": [asdict(o) for o in outcomes],
    }


def diff_against_baseline(
    *,
    baseline: Mapping[str, Any],
    current_outcomes: Sequence[TaskOutcome],
) -> str:
    """
    Compute a small, human-friendly regression diff section.

    Baseline format is expected to match `render_json()` output.
    """
    baseline_results = baseline.get("results")
    if not isinstance(baseline_results, list):
        return "- Baseline format invalid; missing `results`."

    base_by_id: dict[str, Mapping[str, Any]] = {}
    for item in baseline_results:
        if isinstance(item, Mapping) and isinstance(item.get("task_id"), str):
            base_by_id[str(item["task_id"])] = item

    changed: list[str] = []
    for o in current_outcomes:
        base = base_by_id.get(o.task_id)
        if base is None:
            changed.append(f"- NEW: `{o.task_id}` status={o.status} score={o.score:.2f}")
            continue
        prev_status = str(base.get("status", ""))
        prev_score = float(base.get("score", 0.0)) if _is_number(base.get("score")) else 0.0
        if prev_status != o.status or abs(prev_score - o.score) > 1e-9:
            changed.append(
                f"- `{o.task_id}`: {prev_status}/{prev_score:.2f} -> {o.status}/{o.score:.2f}"
            )

    if not changed:
        return "- No changes vs baseline."
    return "\n".join(changed)


def _render_by_category(outcomes: Sequence[TaskOutcome]) -> list[str]:
    buckets: dict[str, list[TaskOutcome]] = defaultdict(list)
    for o in outcomes:
        buckets[o.category].append(o)

    lines: list[str] = []
    lines.append("| Category | Total | Pass | Fail | Error | Skip | Pass% |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for cat in sorted(buckets.keys()):
        items = buckets[cat]
        total = len(items)
        passed = sum(1 for x in items if x.status == "pass")
        failed = sum(1 for x in items if x.status == "fail")
        errored = sum(1 for x in items if x.status == "error")
        skipped = sum(1 for x in items if x.status == "skip")
        pct = (passed / total * 100.0) if total else 0.0
        lines.append(f"| {cat} | {total} | {passed} | {failed} | {errored} | {skipped} | {pct:.1f}% |")
    return lines


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

