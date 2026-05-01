from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class ClaimVerification:
    claim: str
    ok: bool
    evidence: str


CLAIMS_SCHEMA_HINT = '{ "claims": ["<string>", "..."] }'


def chain_of_verification(
    model: Model,
    *,
    question: str,
    verify_claim: Callable[[str], ClaimVerification],
    tracer: Tracer | None = None,
    max_claims: int = 6,
) -> str:
    """
    CoVe (Chain-of-Verification), simplified:

    1) Draft answer
    2) Extract checkable claims
    3) Verify claims via `verify_claim` (tool/rules/human)
    4) Revise answer using verification results
    """
    if max_claims <= 0:
        raise ValueError("max_claims must be > 0")

    draft = model.complete(
        [
            Message(role="system", content="Answer the question as best you can."),
            Message(role="user", content=question),
        ],
        tracer=tracer,
    )

    def parse_claims(value: Any) -> list[str]:
        if not isinstance(value, dict):
            raise SchemaValidationError("expected object")
        claims = value.get("claims")
        if not isinstance(claims, list):
            raise SchemaValidationError('"claims" must be a list')
        out: list[str] = []
        for c in claims:
            if isinstance(c, str) and c.strip():
                out.append(c.strip())
        return out[:max_claims]

    claims = structured_complete(
        model,
        [
            Message(
                role="system",
                content=(
                    "Extract the key factual claims that should be verified.\n"
                    "Return ONLY JSON matching the schema."
                ),
            ),
            Message(role="user", content=f"Question:\n{question}\n\nDraft:\n{draft}"),
        ],
        parser=parse_claims,
        schema_hint=CLAIMS_SCHEMA_HINT,
        tracer=tracer,
    )

    verifications: list[ClaimVerification] = []
    for claim in claims:
        v = verify_claim(claim)
        verifications.append(v)
        if tracer is not None:
            tracer.emit("cove.verified", ok=v.ok, claim=v.claim)

    if not verifications:
        return draft

    revision_input = _format_verifications(verifications)
    revised = model.complete(
        [
            Message(
                role="system",
                content=(
                    "Revise the draft answer using the verification results.\n"
                    "If a claim is unsupported, remove or qualify it."
                ),
            ),
            Message(
                role="user",
                content=f"Question:\n{question}\n\nDraft:\n{draft}\n\nVerification:\n{revision_input}",
            ),
        ],
        tracer=tracer,
    )
    return revised


def _format_verifications(verifications: Sequence[ClaimVerification]) -> str:
    lines: list[str] = []
    for v in verifications:
        status = "OK" if v.ok else "FAIL"
        lines.append(f"- [{status}] {v.claim}\n  evidence: {v.evidence}")
    return "\n".join(lines)

