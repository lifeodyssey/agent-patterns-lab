from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping

from .structured import SchemaValidationError


@dataclass(frozen=True, slots=True)
class FinalAction:
    type: Literal["final"]
    answer: str


@dataclass(frozen=True, slots=True)
class ToolAction:
    type: Literal["tool"]
    tool: str
    args: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class AskAction:
    type: Literal["ask"]
    question: str


Action = FinalAction | ToolAction | AskAction


ACTION_SCHEMA_HINT = """{
  "type": "tool" | "final" | "ask",
  "tool": "<tool_name>",        // when type="tool"
  "args": { "k": "v" },         // when type="tool"
  "answer": "<string>",         // when type="final"
  "question": "<string>"        // when type="ask"
}"""


def parse_action(value: Any) -> Action:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected a JSON object action")

    t = value.get("type")
    if t == "final":
        answer = value.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise SchemaValidationError('final action requires non-empty string "answer"')
        return FinalAction(type="final", answer=answer)

    if t == "ask":
        question = value.get("question")
        if not isinstance(question, str) or not question.strip():
            raise SchemaValidationError('ask action requires non-empty string "question"')
        return AskAction(type="ask", question=question)

    if t == "tool":
        tool = value.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            raise SchemaValidationError('tool action requires non-empty string "tool"')
        args = value.get("args", {})
        if not isinstance(args, dict):
            raise SchemaValidationError('tool action requires object "args"')
        return ToolAction(type="tool", tool=tool, args=args)

    raise SchemaValidationError('action "type" must be one of: tool, final, ask')


def action_to_json(action: Action) -> str:
    """
    Deterministic JSON for traceability and offline tests.
    """
    return json.dumps(asdict(action), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

