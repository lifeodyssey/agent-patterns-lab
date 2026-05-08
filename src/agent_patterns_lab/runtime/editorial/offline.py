from __future__ import annotations

import re
from dataclasses import dataclass

from .rubric import RubricReview, RubricScores


@dataclass(frozen=True, slots=True)
class OfflineHeuristics:
    locale: str

    def review(self, markdown: str) -> RubricReview:
        headings = _headings(markdown)
        has_mermaid = "```mermaid" in markdown
        code_stats = _code_fence_stats(markdown)
        has_non_mermaid_code = code_stats["non_mermaid_blocks"] > 0

        has_problem = _has_any_heading(headings, ["What Problem It Solves", "解决的问题"])
        has_when = _has_any_heading(headings, ["When to Use", "什么时候用"])
        has_how = _has_any_heading(headings, ["How It Works", "它是如何运作的"])
        has_fail = _has_any_heading(headings, ["Failure Modes", "常见失败模式", "Failure Modes & Mitigations"])
        has_worked_example = _has_any_heading(
            headings,
            [
                "Worked Example",
                "Example",
                "Examples",
                "一个能对照的例子",
                "示例",
                "例子",
            ],
        )

        fixes: list[str] = []
        term_notes: list[str] = []
        style_notes: list[str] = []

        clarity = 3
        if not has_problem:
            clarity -= 1
            fixes.append("Add a clear “problem it solves / 解决的问题” section.")
        if not has_how:
            clarity -= 1
            fixes.append("Add a “how it works / 核心流程” section with a minimal loop diagram.")
        if _has_long_lines(markdown):
            clarity -= 1
            style_notes.append("Break long paragraphs/lines; mix short and medium sentences.")

        actionability = 2
        if has_non_mermaid_code:
            actionability += 2
        if has_mermaid:
            actionability += 1
        if not has_worked_example:
            fixes.append("Add a “Worked Example / 示例” section (inputs → steps → outputs).")
        if not has_non_mermaid_code:
            fixes.append("Add a small runnable code sketch (not only diagrams).")

        boundaries = 2
        if has_when:
            boundaries += 1
        if has_fail:
            boundaries += 2
        if not has_when:
            fixes.append("Add explicit “when to use / when not to use” boundaries.")
        if not has_fail:
            fixes.append("Add failure modes + mitigations (loops, cost blowups, tool misuse, etc.).")

        example_quality = 1
        if has_worked_example and has_non_mermaid_code:
            example_quality += 4
        elif has_worked_example:
            example_quality += 3
        elif has_non_mermaid_code:
            example_quality += 2
        if has_mermaid:
            example_quality += 1

        terminology_consistency = 3
        ai_phrases = _ai_cliche_hits(markdown, locale=self.locale)
        if ai_phrases:
            terminology_consistency -= 1
            style_notes.append("Remove AI-ish filler phrases: " + ", ".join(ai_phrases[:6]))

        scores = RubricScores(
            clarity=_clamp(clarity),
            actionability=_clamp(actionability),
            boundaries=_clamp(boundaries),
            example_quality=_clamp(example_quality),
            terminology_consistency=_clamp(terminology_consistency),
        )

        summary = "Offline heuristic review (rough). Focus on missing sections + example quality."
        if self.locale.lower().startswith("zh"):
            summary = "离线启发式评分（粗略）：优先补齐关键小节 + 做一个能对照的例子。"

        return RubricReview(
            scores=scores,
            summary=summary,
            top_fixes=_dedupe_keep_order(fixes)[:8],
            term_notes=_dedupe_keep_order(term_notes)[:8],
            style_notes=_dedupe_keep_order(style_notes)[:8],
        )


def _headings(md: str) -> list[str]:
    out: list[str] = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("#"):
            out.append(s.lstrip("#").strip())
    return out


def _has_any_heading(headings: list[str], candidates: list[str]) -> bool:
    hs = [h.lower() for h in headings]
    for c in candidates:
        needle = c.lower()
        for h in hs:
            if needle in h:
                return True
    return False


def _has_long_lines(md: str, *, limit: int = 140) -> bool:
    """
    A lightweight "readability" signal.

    We intentionally ignore:
    - code blocks (often contain long lines)
    - link/reference lines (URLs are long by nature)
    - markdown tables (a single row can be long but still readable when rendered)
    """
    in_block = False
    for line in md.splitlines():
        s = line.rstrip("\n")
        if s.strip().startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            continue
        if s.lstrip().startswith("|"):
            continue
        if "http://" in s or "https://" in s:
            continue
        if len(s) > limit:
            return True
    return False


def _code_fence_stats(md: str) -> dict[str, int]:
    """
    Very small code fence counter.

    We treat ```mermaid as "diagram" (not a worked example).
    Everything else counts as "non-mermaid code" for actionability.
    """
    in_block = False
    fence_lang = ""
    blocks = 0
    mermaid_blocks = 0
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("```"):
            if not in_block:
                in_block = True
                fence_lang = s[3:].strip().lower()
                blocks += 1
                if fence_lang == "mermaid":
                    mermaid_blocks += 1
            else:
                in_block = False
                fence_lang = ""
    return {
        "blocks": blocks,
        "mermaid_blocks": mermaid_blocks,
        "non_mermaid_blocks": max(0, blocks - mermaid_blocks),
    }


_AI_CLICHES_EN = [
    "in today's",
    "in todays",
    "it is important to note",
    "it's important to note",
    "in conclusion",
    "overall,",
    "delve",
    "tapestry",
    "multifaceted",
    "moreover",
    "furthermore",
    "additionally",
]

_AI_CLICHES_ZH = [
    "在当今",
    "值得注意的是",
    "总的来说",
    "综上所述",
    "我们可以看到",
    "此外",
    "同时",
    "从某种意义上讲",
    "不可否认",
]


def _ai_cliche_hits(md: str, *, locale: str) -> list[str]:
    text = md.lower()
    hits: list[str] = []
    phrases = _AI_CLICHES_ZH if locale.lower().startswith("zh") else _AI_CLICHES_EN
    for p in phrases:
        if p.lower() in text:
            hits.append(p)
    return hits


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def _clamp(v: int) -> int:
    return 0 if v < 0 else 5 if v > 5 else v
