from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_patterns_lab.runtime import (
    Document,
    Message,
    SchemaValidationError,
    SearchResult,
    SimpleSearchIndex,
    Tracer,
    structured_complete,
)
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class RetrievalLoopResult:
    answer: str
    evidence: list[SearchResult]


QUERY_SCHEMA_HINT = '{ "query": "<string>" }'
DECIDE_SCHEMA_HINT = '{ "done": true|false, "answer": "<string>" }'


def retrieval_loop(
    model: Model,
    *,
    question: str,
    index: SimpleSearchIndex,
    rounds: int = 3,
    top_k: int = 3,
    tracer: Tracer | None = None,
) -> RetrievalLoopResult:
    """
    Retrieval loop: propose query -> retrieve -> read notes -> decide -> repeat.

    This is a workflow-ish pattern (fixed control flow) that still lets the model
    adapt queries based on gaps.
    """
    if rounds <= 0:
        raise ValueError("rounds must be > 0")

    evidence: list[SearchResult] = []
    seen: set[str] = set()
    notes = ""

    for r in range(rounds):
        query = structured_complete(
            model,
            [
                Message(
                    role="system",
                    content="Propose the next retrieval query. Return ONLY JSON.",
                ),
                Message(role="user", content=_query_prompt(question, notes)),
            ],
            parser=_parse_query,
            schema_hint=QUERY_SCHEMA_HINT,
            tracer=tracer,
        )

        results = index.search(query, k=top_k)
        if tracer is not None:
            tracer.emit("retrieval.search", round_index=r, query=query, hits=len(results))

        # Dedup by doc_id.
        for res in results:
            if res.doc.doc_id in seen:
                continue
            seen.add(res.doc.doc_id)
            evidence.append(res)

        notes = _build_notes(evidence)

        decision = structured_complete(
            model,
            [
                Message(
                    role="system",
                    content="Decide if you have enough evidence. Return ONLY JSON.",
                ),
                Message(role="user", content=_decide_prompt(question, notes)),
            ],
            parser=_parse_decision,
            schema_hint=DECIDE_SCHEMA_HINT,
            tracer=tracer,
        )

        if tracer is not None:
            tracer.emit("retrieval.decide", round_index=r, done=decision.done)

        if decision.done:
            return RetrievalLoopResult(answer=decision.answer, evidence=evidence)

    # Not done within rounds: best-effort answer.
    return RetrievalLoopResult(answer=_fallback_answer(model, question, notes, tracer=tracer), evidence=evidence)


@dataclass(frozen=True, slots=True)
class _Decision:
    done: bool
    answer: str


def _parse_query(value: Any) -> str:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    q = value.get("query")
    if not isinstance(q, str) or not q.strip():
        raise SchemaValidationError('"query" must be non-empty string')
    return q.strip()


def _parse_decision(value: Any) -> _Decision:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    done = value.get("done")
    answer = value.get("answer", "")
    if not isinstance(done, bool):
        raise SchemaValidationError('"done" must be boolean')
    if not isinstance(answer, str):
        raise SchemaValidationError('"answer" must be string')
    return _Decision(done=done, answer=answer)


def _query_prompt(question: str, notes: str) -> str:
    return f"Question:\n{question}\n\nCurrent notes:\n{notes}\n\nReturn JSON with query."


def _decide_prompt(question: str, notes: str) -> str:
    return (
        f"Question:\n{question}\n\nEvidence notes:\n{notes}\n\n"
        'Return JSON: {"done": true|false, "answer": "<string>"}.\n'
        'If done=false, set answer="" (or a partial answer).'
    )


def _build_notes(evidence: list[SearchResult]) -> str:
    lines: list[str] = []
    for res in evidence:
        snippet = _snippet(res.doc.text)
        lines.append(f"- ({res.doc.doc_id}, score={res.score}) {snippet}")
    return "\n".join(lines)


def _snippet(text: str, *, max_len: int = 160) -> str:
    t = " ".join(text.strip().split())
    return t if len(t) <= max_len else t[: max_len - 1] + "…"


def _fallback_answer(model: Model, question: str, notes: str, *, tracer: Tracer | None) -> str:
    return model.complete(
        [
            Message(role="system", content="Answer using the provided evidence notes."),
            Message(role="user", content=f"Question:\n{question}\n\nNotes:\n{notes}"),
        ],
        tracer=tracer,
    )

