# Retrieval (Offline Index for RAG)

## What Problem It Solves

RAG patterns require retrieval. But for learning and regression tests, you usually want retrieval that is:

- offline, deterministic retrieval
- small local corpora

This repo uses a tiny term-frequency index so examples/tests never depend on network or vector DBs.

## How It Works (in This Repo)

- `Document(doc_id, text, meta?)`: a tiny doc container.
- `SimpleSearchIndex(docs)`: builds an alnum tokenizer per doc.
- `search(query, k=5)`: scores by **sum of term frequencies** (case-insensitive).

It’s intentionally primitive. The point is: you can *see* why a doc matched.

## When to Use / When NOT to Use

Use this retriever when:

- you want offline demos/tests for RAG-style patterns
- you want deterministic behavior for eval baselines

Don’t use it for production search:

- no semantic matching (synonyms won’t work)
- no ranking quality guarantees
- no chunking, no embeddings, no freshness logic

## Worked Example

```python
from agent_patterns_lab.runtime import Document, SimpleSearchIndex

docs = [
    Document(doc_id="rag", text="RAG retrieves relevant documents and uses them as context."),
    Document(doc_id="react", text="ReAct alternates reasoning and tool use."),
]

index = SimpleSearchIndex(docs)
hits = index.search("rag context", k=3)

for h in hits:
    print(h.doc.doc_id, h.score)
```

## Failure Modes & Mitigations

- **Query is empty** → return `[]` (this repo does that).
- **Tokenization misses useful signals** → that’s expected; this is a teaching retriever.
- **“Works in tests, fails in reality”** → when you graduate to embeddings, keep the same *interfaces* and re-run the eval harness.

## Repo Reference

- Implementation: [`src/agent_patterns_lab/runtime/retrieval.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/retrieval.py)
- Sample corpus: `data/mini_corpus.jsonl`
- Tests: [`tests/test_retrieval.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_retrieval.py)
