from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from agent_patterns_lab.patterns.agentic_rag import agentic_rag
from agent_patterns_lab.patterns.agents_as_tools import AgentToolSpec, agent_as_tool
from agent_patterns_lab.patterns.cove import ClaimVerification, chain_of_verification
from agent_patterns_lab.patterns.group_chat import ChatAgent, run_group_chat_selector
from agent_patterns_lab.patterns.handoff import HandoffAgent, run_handoff
from agent_patterns_lab.patterns.lats import lats_beam_search
from agent_patterns_lab.patterns.llm_compiler import llm_compiler
from agent_patterns_lab.patterns.magentic_orchestration import Specialist, run_magentic_orchestration
from agent_patterns_lab.patterns.maker_checker import maker_checker
from agent_patterns_lab.patterns.manager_worker import Worker, run_manager_worker
from agent_patterns_lab.patterns.plan_and_solve import plan_and_solve
from agent_patterns_lab.patterns.planner_executor_replanner import planner_executor_replanner
from agent_patterns_lab.patterns.react import run_react
from agent_patterns_lab.patterns.reflexion import VerificationResult, reflexion
from agent_patterns_lab.patterns.retrieval_loop import retrieval_loop
from agent_patterns_lab.patterns.routing import Route, llm_route
from agent_patterns_lab.patterns.self_discovery import self_discovery
from agent_patterns_lab.patterns.storm import storm_write_article
from agent_patterns_lab.patterns.voting import self_consistency
from agent_patterns_lab.patterns.workflow_chaining import PromptStep, run_prompt_chain
from agent_patterns_lab.runtime import (
    BannedRegexTripwire,
    CircuitBreaker,
    CircuitOpenError,
    Document,
    Guardrails,
    HITLController,
    InMemoryKV,
    Message,
    NeedsApproval,
    ParamBound,
    RunLimits,
    SchemaValidationError,
    SimpleSearchIndex,
    Tool,
    ToolArgsPolicy,
    ToolPolicy,
    ToolRegistry,
    retry,
    structured_complete,
)
from agent_patterns_lab.runtime.adapters.anthropic_model import AnthropicMessagesModel
from agent_patterns_lab.runtime.adapters.openai_model import OpenAIChatModel

from .types import EvalContext, EvalRunResult, EvalScore, EvalTask


