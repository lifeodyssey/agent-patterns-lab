from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agent_patterns_lab.runtime import (
    Message,
    SchemaValidationError,
    SearchResult,
    SimpleSearchIndex,
    Tracer,
    structured_complete,
)
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class StormSection:
    title: str
    content: str
    evidence: list[SearchResult]


@dataclass(frozen=True, slots=True)
class StormArticle:
    topic: str
    sections: list[StormSection]
    article: str


OUTLINE_SCHEMA_HINT = '{ "sections": ["<title>", "..."] }'
QUERY_SCHEMA_HINT = '{ "query": "<string>" }'


def storm_write_article(
    model: Model,
    *,
    topic: str,
    index: SimpleSearchIndex,
    sections_rounds: int = 1,
    top_k: int = 3,
    tracer: Tracer | None = None,
    max_sections: int = 6,
) -> StormArticle:
    """
    STORM-like research writing (mini, offline-friendly):

    1) Outline sections
    2) For each section:
       - generate a targeted query (can repeat `sections_rounds` times)
       - retrieve evidence
       - write the section using evidence snippets + doc_id citations
    3) Assemble final article
    """
    if sections_rounds <= 0:
        raise ValueError("sections_rounds must be > 0")
    if max_sections <= 0:
        raise ValueError("max_sections must be > 0")

    outline = structured_complete(
        model,
        [
            Message(
                role="system",
                content="Create a short outline. Return ONLY JSON matching the schema.",
            ),
            Message(role="user", content=f"Topic:\n{topic}"),
        ],
        parser=lambda v: _parse_outline(v, max_sections=max_sections),
        schema_hint=OUTLINE_SCHEMA_HINT,
        tracer=tracer,
    )
    if tracer is not None:
        tracer.emit("storm.outline", sections=len(outline))

    sections: list[StormSection] = []
    for title in outline:
        evidence: list[SearchResult] = []
        seen: set[str] = set()
        notes = ""

        for r in range(sections_rounds):
            query = structured_complete(
                model,
                [
                    Message(
                        role="system",
                        content="Generate a focused search query for this section. Return ONLY JSON.",
                    ),
                    Message(role="user", content=_query_prompt(topic, title, notes)),
                ],
                parser=_parse_query,
                schema_hint=QUERY_SCHEMA_HINT,
                tracer=tracer,
            )

            results = index.search(query, k=top_k)
            added = 0
            for res in results:
                if res.doc.doc_id in seen:
                    continue
                seen.add(res.doc.doc_id)
                evidence.append(res)
                added += 1
            notes = _notes(evidence)

            if tracer is not None:
                tracer.emit("storm.search", section=title, round_index=r, query=query, hits=len(results), added=added)

        content = model.complete(
            [
                Message(
                    role="system",
                    content=(
                        "Write this section using the evidence notes.\n"
                        "Cite sources with [doc_id] where relevant."
                    ),
                ),
                Message(role="user", content=_write_prompt(topic, title, notes)),
            ],
            tracer=tracer,
        )
        sections.append(StormSection(title=title, content=content, evidence=evidence))

        if tracer is not None:
            tracer.emit("storm.section", section=title, evidence=len(evidence))

    article = model.complete(
        [
            Message(
                role="system",
                content="Assemble the final article from the drafted sections.",
            ),
            Message(role="user", content=_assemble_prompt(topic, sections)),
        ],
        tracer=tracer,
    )

    if tracer is not None:
        tracer.emit("storm.done")
    return StormArticle(topic=topic, sections=sections, article=article)


def _parse_outline(value: Any, *, max_sections: int) -> list[str]:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    sections = value.get("sections")
    if not isinstance(sections, list):
        raise SchemaValidationError('"sections" must be a list')
    out: list[str] = []
    for s in sections:
        if isinstance(s, str) and s.strip():
            out.append(s.strip())
        if len(out) >= max_sections:
            break
    if not out:
        raise SchemaValidationError("sections must contain at least one item")
    return out


def _parse_query(value: Any) -> str:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    q = value.get("query")
    if not isinstance(q, str) or not q.strip():
        raise SchemaValidationError('"query" must be non-empty string')
    return q.strip()


def _query_prompt(topic: str, section: str, notes: str) -> str:
    return f"Topic:\n{topic}\n\nSection:\n{section}\n\nCurrent notes:\n{notes}\n\nReturn JSON query."


def _write_prompt(topic: str, section: str, notes: str) -> str:
    return f"Topic:\n{topic}\n\nSection:\n{section}\n\nEvidence notes:\n{notes}\n\nWrite the section now."


def _notes(evidence: Sequence[SearchResult]) -> str:
    lines: list[str] = []
    for r in evidence:
        snippet = _snippet(r.doc.text)
        lines.append(f"- [{r.doc.doc_id}] {snippet}")
    return "\n".join(lines)


def _snippet(text: str, *, max_len: int = 180) -> str:
    t = " ".join(text.strip().split())
    return t if len(t) <= max_len else t[: max_len - 1] + "…"


def _assemble_prompt(topic: str, sections: Sequence[StormSection]) -> str:
    blocks: list[str] = [f"Topic: {topic}", ""]
    for s in sections:
        blocks.append(f"## {s.title}\n{s.content}")
    return "\n\n".join(blocks)

