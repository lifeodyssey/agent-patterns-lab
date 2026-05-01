from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .tracing import Tracer


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    """
    Minimal human-in-the-loop approval request.

    `id` is stable for the same (tool, args) so a caller can approve once and resume.
    """

    id: str
    tool: str
    args: dict[str, Any]
    reason: str


class NeedsApproval(RuntimeError):
    def __init__(self, request: ApprovalRequest) -> None:
        super().__init__(f"needs approval: {request.tool} ({request.id})")
        self.request = request


class ApprovalDenied(RuntimeError):
    def __init__(self, request: ApprovalRequest) -> None:
        super().__init__(f"approval denied: {request.tool} ({request.id})")
        self.request = request


class ScriptedApprovalsExhausted(RuntimeError):
    pass


@dataclass
class ScriptedApprover:
    """
    Deterministic approver for offline demos/tests.

    Each approval request consumes one decision from `decisions`.
    """

    decisions: Sequence[bool]
    _idx: int = 0

    def decide(self, request: ApprovalRequest) -> bool:
        _ = request
        if self._idx >= len(self.decisions):
            raise ScriptedApprovalsExhausted("ScriptedApprover decisions exhausted")
        out = bool(self.decisions[self._idx])
        self._idx += 1
        return out


@dataclass
class HITLController:
    """
    An interrupt/resume friendly approval gate.

    Usage pattern:
    - call `check()` before executing a risky tool
    - if it raises `NeedsApproval`, present `request` to a human
    - call `approve(request)` (or `deny(request)`) then retry the same tool call
    """

    require_approval_for_tools: set[str] = field(default_factory=set)
    approved: set[str] = field(default_factory=set)
    denied: set[str] = field(default_factory=set)

    def check(
        self,
        tool: str,
        args: Mapping[str, Any] | None = None,
        *,
        reason: str = "high_risk_tool",
        tracer: Tracer | None = None,
    ) -> None:
        if tool not in self.require_approval_for_tools:
            return

        safe_args = dict(args or {})
        request = self._make_request(tool, safe_args, reason=reason)

        if request.id in self.approved:
            if tracer is not None:
                tracer.emit("hitl.approved_cached", tool=tool, request_id=request.id)
            return

        if request.id in self.denied:
            if tracer is not None:
                tracer.emit("hitl.denied_cached", tool=tool, request_id=request.id)
            raise ApprovalDenied(request)

        if tracer is not None:
            tracer.emit("hitl.needs_approval", tool=tool, request_id=request.id, reason=reason)
        raise NeedsApproval(request)

    def approve(self, request: ApprovalRequest, *, tracer: Tracer | None = None) -> None:
        self.approved.add(request.id)
        self.denied.discard(request.id)
        if tracer is not None:
            tracer.emit("hitl.approve", tool=request.tool, request_id=request.id)

    def deny(self, request: ApprovalRequest, *, tracer: Tracer | None = None) -> None:
        self.denied.add(request.id)
        self.approved.discard(request.id)
        if tracer is not None:
            tracer.emit("hitl.deny", tool=request.tool, request_id=request.id)

    def _make_request(self, tool: str, args: dict[str, Any], *, reason: str) -> ApprovalRequest:
        payload = {"tool": tool, "args": args}
        digest = _stable_digest(payload)
        return ApprovalRequest(id=digest, tool=tool, args=args, reason=reason)


def _stable_digest(payload: Any) -> str:
    """
    Stable digest for JSON-serializable payloads.

    Falls back to `repr(payload)` if JSON encoding fails.
    """
    try:
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    except Exception:
        encoded = repr(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]

