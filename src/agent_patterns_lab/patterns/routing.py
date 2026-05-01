from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from agent_patterns_lab.runtime.model import Model
from agent_patterns_lab.runtime.structured import SchemaValidationError, structured_complete
from agent_patterns_lab.runtime.tracing import Tracer
from agent_patterns_lab.runtime.types import Message


@dataclass(frozen=True, slots=True)
class Route:
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class Rule:
    route: str
    predicate: Callable[[str], bool]


def rule_route(text: str, *, rules: Sequence[Rule], default: str) -> str:
    for rule in rules:
        if rule.predicate(text):
            return rule.route
    return default


def llm_route(
    model: Model,
    *,
    text: str,
    routes: Sequence[Route],
    tracer: Tracer | None = None,
    max_retries: int = 2,
) -> str:
    allowed = [r.name for r in routes]
    schema_hint = '{ "route": "<one of: ' + ", ".join(allowed) + '>" }'

    system = (
        "You are a router. Choose the best route for the user's input.\n"
        "Return ONLY JSON, matching the schema."
    )
    route_list = "\n".join(
        f"- {r.name}: {r.description or ''}".rstrip() for r in routes
    )
    user = f"Input:\n{text}\n\nRoutes:\n{route_list}\n\nReturn JSON now."

    messages = [Message(role="system", content=system), Message(role="user", content=user)]

    def parse_choice(value: Any) -> str:
        if not isinstance(value, dict):
            raise SchemaValidationError("expected a JSON object")
        route = value.get("route")
        if not isinstance(route, str):
            raise SchemaValidationError('expected key "route" to be a string')
        if route not in allowed:
            raise SchemaValidationError(f'route must be one of: {", ".join(allowed)}')
        return route

    return structured_complete(
        model,
        messages,
        parser=parse_choice,
        schema_hint=schema_hint,
        max_retries=max_retries,
        tracer=tracer,
    )

