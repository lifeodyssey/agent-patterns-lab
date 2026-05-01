from __future__ import annotations

from pathlib import Path

from agent_patterns_lab.patterns.agents_as_tools import AgentToolSpec, agent_as_tool
from agent_patterns_lab.patterns.react import run_react
from agent_patterns_lab.runtime import MockLLM, RunLimits, ToolRegistry, Tracer


def main() -> None:
    tracer = Tracer()

    math_agent = MockLLM(["42"])
    style_agent = MockLLM(["The answer is 42."])

    tools = ToolRegistry(
        [
            agent_as_tool(
                AgentToolSpec(
                    name="math_agent",
                    description="Specialist agent for arithmetic questions.",
                    model=math_agent,
                    system_prompt="You are a math specialist. Return only the numeric answer.",
                ),
                tracer=tracer,
            ),
            agent_as_tool(
                AgentToolSpec(
                    name="style_agent",
                    description="Specialist agent for writing/formatting.",
                    model=style_agent,
                    system_prompt="You are a writer. Produce a single concise sentence.",
                ),
                tracer=tracer,
            ),
        ]
    )

    controller = MockLLM(
        [
            '{"type":"tool","tool":"math_agent","args":{"task":"Compute 7*6"}}',
            '{"type":"tool","tool":"style_agent","args":{"task":"Write a short sentence using the number 42."}}',
            '{"type":"final","answer":"The answer is 42."}',
        ]
    )

    out = run_react(controller, task="Compute 7*6 and present it nicely.", tools=tools, limits=RunLimits(max_steps=6), tracer=tracer)
    print(out)

    trace_path = tracer.export_jsonl(Path(".traces") / "61_agents_as_tools.jsonl")
    print(f"[trace] {trace_path}")


if __name__ == "__main__":
    main()

