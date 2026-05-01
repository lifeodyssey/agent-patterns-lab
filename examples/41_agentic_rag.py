from __future__ import annotations

import json
from pathlib import Path

from agent_patterns_lab.patterns.agentic_rag import agentic_rag
from agent_patterns_lab.runtime import Document, MockLLM, SimpleSearchIndex, Tracer


def load_docs(path: Path) -> list[Document]:
    docs: list[Document] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        docs.append(Document(doc_id=obj["doc_id"], text=obj["text"]))
    return docs


def main() -> None:
    tracer = Tracer()
    docs = load_docs(Path("data/mini_corpus.jsonl"))
    index = SimpleSearchIndex(docs)

    model = MockLLM(
        [
            '{"type":"tool","tool":"search","args":{"query":"capital of France","k":2}}',
            '{"type":"final","answer":"Paris is the capital of France. [paris]"}',
        ]
    )

    result = agentic_rag(model, question="What is the capital of France?", index=index, tracer=tracer)
    print(result.answer)

    trace_path = tracer.export_jsonl(Path(".traces") / "41_agentic_rag.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

