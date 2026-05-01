from __future__ import annotations

import json
from pathlib import Path

from agent_patterns_lab.patterns.storm import storm_write_article
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
    index = SimpleSearchIndex(load_docs(Path("data/mini_corpus.jsonl")))

    model = MockLLM(
        [
            '{"sections":["Agent Loop","RAG"]}',
            '{"query":"agent loop"}',
            "Agent loops iterate decide/act/observe. [agent_loop]",
            '{"query":"RAG retrieval augmented generation"}',
            "RAG grounds answers by retrieving docs. [rag]",
            "Final article:\n## Agent Loop\n...\n## RAG\n...",
        ]
    )

    article = storm_write_article(model, topic="Agent patterns", index=index, tracer=tracer)
    print(article.article)

    trace_path = tracer.export_jsonl(Path(".traces") / "56_storm.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

