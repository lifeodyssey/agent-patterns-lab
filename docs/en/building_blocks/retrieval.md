# Retrieval (Offline Index for RAG)

## The Problem It Solves

RAG patterns require retrieval. For learning and tests, you want:

- offline, deterministic retrieval
- small local corpora

This repo uses a tiny term-frequency index for demos/tests.

## Repo Reference

- Implementation: `src/agent_patterns_lab/runtime/retrieval.py`
- Sample corpus: `data/mini_corpus.jsonl`
- Tests: `tests/test_retrieval.py`

