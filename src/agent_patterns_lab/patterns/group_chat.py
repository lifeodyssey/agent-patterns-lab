from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Sequence

from agent_patterns_lab.runtime import Message, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.structured import SchemaValidationError


@dataclass(frozen=True, slots=True)
class ChatAgent:
    name: str
    description: str
    model: Model
    system_prompt: str | None = None


@dataclass(frozen=True, slots=True)
class Speak:
    type: Literal["speak"]
    content: str


@dataclass(frozen=True, slots=True)
class Final:
    type: Literal["final"]
    answer: str


ChatTurn = Speak | Final


CHAT_TURN_SCHEMA_HINT = """{
  "type": "speak" | "final",
  "content": "<string>",   // when type="speak"
  "answer": "<string>"     // when type="final"
}"""


def parse_chat_turn(value: Any) -> ChatTurn:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected JSON object")
    t = value.get("type")
    if t == "speak":
        content = value.get("content")
        if not isinstance(content, str) or not content.strip():
            raise SchemaValidationError('speak requires non-empty string "content"')
        return Speak(type="speak", content=content)
    if t == "final":
        answer = value.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise SchemaValidationError('final requires non-empty string "answer"')
        return Final(type="final", answer=answer)
    raise SchemaValidationError('type must be "speak" or "final"')


NEXT_SPEAKER_SCHEMA_HINT = """{ "speaker": "<agent_name>" }"""


def _parse_next_speaker(value: Any, *, valid: set[str]) -> str:
    if not isinstance(value, dict):
        raise SchemaValidationError("expected object")
    speaker = value.get("speaker")
    if not isinstance(speaker, str) or not speaker.strip():
        raise SchemaValidationError('"speaker" must be non-empty string')
    if speaker not in valid:
        raise SchemaValidationError(f"unknown speaker: {speaker}")
    return speaker


def run_group_chat_round_robin(
    agents: Sequence[ChatAgent],
    *,
    task: str,
    max_rounds: int = 3,
    tracer: Tracer | None = None,
) -> str:
    """
    Multi-agent group chat with a fixed round-robin schedule.
    """
    if max_rounds <= 0:
        raise ValueError("max_rounds must be > 0")
    if not agents:
        raise ValueError("agents must be non-empty")

    roster = "\n".join(f"- {a.name}: {a.description}" for a in agents)
    history: list[Message] = [
        Message(
            role="system",
            content=(
                "You are in a group chat with multiple specialist agents.\n"
                "Stay in your role and be helpful. Return ONLY JSON for each turn.\n\n"
                f"Participants:\n{roster}\n\nSchema:\n{CHAT_TURN_SCHEMA_HINT}"
            ),
        ),
        Message(role="user", content=task),
    ]

    for round_index in range(max_rounds):
        for agent in agents:
            sys = agent.system_prompt or f"You are {agent.name}. {agent.description}"
            messages = [Message(role="system", content=sys)] + history
            turn = structured_complete(
                agent.model,
                messages,
                parser=parse_chat_turn,
                schema_hint=CHAT_TURN_SCHEMA_HINT,
                tracer=tracer,
            )
            if tracer is not None:
                tracer.emit("group_chat.turn", mode="round_robin", round=round_index, speaker=agent.name, type=turn.type)

            if isinstance(turn, Final):
                return turn.answer

            history.append(Message(role="assistant", name=agent.name, content=turn.content))

    raise RuntimeError("group chat did not reach final within max_rounds")


def run_group_chat_selector(
    selector: Model,
    agents: Sequence[ChatAgent],
    *,
    task: str,
    max_turns: int = 6,
    tracer: Tracer | None = None,
) -> str:
    """
    Multi-agent group chat where a selector model chooses who speaks next.
    """
    if max_turns <= 0:
        raise ValueError("max_turns must be > 0")
    if not agents:
        raise ValueError("agents must be non-empty")

    valid = {a.name for a in agents}
    agent_by_name = {a.name: a for a in agents}

    roster = "\n".join(f"- {a.name}: {a.description}" for a in agents)
    history: list[Message] = [
        Message(role="system", content=f"Participants:\n{roster}"),
        Message(role="user", content=task),
    ]

    selector_system = (
        "You are a selector that chooses which agent should speak next.\n"
        "Return ONLY JSON.\n\n"
        f"Valid speakers: {sorted(valid)}\n\nSchema:\n{NEXT_SPEAKER_SCHEMA_HINT}"
    )

    for turn_index in range(max_turns):
        speaker = structured_complete(
            selector,
            [Message(role="system", content=selector_system)] + history,
            parser=lambda v: _parse_next_speaker(v, valid=valid),
            schema_hint=NEXT_SPEAKER_SCHEMA_HINT,
            tracer=tracer,
        )
        agent = agent_by_name[speaker]

        sys = agent.system_prompt or f"You are {agent.name}. {agent.description}"
        turn = structured_complete(
            agent.model,
            [Message(role="system", content=sys)] + history,
            parser=parse_chat_turn,
            schema_hint=CHAT_TURN_SCHEMA_HINT,
            tracer=tracer,
        )

        if tracer is not None:
            tracer.emit("group_chat.turn", mode="selector", turn=turn_index, speaker=speaker, type=turn.type)

        if isinstance(turn, Final):
            return turn.answer

        history.append(Message(role="assistant", name=speaker, content=turn.content))

    raise RuntimeError("group chat did not reach final within max_turns")
