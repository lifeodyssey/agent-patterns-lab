from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.tracing import Tracer
from agent_patterns_lab.runtime.types import Message


@dataclass(frozen=True, slots=True)
class PromptStep:
    """
    A single step in a prompt chain.

    `user_prompt` can reference the previous step output via `{input}`.
    """

    name: str
    user_prompt: str
    system_prompt: str | None = None


def run_prompt_chain(
    model: Model,
    *,
    initial_input: str,
    steps: Sequence[PromptStep],
    tracer: Tracer | None = None,
) -> str:
    current = initial_input

    for idx, step in enumerate(steps):
        messages: list[Message] = []
        if step.system_prompt:
            messages.append(Message(role="system", content=step.system_prompt))
        messages.append(Message(role="user", content=step.user_prompt.format(input=current)))

        out = model.complete(messages, tracer=tracer)
        if tracer is not None:
            tracer.emit("workflow.step", index=idx, step_name=step.name, input=current, output=out)

        current = out

    return current
