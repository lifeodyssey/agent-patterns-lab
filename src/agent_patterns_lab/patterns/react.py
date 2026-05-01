from __future__ import annotations

from agent_patterns_lab.runtime import Message, RunLimits, Tracer, structured_complete
from agent_patterns_lab.runtime.actions import (
    ACTION_SCHEMA_HINT,
    AskAction,
    FinalAction,
    ToolAction,
    action_to_json,
    parse_action,
)
from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.runner import run_loop
from agent_patterns_lab.runtime.tools import ToolRegistry


class NeedUserInput(RuntimeError):
    def __init__(self, question: str) -> None:
        super().__init__(question)
        self.question = question


def run_react(
    model: Model,
    *,
    task: str,
    tools: ToolRegistry,
    limits: RunLimits = RunLimits(max_steps=10),
    tracer: Tracer | None = None,
) -> str:
    tool_lines = "\n".join(f"- {t.name}: {t.description}" for t in tools.list())
    system = (
        "You are a ReAct-style agent. You may call tools to gather information or perform actions.\n"
        "At each step, return ONLY a JSON action matching the schema.\n\n"
        "Available tools:\n"
        f"{tool_lines or '(none)'}\n\n"
        "Action schema:\n"
        f"{ACTION_SCHEMA_HINT}"
    )
    messages: list[Message] = [
        Message(role="system", content=system),
        Message(role="user", content=task),
    ]

    def step(_step_index: int) -> str | None:
        action = structured_complete(
            model,
            messages,
            parser=parse_action,
            schema_hint=ACTION_SCHEMA_HINT,
            tracer=tracer,
        )

        if tracer is not None:
            tracer.emit("react.action", action_type=action.type)

        if isinstance(action, FinalAction):
            return action.answer

        if isinstance(action, AskAction):
            raise NeedUserInput(action.question)

        # ToolAction
        tool_out = tools.call(action.tool, action.args, tracer=tracer)
        messages.append(Message(role="assistant", content=action_to_json(action)))
        messages.append(Message(role="tool", name=action.tool, content=tool_out))
        return None

    return run_loop(step, limits=limits, tracer=tracer)
