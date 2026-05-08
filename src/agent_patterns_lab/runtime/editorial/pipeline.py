from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from agent_patterns_lab.runtime import Message, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model

from .offline import OfflineHeuristics
from .rubric import RUBRIC_SCHEMA_HINT, RubricReview, parse_rubric_review, rubric_definition


@dataclass(frozen=True, slots=True)
class EditorialStage:
    name: str
    scores: Mapping[str, Any]
    summary: str
    top_fixes: list[str]
    term_notes: list[str]
    style_notes: list[str]


@dataclass(frozen=True, slots=True)
class EditorialResult:
    locale: str
    path: str
    review: EditorialStage
    revise: EditorialStage
    polish: EditorialStage
    final_markdown: str

    def to_json(self) -> dict[str, Any]:
        return {
            "locale": self.locale,
            "path": self.path,
            "review": dict(self.review.scores, summary=self.review.summary, top_fixes=self.review.top_fixes, term_notes=self.review.term_notes, style_notes=self.review.style_notes),
            "revise": dict(self.revise.scores, summary=self.revise.summary, top_fixes=self.revise.top_fixes, term_notes=self.revise.term_notes, style_notes=self.revise.style_notes),
            "polish": dict(self.polish.scores, summary=self.polish.summary, top_fixes=self.polish.top_fixes, term_notes=self.polish.term_notes, style_notes=self.polish.style_notes),
        }


