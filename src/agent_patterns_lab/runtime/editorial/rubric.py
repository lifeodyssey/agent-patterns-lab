from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_patterns_lab.runtime.structured import SchemaValidationError


@dataclass(frozen=True, slots=True)
class RubricScores:
    """
    0–5 analytic rubric dimensions.

    These are intentionally *human-facing* (not model benchmark metrics).
    """

    clarity: int
    actionability: int
    boundaries: int
    example_quality: int
    terminology_consistency: int

    def as_dict(self) -> dict[str, int]:
        return {
            "clarity": self.clarity,
            "actionability": self.actionability,
            "boundaries": self.boundaries,
            "example_quality": self.example_quality,
            "terminology_consistency": self.terminology_consistency,
        }

    def overall(self) -> float:
        vals = [
            self.clarity,
            self.actionability,
            self.boundaries,
            self.example_quality,
            self.terminology_consistency,
        ]
        return sum(vals) / len(vals)


@dataclass(frozen=True, slots=True)
class RubricReview:
    scores: RubricScores
    summary: str
    top_fixes: list[str]
    term_notes: list[str]
    style_notes: list[str]


RUBRIC_SCHEMA_HINT = """{
  "scores": {
    "clarity": 0-5,
    "actionability": 0-5,
    "boundaries": 0-5,
    "example_quality": 0-5,
    "terminology_consistency": 0-5
  },
  "summary": "<string>",
  "top_fixes": ["<string>", "..."],
  "term_notes": ["<string>", "..."],
  "style_notes": ["<string>", "..."]
}"""


def parse_rubric_review(value: Any) -> RubricReview:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")

    scores = value.get("scores")
    if not isinstance(scores, dict):
        raise SchemaValidationError('"scores" must be an object')

    clarity = _score(scores, "clarity")
    actionability = _score(scores, "actionability")
    boundaries = _score(scores, "boundaries")
    example_quality = _score(scores, "example_quality")
    terminology_consistency = _score(scores, "terminology_consistency")

    summary = value.get("summary", "")
    if not isinstance(summary, str):
        raise SchemaValidationError('"summary" must be a string')

    top_fixes = _str_list(value.get("top_fixes", []), "top_fixes")
    term_notes = _str_list(value.get("term_notes", []), "term_notes")
    style_notes = _str_list(value.get("style_notes", []), "style_notes")

    return RubricReview(
        scores=RubricScores(
            clarity=clarity,
            actionability=actionability,
            boundaries=boundaries,
            example_quality=example_quality,
            terminology_consistency=terminology_consistency,
        ),
        summary=summary.strip(),
        top_fixes=top_fixes,
        term_notes=term_notes,
        style_notes=style_notes,
    )


def _score(scores: dict[str, Any], key: str) -> int:
    v = scores.get(key)
    if not isinstance(v, int) or isinstance(v, bool):
        raise SchemaValidationError(f'"scores.{key}" must be an integer 0..5')
    if v < 0 or v > 5:
        raise SchemaValidationError(f'"scores.{key}" must be between 0 and 5')
    return v


def _str_list(value: Any, key: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SchemaValidationError(f'"{key}" must be a list of strings')
    out: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise SchemaValidationError(f'"{key}[{idx}]" must be a string')
        s = item.strip()
        if s:
            out.append(s)
    return out


def rubric_definition(locale: str) -> str:
    if locale.lower().startswith("zh"):
        return _RUBRIC_ZH
    return _RUBRIC_EN


_RUBRIC_EN = """Rubric (0–5):
- clarity: Are concepts explained plainly (few assumptions, defined terms, short paragraphs)?
- actionability: Could a reader implement this (steps, pseudo-code, concrete inputs/outputs)?
- boundaries: Is "when to use / when not to use" explicit (failure modes, stop conditions, costs)?
- example_quality: Is there at least one worked example (not just a diagram), minimal but real?
- terminology_consistency: Are terms and pattern names consistent across the page (no accidental synonyms)?

Score guidance:
- 0: unusable / misleading
- 2: partially helpful but missing core pieces
- 3: workable, but gaps exist
- 4: strong, only minor gaps
- 5: excellent, crisp and shippable"""


_RUBRIC_ZH = """Rubric（0–5）：
- 清晰度 clarity：概念是否讲清楚（少预设、术语有定义、段落短、读起来不费劲）？
- 可操作性 actionability：读者是否能照着做（步骤/伪代码/输入输出/可复用骨架）？
- 边界 boundaries：什么时候用/什么时候不用是否明确（失败模式、终止条件、成本/风险）？
- 例子质量 example_quality：至少有 1 个“能跑/能对照”的例子（不只是图），例子足够小但真实？
- 术语一致性 terminology_consistency：术语/模式名是否统一（不要同一概念换不同叫法）？

打分参考：
- 0：不可用/误导
- 2：有帮助但缺核心
- 3：能用但缺口明显
- 4：很强，仅小瑕疵
- 5：可直接发布，表达利落"""