def all_tasks() -> list[EvalTask]:
    """
    Offline-first eval tasks covering the major pattern categories.
    """
    tasks: list[EvalTask] = []

    # 1) Workflow / chaining
    tasks.append(
        EvalTask(
            task_id="wf_prompt_chain",
            category="workflow",
            name="Prompt Chaining",
            description="A 2-step chain where step 2 depends on step 1 output.",
            run=_task_prompt_chain,
            score=score_exact("HELLO WORLD"),
            offline_scripts={"main": ["hello world", "HELLO WORLD"]},
        )
    )

    # 2) Routing (LLM-based)
    tasks.append(
        EvalTask(
            task_id="wf_llm_routing",
            category="workflow",
            name="LLM Routing",
            description="LLM chooses a route from an allowlist.",
            run=_task_llm_routing,
            score=score_exact("math"),
            offline_scripts={"main": ['{"route":"math"}']},
        )
    )

    # 3) Structured output + JSON extraction
    tasks.append(
        EvalTask(
            task_id="structured_json_extraction",
            category="structured",
            name="Structured Output",
            description="Extract JSON from fenced output and validate schema.",
            run=_task_structured_extraction,
            score=score_exact("123"),
            offline_scripts={
                "main": [
                    'Here is JSON:\n```json\n{"value":123}\n```',
                ]
            },
        )
    )

    # 4) Tool calling + agent loop (ReAct)
    tasks.append(
        EvalTask(
            task_id="react_tool_loop",
            category="react",
            name="ReAct Loop",
            description="Tool action then final action with max_steps safety.",
            run=_task_react_tool_loop,
            score=score_exact("4"),
            offline_scripts={
                "main": [
                    '{"type":"tool","tool":"add","args":{"a":2,"b":2}}',
                    '{"type":"final","answer":"4"}',
                ]
            },
        )
    )

    # 5) Reliability primitives (retry + circuit breaker)
    tasks.append(
        EvalTask(
            task_id="reliability_retry_circuit",
            category="reliability",
            name="Retry + Circuit Breaker",
            description="Core cross-cutting reliability mechanisms.",
            run=_task_reliability_primitives,
            score=score_contains_all(['"retry":"ok"', '"circuit":"open"']),
            offline_scripts={},
        )
    )

    # 6) Maker-checker loop
    tasks.append(
        EvalTask(
            task_id="maker_checker_loop",
            category="reliability",
            name="Maker-Checker",
            description="Maker revises after checker feedback until passed.",
            run=_task_maker_checker,
            score=score_exact("5"),
            offline_scripts={
                "maker": ["4", "5"],
                "checker": [
                    '{"passed":false,"feedback":"Need 5"}',
                    '{"passed":true,"feedback":"OK"}',
                ],
            },
        )
    )

    # 7) Voting / self-consistency
    tasks.append(
        EvalTask(
            task_id="voting_self_consistency",
            category="reliability",
            name="Self-Consistency Voting",
            description="Sample N times and majority vote with stable tie-break.",
            run=_task_voting,
            score=score_exact("B"),
            offline_scripts={"main": ["A", "B", "B", "C", "B"]},
        )
    )

    # 8) Chain-of-Verification (CoVe)
    tasks.append(
        EvalTask(
            task_id="cove_chain_of_verification",
            category="reliability",
            name="Chain-of-Verification",
            description="Draft → extract claims → verify → revise.",
            run=_task_cove,
            score=score_contains_all(["Paris"]),
            offline_scripts={
                "main": [
                    "Paris is the capital of France.",
                    '{"claims":["Paris is the capital of France."]}',
                    "Paris is the capital of France. [paris]",
                ]
            },
        )
    )

    # 9) Reflexion + memory
    tasks.append(
        EvalTask(
            task_id="memory_reflexion",
            category="memory",
            name="Reflexion",
            description="Fail → lesson → retry using memory.",
            run=_task_reflexion,
            score=score_exact("5"),
            offline_scripts={
                "main": [
                    "4",
                    '{"lesson":"Double-check arithmetic"}',
                    "5",
                ]
            },
        )
    )

    # 10) Retrieval loop (workflow-ish RAG)
    tasks.append(
        EvalTask(
            task_id="rag_retrieval_loop",
            category="rag",
            name="Retrieval Loop",
            description="Query → retrieve → decide(done) loop with evidence notes.",
            run=_task_retrieval_loop,
            score=score_requires_evidence(doc_id="rag", needle="[rag]"),
            offline_scripts={
                "main": [
                    '{"query":"RAG"}',
                    '{"done":true,"answer":"RAG retrieves documents and uses them as context. [rag]"}',
                ]
            },
        )
    )

    # 11) Agentic RAG (agent loop + ledger)
    tasks.append(
        EvalTask(
            task_id="rag_agentic_rag",
            category="rag",
            name="Agentic RAG",
            description="ReAct-style retrieve/read/decide with evidence ledger.",
            run=_task_agentic_rag,
            score=score_requires_evidence(doc_id="agent_loop", needle="[agent_loop]"),
            offline_scripts={
                "main": [
                    '{"type":"tool","tool":"search","args":{"query":"agent loop","k":3}}',
                    '{"type":"final","answer":"An agent loop is decide -> act -> observe -> update -> repeat. [agent_loop]"}',
                ]
            },
        )
    )

    # 12) Plan & Solve
    tasks.append(
        EvalTask(
            task_id="planning_plan_and_solve",
            category="planning",
            name="Plan & Solve",
            description="Structured plan, execute steps, synthesize final answer.",
            run=_task_plan_and_solve,
            score=score_contains_all(["5"]),
            offline_scripts={
                "main": [
                    '{"plan":["Compute 2+3","State the result"]}',
                    "5",
                    "The result is 5.",
                    "2+3=5.",
                ]
            },
        )
    )

    # 13) Planner-Executor-Replanner (PER)
    tasks.append(
        EvalTask(
            task_id="planning_per",
            category="planning",
            name="Planner-Executor-Replanner",
            description="Separate planner/executor/replanner with structured decisions.",
            run=_task_per,
            score=score_contains_all(["7"]),
            offline_scripts={
                "planner": ['{"plan":["Compute 3+4"]}'],
                "executor": ["7"],
                "replanner": ['{"action":"final","plan":[],"answer":"3+4=7"}'],
            },
        )
    )

    # 14) LLM Compiler (DAG execution)
    tasks.append(
        EvalTask(
            task_id="planning_llm_compiler",
            category="planning",
            name="LLM Compiler",
            description="Compile to DAG, execute nodes, assemble final.",
            run=_task_llm_compiler,
            score=score_exact("2"),
            offline_scripts={
                "main": [
                    '{"tasks":[{"id":"t1","instruction":"Compute 1+1","deps":[]}],"final":{"instruction":"Return t1."}}',
                    "2",
                    "2",
                ]
            },
        )
    )

    # 15) LATS-ish beam search
    tasks.append(
        EvalTask(
            task_id="search_lats",
            category="search",
            name="LATS Beam Search",
            description="Propose candidates and score them via beam search.",
            run=_task_lats,
            score=score_exact("good"),
            offline_scripts={
                "proposer": ['{"candidates":["bad","good"]}'],
                "evaluator": ['{"score":1}', '{"score":9}'],
            },
        )
    )

    # 16) Self-Discovery
    tasks.append(
        EvalTask(
            task_id="planning_self_discovery",
            category="planning",
            name="Self-Discovery",
            description="Choose reasoning modules then solve the task.",
            run=_task_self_discovery,
            score=score_meta_contains("modules", "check"),
            offline_scripts={"main": ['{"modules":["check","simplify"]}', "ok"]},
        )
    )

    # 17) STORM-like research writing
    tasks.append(
        EvalTask(
            task_id="rag_storm",
            category="rag",
            name="STORM Research Writing",
            description="Outline → per-section retrieval → write → assemble.",
            run=_task_storm,
            score=score_contains_all(["[agent_loop]"]),
            offline_scripts={
                "main": [
                    '{"sections":["Definition"]}',
                    '{"query":"agent loop"}',
                    "An agent loop is a control loop. [agent_loop]",
                    "## Definition\nAn agent loop is a control loop. [agent_loop]",
                ]
            },
        )
    )

    # 18) Multi-agent: manager-worker
    tasks.append(
        EvalTask(
            task_id="multi_manager_worker",
            category="multi_agent",
            name="Manager-Worker",
            description="Manager decomposes and synthesizes; workers execute subtasks.",
            run=_task_manager_worker,
            score=score_contains_all(["4"]),
            offline_scripts={
                "manager": [
                    '{"assignments":[{"worker":"math","task":"Compute 2+2"},{"worker":"writer","task":"Explain briefly"}]}',
                    "2+2=4.",
                ],
                "math": ["4"],
                "writer": ["Because 2+2=4."],
            },
        )
    )

    # 19) Multi-agent: agents-as-tools inside ReAct
    tasks.append(
        EvalTask(
            task_id="multi_agents_as_tools",
            category="multi_agent",
            name="Agents-as-Tools",
            description="Wrap sub-agents as tools; primary agent stays in control.",
            run=_task_agents_as_tools,
            score=score_contains_all(["42"]),
            offline_scripts={
                "controller": [
                    '{"type":"tool","tool":"math_agent","args":{"task":"Compute 7*6"}}',
                    '{"type":"tool","tool":"style_agent","args":{"task":"Write a one-sentence answer with 42."}}',
                    '{"type":"final","answer":"The answer is 42."}',
                ],
                "math_agent": ["42"],
                "style_agent": ["The answer is 42."],
            },
        )
    )

    # 20) Multi-agent: group chat (selector)
    tasks.append(
        EvalTask(
            task_id="multi_group_chat_selector",
            category="multi_agent",
            name="Group Chat (Selector)",
            description="Selector picks next speaker; agents speak/finalize.",
            run=_task_group_chat_selector,
            score=score_exact("2+2=4."),
            offline_scripts={
                "selector": ['{"speaker":"researcher"}', '{"speaker":"writer"}'],
                "researcher": ['{"type":"speak","content":"Fact: 2+2=4."}'],
                "writer": ['{"type":"final","answer":"2+2=4."}'],
            },
        )
    )

    # 21) Multi-agent: handoff
    tasks.append(
        EvalTask(
            task_id="multi_handoff",
            category="multi_agent",
            name="Handoff",
            description="Router hands off the task with a summary.",
            run=_task_handoff,
            score=score_exact("10"),
            offline_scripts={"router": ['{"type":"handoff","to":"math","summary":"Compute 9+1."}'], "math": ["10"]},
        )
    )

    # 22) Multi-agent: magentic orchestration
    tasks.append(
        EvalTask(
            task_id="multi_magentic",
            category="multi_agent",
            name="Magentic Orchestration",
            description="Task ledger + stall detection + delegation loop.",
            run=_task_magentic,
            score=score_contains_all(["7"]),
            offline_scripts={
                "orchestrator": [
                    '{"type":"delegate","agent":"calc","task":"Compute 3+4"}',
                    '{"type":"final","answer":"3+4=7."}',
                ],
                "calc": ["7"],
            },
        )
    )

    # 23) Governance: policy + guardrails + HITL
    tasks.append(
        EvalTask(
            task_id="governance_policy_guardrails_hitl",
            category="governance",
            name="Policy + Guardrails + HITL",
            description="Allowlist/bounds + approval gate + output tripwire.",
            run=_task_governance,
            score=score_exact("DEPLOYED to prod"),
            offline_scripts={},
        )
    )

    # 24) Adapters (SDK wrappers) in offline stub mode
    tasks.append(
        EvalTask(
            task_id="adapters_openai_stub",
            category="adapters",
            name="OpenAI Adapter (Stub)",
            description="Adapter can run with a stub client without importing the SDK.",
            run=_task_openai_adapter_stub,
            score=score_exact("ok"),
            offline_scripts={},
        )
    )
    tasks.append(
        EvalTask(
            task_id="adapters_anthropic_stub",
            category="adapters",
            name="Anthropic Adapter (Stub)",
            description="Adapter can run with a stub client without importing the SDK.",
            run=_task_anthropic_adapter_stub,
            score=score_exact("ok"),
            offline_scripts={},
        )
    )

    return tasks


