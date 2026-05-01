from __future__ import annotations

import json
from pathlib import Path

from agent_patterns_lab.patterns.retrieval_loop import retrieval_loop
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

    # 1) propose query  2) decide done+answer
    model = MockLLM(
        [
            '{"query":"Paris capital"}',
            '{"done": true, "answer": "Paris is the capital of France. [paris]"}',
        ]
    )

    result = retrieval_loop(model, question="What is the capital of France?", index=index, rounds=2, tracer=tracer)
    print(result.answer)

    trace_path = tracer.export_jsonl(Path(".traces") / "40_retrieval_loop.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

