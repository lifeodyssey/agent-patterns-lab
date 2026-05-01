from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence


@dataclass(frozen=True, slots=True)
class Document:
    doc_id: str
    text: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SearchResult:
    doc: Document
    score: int


class SimpleSearchIndex:
    """
    A tiny offline retriever for demos/tests.

    Scoring: sum of term frequencies for query terms (case-insensitive, alnum tokens).
    """

    def __init__(self, docs: Sequence[Document]) -> None:
        self._docs = list(docs)
        self._tokens = {d.doc_id: _tokenize(d.text) for d in self._docs}

    def search(self, query: str, *, k: int = 5) -> list[SearchResult]:
        terms = _tokenize(query)
        if not terms:
            return []

        results: list[SearchResult] = []
        for doc in self._docs:
            score = _score(self._tokens[doc.doc_id], terms)
            if score > 0:
                results.append(SearchResult(doc=doc, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]


def _score(doc_tokens: list[str], query_terms: Iterable[str]) -> int:
    total = 0
    for term in query_terms:
        total += sum(1 for t in doc_tokens if t == term)
    return total


def _tokenize(text: str) -> list[str]:
    cleaned = []
    for ch in text.lower():
        cleaned.append(ch if ch.isalnum() else " ")
    return [t for t in "".join(cleaned).split() if t]

