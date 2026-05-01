from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class LatsResult:
    best: str
    score: float


CANDIDATES_SCHEMA_HINT = '{ "candidates": ["<draft 1>", "<draft 2>", "..."] }'
SCORE_SCHEMA_HINT = '{ "score": <number> }'


def lats_beam_search(
    proposer: Model,
    evaluator: Model,
    *,
    task: str,
    depth: int = 2,
    branch_factor: int = 3,
    beam_size: int = 2,
    tracer: Tracer | None = None,
) -> LatsResult:
    """
    LATS-ish beam search (simplified):
    - Propose multiple candidate drafts (branch_factor)
    - Score each candidate
    - Keep top `beam_size` and iterate `depth` times

    This models the core idea: treat reasoning/solutions as a search space.
    """
    if depth <= 0:
        raise ValueError("depth must be > 0")
    if branch_factor <= 0:
        raise ValueError("branch_factor must be > 0")
    if beam_size <= 0:
        raise ValueError("beam_size must be > 0")

    beam: list[str] = [""]

    best_text = ""
    best_score = float("-inf")

    for d in range(depth):
        expanded: list[str] = []
        for parent in beam:
            candidates = structured_complete(
                proposer,
                [
                    Message(
                        role="system",
                        content="Generate diverse candidate drafts. Return ONLY JSON matching the schema.",
                    ),
                    Message(role="user", content=_expand_prompt(task, parent, branch_factor)),
                ],
                parser=lambda v: _parse_candidates(v, max_n=branch_factor),
                schema_hint=CANDIDATES_SCHEMA_HINT,
                tracer=tracer,
            )
            expanded.extend(candidates)
            if tracer is not None:
                tracer.emit("lats.expand", depth=d, parent_len=len(parent), candidates=len(candidates))

        scored: list[tuple[float, str]] = []
        for cand in expanded:
            score = structured_complete(
                evaluator,
                [
                    Message(
                        role="system",
                        content="Score the candidate from 0.0 to 10.0. Return ONLY JSON.",
                    ),
                    Message(role="user", content=_score_prompt(task, cand)),
                ],
                parser=_parse_score,
                schema_hint=SCORE_SCHEMA_HINT,
                tracer=tracer,
            )
            scored.append((score, cand))
            if tracer is not None:
                tracer.emit("lats.score", depth=d, score=score)

            if score > best_score:
                best_score = score
                best_text = cand

        scored.sort(key=lambda x: x[0], reverse=True)
        beam = [c for _s, c in scored[:beam_size]] or beam

    return LatsResult(best=best_text, score=best_score)


def _parse_candidates(value: Any, *, max_n: int) -> list[str]:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    candidates = value.get("candidates")
    if not isinstance(candidates, list):
        raise SchemaValidationError('"candidates" must be a list')
    out: list[str] = []
    for c in candidates:
        if isinstance(c, str) and c.strip():
            out.append(c.strip())
        if len(out) >= max_n:
            break
    if not out:
        raise SchemaValidationError("candidates must contain at least one non-empty string")
    return out


def _parse_score(value: Any) -> float:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    score = value.get("score")
    if not isinstance(score, (int, float)):
        raise SchemaValidationError('"score" must be a number')
    return float(score)


def _expand_prompt(task: str, parent: str, branch_factor: int) -> str:
    seed = parent.strip() or "(none)"
    return (
        f"Task:\n{task}\n\nCurrent best draft:\n{seed}\n\n"
        f"Generate {branch_factor} improved alternatives.\n"
        "Return JSON: {\"candidates\":[...]}"
    )


def _score_prompt(task: str, candidate: str) -> str:
    return f"Task:\n{task}\n\nCandidate:\n{candidate}\n\nReturn JSON score."