# -------------------------
# Scorers
# -------------------------


def score_exact(expected: str) -> Callable[[EvalRunResult], EvalScore]:
    def scorer(result: EvalRunResult) -> EvalScore:
        ok = result.output == expected
        reason = "" if ok else f"expected {expected!r}, got {result.output!r}"
        return EvalScore(passed=ok, score=1.0 if ok else 0.0, reason=reason)

    return scorer


def score_contains_all(needles: Sequence[str]) -> Callable[[EvalRunResult], EvalScore]:
    def scorer(result: EvalRunResult) -> EvalScore:
        missing = [n for n in needles if n not in result.output]
        ok = not missing
        reason = "" if ok else f"missing substrings: {missing}"
        return EvalScore(passed=ok, score=1.0 if ok else 0.0, reason=reason)

    return scorer


def score_requires_evidence(*, doc_id: str, needle: str) -> Callable[[EvalRunResult], EvalScore]:
    def scorer(result: EvalRunResult) -> EvalScore:
        evidence = list(result.meta.get("evidence_ids", [])) if isinstance(result.meta, Mapping) else []
        ok = (doc_id in evidence) and (needle in result.output)
        reason = "" if ok else f"need evidence {doc_id!r} and output contains {needle!r}; got evidence={evidence}"
        return EvalScore(passed=ok, score=1.0 if ok else 0.0, reason=reason)

    return scorer


