from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.runtime import (
    BannedRegexTripwire,
    Guardrails,
    HITLController,
    NeedsApproval,
    ParamBound,
    Tool,
    ToolArgsPolicy,
    ToolPolicy,
    ToolRegistry,
    Tracer,
)


def main() -> None:
    tracer = Tracer()

    def deploy(args: dict) -> str:
        return f"DEPLOYED to {args['env']}"

    tools = ToolRegistry([Tool(name="deploy", description="Deploy to an environment", handler=deploy)])

    policy = ToolPolicy(
        allowed_tools={"deploy"},
        per_tool={
            "deploy": ToolArgsPolicy(
                required_keys={"env"},
                bounds={"env": ParamBound(pattern=r"(dev|staging|prod)")},
            )
        },
    )

    guardrails = Guardrails(tool_output_text=[BannedRegexTripwire(patterns=[r"ERROR"])])
    hitl = HITLController(require_approval_for_tools={"deploy"})

    tool_name = "deploy"
    tool_args = {"env": "prod"}

    # Governance stack (simplified):
    policy.check_tool_call(tool_name, tool_args)
    hitl_reason = "prod_deploy_requires_human_approval"

    try:
        hitl.check(tool_name, tool_args, reason=hitl_reason, tracer=tracer)
    except NeedsApproval as e:
        print(f"[hitl] approve? tool={e.request.tool} args={e.request.args} reason={e.request.reason}")
        # Offline simulation: approve and retry.
        hitl.approve(e.request, tracer=tracer)

    out = tools.call(tool_name, tool_args, tracer=tracer)
    guardrails.check_tool_output(out, tracer=tracer)

    print(out)
    trace_path = tracer.export_jsonl(Path(".traces") / "66_governance_hitl_policy_guardrails.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