class EditorialPipeline:
    """
    review → revise → polish, with a rubric score for each stage.

    Modes:
    - offline: heuristic-only scoring; content is not rewritten.
    - live: requires a `Model`; performs rewrite + re-score.
    """

    def __init__(
        self,
        *,
        mode: str,
        locale: str,
        writer: Model | None = None,
        reviewer: Model | None = None,
        polisher: Model | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self.mode = mode
        self.locale = locale
        self.writer = writer
        self.reviewer = reviewer
        self.polisher = polisher
        self.tracer = tracer

        if self.mode not in ("offline", "live"):
            raise ValueError('mode must be "offline" or "live"')

        if self.mode == "live" and (writer is None or reviewer is None or polisher is None):
            raise ValueError("live mode requires writer+reviewer+polisher models")

    def run(self, *, path: Path, markdown: str) -> EditorialResult:
        if self.mode == "offline":
            heur = OfflineHeuristics(locale=self.locale)
            r0 = heur.review(markdown)
            r1 = r0
            r2 = r0
            stage0 = _stage("review", r0)
            stage1 = _stage("revise", r1, summary_suffix="(skipped: offline mode)")
            stage2 = _stage("polish", r2, summary_suffix="(skipped: offline mode)")
            return EditorialResult(
                locale=self.locale,
                path=str(path),
                review=stage0,
                revise=stage1,
                polish=stage2,
                final_markdown=markdown,
            )

        # live mode
        assert self.writer is not None
        assert self.reviewer is not None
        assert self.polisher is not None

        review0 = _review(self.reviewer, markdown=markdown, locale=self.locale, tracer=self.tracer)
        revised = _revise(self.writer, markdown=markdown, review=review0, locale=self.locale, tracer=self.tracer)
        review1 = _review(self.reviewer, markdown=revised, locale=self.locale, tracer=self.tracer)
        polished = _polish(self.polisher, markdown=revised, locale=self.locale, tracer=self.tracer)
        review2 = _review(self.reviewer, markdown=polished, locale=self.locale, tracer=self.tracer)

        return EditorialResult(
            locale=self.locale,
            path=str(path),
            review=_stage("review", review0),
            revise=_stage("revise", review1),
            polish=_stage("polish", review2),
            final_markdown=polished,
        )

    def write_outputs(
        self,
        *,
        result: EditorialResult,
        out_dir: Path,
        apply_to_source: bool = False,
    ) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        report_path = out_dir / _safe_report_name(result.path, locale=result.locale)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if apply_to_source:
            Path(result.path).write_text(result.final_markdown, encoding="utf-8")
            return

        mirror_path = out_dir / "out" / result.locale / _relative_from_docs(Path(result.path))
        mirror_path.parent.mkdir(parents=True, exist_ok=True)
        mirror_path.write_text(result.final_markdown, encoding="utf-8")


def render_aggregate_report(results: list[EditorialResult]) -> str:
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    lines: list[str] = []
    lines.append("# Editorial Rubric Report")
    lines.append("")
    lines.append(f"- Generated: {ts}")
    lines.append(f"- Files: {len(results)}")
    lines.append("")
    lines.append("| Locale | Stage | Avg | clarity | action | bounds | examples | terms |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for locale in sorted({r.locale for r in results}):
        subset = [r for r in results if r.locale == locale]
        for stage in ("review", "revise", "polish"):
            avg = _avg_stage(subset, stage)
            lines.append(
                f"| {locale} | {stage} | {avg['overall']:.2f} | {avg['clarity']:.2f} | {avg['actionability']:.2f} | {avg['boundaries']:.2f} | {avg['example_quality']:.2f} | {avg['terminology_consistency']:.2f} |"
            )
    lines.append("")
    lines.append("## Lowest (polish.overall)")
    lines.append("")
    ranked = sorted(results, key=lambda r: float(r.polish.scores.get("overall", 0.0)))
    for r in ranked[:12]:
        lines.append(f"- `{r.path}` ({r.locale}) — {r.polish.scores.get('overall')}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _avg_stage(results: list[EditorialResult], stage: str) -> dict[str, float]:
    key = stage
    totals = {
        "clarity": 0.0,
        "actionability": 0.0,
        "boundaries": 0.0,
        "example_quality": 0.0,
        "terminology_consistency": 0.0,
        "overall": 0.0,
    }
    n = 0
    for r in results:
        st: EditorialStage = getattr(r, key)
        if not st.scores:
            continue
        n += 1
        for k in ("clarity", "actionability", "boundaries", "example_quality", "terminology_consistency"):
            totals[k] += float(st.scores.get(k, 0.0))
        totals["overall"] += float(st.scores.get("overall", 0.0))
    if n == 0:
        return totals
    return {k: v / n for k, v in totals.items()}


def _stage(name: str, review: RubricReview, summary_suffix: str | None = None) -> EditorialStage:
    summary = review.summary
    if summary_suffix:
        summary = (summary + " " + summary_suffix).strip()
    scores = dict(review.scores.as_dict())
    scores["overall"] = review.scores.overall()
    return EditorialStage(
        name=name,
        scores=scores,
        summary=summary,
        top_fixes=list(review.top_fixes),
        term_notes=list(review.term_notes),
        style_notes=list(review.style_notes),
    )


def _review(model: Model, *, markdown: str, locale: str, tracer: Tracer | None) -> RubricReview:
    system = (
        "You are a strict technical editor.\n"
        "Evaluate the markdown and return ONLY JSON matching the schema.\n"
        "Be concrete and actionable; do not be polite.\n\n"
        + rubric_definition(locale)
    )
    user = (
        "Review this page.\n"
        "Return a JSON rubric score + fix list.\n\n"
        "Markdown:\n"
        "-----\n"
        f"{markdown}\n"
        "-----"
    )
    messages = [Message(role="system", content=system), Message(role="user", content=user)]
    return structured_complete(model, messages, parser=parse_rubric_review, schema_hint=RUBRIC_SCHEMA_HINT, tracer=tracer)


def _revise(model: Model, *, markdown: str, review: RubricReview, locale: str, tracer: Tracer | None) -> str:
    system = (
        "You are the writer.\n"
        "Revise the markdown to address the editor feedback.\n"
        "Return ONLY the updated markdown (no commentary, no analysis).\n"
        "Keep existing links and code fences unless you are fixing a bug.\n"
    )
    if locale.lower().startswith("zh"):
        system += "用中文写，少废话，像工程师写的文档。\n"
    else:
        system += "Write in English. Prefer short paragraphs and direct voice.\n"

    fixes = "\n".join(f"- {x}" for x in review.top_fixes) or "- (none)"
    style = "\n".join(f"- {x}" for x in review.style_notes) or "- (none)"
    terms = "\n".join(f"- {x}" for x in review.term_notes) or "- (none)"

    user = (
        "Editor feedback:\n"
        f"{fixes}\n\n"
        "Terminology notes:\n"
        f"{terms}\n\n"
        "Style notes:\n"
        f"{style}\n\n"
        "Original markdown:\n"
        "-----\n"
        f"{markdown}\n"
        "-----\n\n"
        "Return ONLY the revised markdown."
    )
    return model.complete([Message(role="system", content=system), Message(role="user", content=user)], tracer=tracer)


def _polish(model: Model, *, markdown: str, locale: str, tracer: Tracer | None) -> str:
    system = (
        "You are the polisher.\n"
        "Goal: make the markdown feel human-written (less template-y), while keeping technical precision.\n"
        "Mirror the author's voice where it already works; don't flatten it into generic prose.\n"
        "Return ONLY the updated markdown.\n\n"
        "Constraints:\n"
        "- Do NOT add marketing hype.\n"
        "- Cut filler transitions (e.g. 'moreover', 'in conclusion', '值得注意的是').\n"
        "- Vary sentence length; allow occasional short punchy sentences.\n"
        "- Prefer concrete phrasing over vague claims.\n"
        "- Keep headings, links, and code fences intact.\n"
    )
    if locale.lower().startswith("zh"):
        system += (
            "\n中文口吻建议：\n"
            "- 用更口语但不油腻的表达（像同事写的）。\n"
            "- 允许一两句短句强调重点。\n"
            "- 避免“在当今…/综上所述/值得注意的是/不可否认”。\n"
        )
    else:
        system += (
            "\nEnglish voice tips:\n"
            "- Use contractions occasionally.\n"
            "- Avoid 'In today's X', 'It's important to note', 'In conclusion'.\n"
        )

    user = (
        "Polish this markdown.\n"
        "Return ONLY the polished markdown.\n\n"
        "Markdown:\n"
        "-----\n"
        f"{markdown}\n"
        "-----"
    )
    return model.complete([Message(role="system", content=system), Message(role="user", content=user)], tracer=tracer)


def _safe_report_name(path: str, *, locale: str) -> Path:
    p = Path(path)
    # Keep directory structure under docs/ if possible.
    rel = _relative_from_docs(p)
    base = rel.with_suffix(".json")
    return Path("reports") / locale / base


def _relative_from_docs(path: Path) -> Path:
    parts = list(path.parts)
    if "docs" in parts:
        idx = parts.index("docs")
        return Path(*parts[idx + 1 :])
    return Path(path.name)