def score_meta_contains(key: str, required_item: str) -> Callable[[EvalRunResult], EvalScore]:
    def scorer(result: EvalRunResult) -> EvalScore:
        value = result.meta.get(key)
        ok = isinstance(value, list) and required_item in [str(x) for x in value]
        reason = "" if ok else f"meta[{key!r}] must contain {required_item!r}; got {value!r}"
        return EvalScore(passed=ok, score=1.0 if ok else 0.0, reason=reason)

    return scorer


# -------------------------
# Task implementations
# -------------------------


def _task_prompt_chain(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    out = run_prompt_chain(
        model,
        initial_input="world",
        steps=[
            PromptStep(name="draft", user_prompt="Say hello to {input}"),
            PromptStep(name="shout", user_prompt="Uppercase: {input}"),
        ],
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=out)


def _task_llm_routing(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    route = llm_route(
        model,
        text="Compute 2+2",
        routes=[Route(name="math", description="do arithmetic"), Route(name="chat", description="chit-chat")],
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=route)


def _task_structured_extraction(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")

    def parse(value: Any) -> int:
        if not isinstance(value, dict):
            raise SchemaValidationError("expected object")
        v = value.get("value")
        if not isinstance(v, int):
            raise SchemaValidationError('"value" must be int')
        return v

    v = structured_complete(
        model,
        [
            Message(role="system", content="Return ONLY JSON like {\"value\":123}."),
            Message(role="user", content="Return {\"value\":123}."),
        ],
        parser=parse,
        schema_hint='{"value":123}',
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=str(v))


def _task_react_tool_loop(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")

    def add(args: dict) -> str:
        return str(int(args["a"]) + int(args["b"]))

    tools = ToolRegistry([Tool(name="add", description="Add integers", handler=add)])
    out = run_react(
        model,
        task="Compute 2+2.",
        tools=tools,
        limits=RunLimits(max_steps=5),
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=out)


def _task_reliability_primitives(ctx: EvalContext) -> EvalRunResult:
    _ = ctx
    attempts = {"n": 0}

    def flaky() -> str:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ValueError("boom")
        return "ok"

    retry_out = retry(flaky, attempts=3, backoff_s=0.0, sleep=lambda _s: None)

    breaker = CircuitBreaker(failure_threshold=2, reset_timeout_s=9999.0, time_fn=lambda: 0.0)

    def always_fail() -> str:
        raise ValueError("fail")

    for _i in range(2):
        try:
            breaker.call(always_fail)
        except Exception:
            pass

    circuit_state = breaker.state()
    open_blocked = False
    try:
        breaker.call(lambda: "should_not_run")
    except CircuitOpenError:
        open_blocked = True

    payload = {"retry": retry_out, "circuit": circuit_state, "open_blocked": open_blocked}
    return EvalRunResult(output=json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _task_maker_checker(ctx: EvalContext) -> EvalRunResult:
    maker = ctx.make_model("maker")
    checker = ctx.make_model("checker")
    out = maker_checker(maker, checker, task="Return exactly the number 5.", max_rounds=2, tracer=ctx.tracer)
    return EvalRunResult(output=out)


def _task_voting(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    out = self_consistency(
        model,
        [Message(role="system", content="Answer with A/B/C only."), Message(role="user", content="Pick B.")],
        n=5,
        normalize=lambda s: s.strip().upper(),
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=out.strip().upper())


def _task_cove(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")

    def verify_claim(claim: str) -> ClaimVerification:
        ok = "paris" in claim.lower()
        return ClaimVerification(claim=claim, ok=ok, evidence="matched known fact" if ok else "unsupported")

    out = chain_of_verification(
        model,
        question="What is the capital of France?",
        verify_claim=verify_claim,
        tracer=ctx.tracer,
        max_claims=3,
    )
    return EvalRunResult(output=out)


def _task_reflexion(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    kv = InMemoryKV()

    def verify(answer: str) -> VerificationResult:
        ok = "5" in answer
        return VerificationResult(ok=ok, feedback="must contain 5")

    out = reflexion(
        model,
        task="Compute 2+3 and return only the number.",
        verify=verify,
        memory_get=kv.get,
        memory_set=kv.set,
        rounds=2,
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=out, meta={"lessons": kv.items().get("reflexion.lessons", [])})


def _load_corpus(data_dir: Path) -> SimpleSearchIndex:
    path = data_dir / "mini_corpus.jsonl"
    docs: list[Document] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        docs.append(Document(doc_id=str(obj["doc_id"]), text=str(obj["text"])))
    return SimpleSearchIndex(docs)


def _task_retrieval_loop(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    index = _load_corpus(ctx.data_dir)
    result = retrieval_loop(model, question="What is RAG?", index=index, rounds=1, top_k=3, tracer=ctx.tracer)
    ids = [r.doc.doc_id for r in result.evidence]
    return EvalRunResult(output=result.answer, meta={"evidence_ids": ids})


def _task_agentic_rag(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    index = _load_corpus(ctx.data_dir)
    result = agentic_rag(model, question="What is an agent loop?", index=index, limits=RunLimits(max_steps=4), tracer=ctx.tracer)
    ids = [r.doc.doc_id for r in result.evidence]
    return EvalRunResult(output=result.answer, meta={"evidence_ids": ids})


def _task_plan_and_solve(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    result = plan_and_solve(model, task="Compute 2+3 and explain briefly.", tracer=ctx.tracer, max_plan_steps=4)
    return EvalRunResult(output=result.answer, meta={"plan": list(result.plan)})


def _task_per(ctx: EvalContext) -> EvalRunResult:
    planner = ctx.make_model("planner")
    executor = ctx.make_model("executor")
    replanner = ctx.make_model("replanner")
    result = planner_executor_replanner(
        planner,
        executor,
        replanner,
        task="Compute 3+4 and return the result.",
        limits=RunLimits(max_steps=4),
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=result.answer, meta={"replans": result.replans})


def _task_llm_compiler(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    out = llm_compiler(model, task="Compute 1+1.", tracer=ctx.tracer, max_tasks=3)
    return EvalRunResult(output=out)


def _task_lats(ctx: EvalContext) -> EvalRunResult:
    proposer = ctx.make_model("proposer")
    evaluator = ctx.make_model("evaluator")
    result = lats_beam_search(
        proposer,
        evaluator,
        task="Return the string 'good'.",
        depth=1,
        branch_factor=2,
        beam_size=1,
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=result.best, meta={"score": result.score})


def _task_self_discovery(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    result = self_discovery(
        model,
        task="Return the string ok.",
        available_modules=["check", "simplify", "plan"],
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=result.answer, meta={"modules": list(result.modules)})


def _task_storm(ctx: EvalContext) -> EvalRunResult:
    model = ctx.make_model("main")
    index = _load_corpus(ctx.data_dir)
    article = storm_write_article(
        model,
        topic="Agent loop",
        index=index,
        sections_rounds=1,
        top_k=3,
        tracer=ctx.tracer,
        max_sections=2,
    )
    evidence_ids = {r.doc.doc_id for s in article.sections for r in s.evidence}
    return EvalRunResult(output=article.article, meta={"sections": len(article.sections), "evidence_ids": sorted(evidence_ids)})


def _task_manager_worker(ctx: EvalContext) -> EvalRunResult:
    manager = ctx.make_model("manager")
    workers = [
        Worker(name="math", description="math", model=ctx.make_model("math")),
        Worker(name="writer", description="writer", model=ctx.make_model("writer")),
    ]
    out = run_manager_worker(manager, workers, task="Compute 2+2 and explain briefly.", tracer=ctx.tracer)
    return EvalRunResult(output=out)


def _task_agents_as_tools(ctx: EvalContext) -> EvalRunResult:
    controller = ctx.make_model("controller")
    tools = ToolRegistry(
        [
            agent_as_tool(
                AgentToolSpec(
                    name="math_agent",
                    description="math",
                    model=ctx.make_model("math_agent"),
                    system_prompt="Return only the numeric result.",
                ),
                tracer=ctx.tracer,
            ),
            agent_as_tool(
                AgentToolSpec(
                    name="style_agent",
                    description="writer",
                    model=ctx.make_model("style_agent"),
                    system_prompt="Return one short sentence.",
                ),
                tracer=ctx.tracer,
            ),
        ]
    )
    out = run_react(
        controller,
        task="Compute 7*6 and present it nicely.",
        tools=tools,
        limits=RunLimits(max_steps=6),
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=out)


def _task_group_chat_selector(ctx: EvalContext) -> EvalRunResult:
    selector = ctx.make_model("selector")
    agents = [
        ChatAgent(name="researcher", description="facts", model=ctx.make_model("researcher")),
        ChatAgent(name="writer", description="final", model=ctx.make_model("writer")),
    ]
    out = run_group_chat_selector(selector, agents, task="Compute 2+2.", max_turns=4, tracer=ctx.tracer)
    return EvalRunResult(output=out)


def _task_handoff(ctx: EvalContext) -> EvalRunResult:
    router = ctx.make_model("router")
    agents = [HandoffAgent(name="math", description="math", model=ctx.make_model("math"))]
    out = run_handoff(router, agents, task="What is 9+1?", tracer=ctx.tracer)
    return EvalRunResult(output=out)


def _task_magentic(ctx: EvalContext) -> EvalRunResult:
    orchestrator = ctx.make_model("orchestrator")
    specialists = [Specialist(name="calc", description="math", model=ctx.make_model("calc"))]
    out = run_magentic_orchestration(
        orchestrator,
        specialists,
        task="Compute 3+4.",
        limits=RunLimits(max_steps=4),
        stall_limit=2,
        tracer=ctx.tracer,
    )
    return EvalRunResult(output=out)


def _task_governance(ctx: EvalContext) -> EvalRunResult:
    _ = ctx

    def deploy(args: dict) -> str:
        return f"DEPLOYED to {args['env']}"

    tools = ToolRegistry([Tool(name="deploy", description="deploy", handler=deploy)])

    policy = ToolPolicy(
        allowed_tools={"deploy"},
        per_tool={
            "deploy": ToolArgsPolicy(required_keys={"env"}, bounds={"env": ParamBound(pattern=r"(dev|staging|prod)")})
        },
    )
    guardrails = Guardrails(tool_output_text=[BannedRegexTripwire(patterns=[r"ERROR"])])
    hitl = HITLController(require_approval_for_tools={"deploy"})

    tool_name = "deploy"
    tool_args = {"env": "prod"}
    policy.check_tool_call(tool_name, tool_args)
    try:
        hitl.check(tool_name, tool_args, reason="prod_deploy_requires_approval")
    except NeedsApproval as e:
        hitl.approve(e.request)

    out = tools.call(tool_name, tool_args)
    guardrails.check_tool_output(out)
    return EvalRunResult(output=out)


class _StubOpenAIResp:
    def __init__(self, text: str) -> None:
        self.choices = [_StubOpenAIChoice(text)]


class _StubOpenAIChoice:
    def __init__(self, text: str) -> None:
        self.message = _StubOpenAIMsg(text)


class _StubOpenAIMsg:
    def __init__(self, text: str) -> None:
        self.content = text


class _StubOpenAICompletions:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    def create(self, **_kwargs):  # type: ignore[no-untyped-def]
        return _StubOpenAIResp(self.reply)


class _StubOpenAIChat:
    def __init__(self, reply: str) -> None:
        self.completions = _StubOpenAICompletions(reply)


class _StubOpenAIClient:
    def __init__(self, reply: str) -> None:
        self.chat = _StubOpenAIChat(reply)


def _task_openai_adapter_stub(ctx: EvalContext) -> EvalRunResult:
    _ = ctx
    model = OpenAIChatModel(model="stub", client=_StubOpenAIClient("ok"))
    out = model.complete([Message(role="user", content="hi")])
    return EvalRunResult(output=out)


class _AnthropicBlock:
    def __init__(self, text: str) -> None:
        self.text = text


class _AnthropicResp:
    def __init__(self, text: str) -> None:
        self.content = [_AnthropicBlock(text)]


class _StubAnthropicMessages:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    def create(self, **_kwargs):  # type: ignore[no-untyped-def]
        return _AnthropicResp(self.reply)


class _StubAnthropicClient:
    def __init__(self, reply: str) -> None:
        self.messages = _StubAnthropicMessages(reply)


def _task_anthropic_adapter_stub(ctx: EvalContext) -> EvalRunResult:
    _ = ctx
    model = AnthropicMessagesModel(model="stub", client=_StubAnthropicClient("ok"))
    out = model.complete([Message(role="system", content="sys"), Message(role="user", content="hi")])
    return EvalRunResult(output=out)
