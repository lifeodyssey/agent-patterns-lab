from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_patterns_lab.runtime import (
    ACTION_SCHEMA_HINT,
    Message,
    RunLimits,
    SearchResult,
    SimpleSearchIndex,
    Tool,
    ToolRegistry,
    Tracer,
    action_to_json,
    parse_action,
    structured_complete,
)
from agent_patterns_lab.runtime.actions import FinalAction, ToolAction
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.runner import run_loop


@dataclass(frozen=True, slots=True)
class AgenticRagResult:
    answer: str
    evidence: list[SearchResult]


class EvidenceLedger:
    def __init__(self) -> None:
        self._evidence: list[SearchResult] = []
        self._seen: set[str] = set()

    def add(self, results: list[SearchResult]) -> int:
        added = 0
        for r in results:
            doc_id = r.doc.doc_id
            if doc_id in self._seen:
                continue
            self._seen.add(doc_id)
            self._evidence.append(r)
            added += 1
        return added

    def evidence(self) -> list[SearchResult]:
        return list(self._evidence)

    def notes(self, *, max_len: int = 150) -> str:
        lines: list[str] = []
        for r in self._evidence:
            snippet = _snippet(r.doc.text, max_len=max_len)
            lines.append(f"- [{r.doc.doc_id}] (score={r.score}) {snippet}")
        return "\n".join(lines)


def agentic_rag(
    model: Model,
    *,
    question: str,
    index: SimpleSearchIndex,
    limits: RunLimits = RunLimits(max_steps=8),
    tracer: Tracer | None = None,
) -> AgenticRagResult:
    """
    Agentic RAG (RAG agent): dynamic retrieve/read/decide loop, with an evidence ledger.

    This is basically "ReAct + retrieval tool + evidence management + stop conditions".
    """
    ledger = EvidenceLedger()

    def search_tool(args: dict[str, Any]) -> str:
        query = args.get("query")
        k = int(args.get("k", 3))
        if not isinstance(query, str) or not query.strip():
            return "ERROR: missing non-empty 'query'"
        results = index.search(query, k=k)
        added = ledger.add(results)
        if tracer is not None:
            tracer.emit("agentic_rag.search", query=query, hits=len(results), added=added)
        return ledger.notes()

    tools = ToolRegistry(
        [
            Tool(
                name="search",
                description="Search the local corpus. args: {query: string, k?: int}",
                handler=search_tool,
            )
        ]
    )

    system = (
        "You are an agentic RAG system.\n"
        "- Use the `search` tool to gather evidence before answering.\n"
        "- Prefer multiple targeted searches over one vague search.\n"
        "- When answering, cite doc_ids like [doc_id] where relevant.\n"
        "- Return ONLY a JSON action matching the schema.\n\n"
        "Action schema:\n"
        f"{ACTION_SCHEMA_HINT}"
    )
    messages: list[Message] = [
        Message(role="system", content=system),
        Message(role="user", content=question),
    ]

    def step(_i: int) -> AgenticRagResult | None:
        action = structured_complete(
            model,
            messages,
            parser=parse_action,
            schema_hint=ACTION_SCHEMA_HINT,
            tracer=tracer,
        )

        if isinstance(action, FinalAction):
            return AgenticRagResult(answer=action.answer, evidence=ledger.evidence())

        if isinstance(action, ToolAction):
            tool_out = tools.call(action.tool, action.args, tracer=tracer)
            messages.append(Message(role="assistant", content=action_to_json(action)))
            messages.append(Message(role="tool", name=action.tool, content=tool_out))
            return None

        # AskAction: treat as a final answer in this simplified demo.
        return AgenticRagResult(answer=str(getattr(action, "question", "")), evidence=ledger.evidence())

    return run_loop(step, limits=limits, tracer=tracer)


def _snippet(text: str, *, max_len: int) -> str:
    t = " ".join(text.strip().split())
    return t if len(t) <= max_len else t[: max_len - 1] + "…"

