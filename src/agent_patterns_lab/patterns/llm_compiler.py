from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agent_patterns_lab.runtime import Message, SchemaValidationError, Tracer, structured_complete
from agent_patterns_lab.runtime.model import Model


@dataclass(frozen=True, slots=True)
class TaskNode:
    task_id: str
    instruction: str
    deps: list[str]


@dataclass(frozen=True, slots=True)
class CompiledPlan:
    nodes: list[TaskNode]
    final_instruction: str


DAG_SCHEMA_HINT = """{
  "tasks": [{"id":"t1","instruction":"...","deps":["t0"]}],
  "final": {"instruction":"..."}
}"""


def llm_compiler(
    model: Model,
    *,
    task: str,
    tracer: Tracer | None = None,
    max_tasks: int = 12,
) -> str:
    """
    LLM Compiler (simplified):
    1) Ask model to "compile" a plan into a DAG (tasks with deps)
    2) Execute tasks topologically, feeding dep outputs into each task
    3) Run a final assembly step
    """
    compiled = compile_to_dag(model, task=task, tracer=tracer, max_tasks=max_tasks)
    outputs = execute_dag(model, compiled, tracer=tracer)
    return outputs["__final__"]


def compile_to_dag(
    model: Model,
    *,
    task: str,
    tracer: Tracer | None = None,
    max_tasks: int = 12,
    max_retries: int = 2,
) -> CompiledPlan:
    if max_tasks <= 0:
        raise ValueError("max_tasks must be > 0")

    def parse(value: Any) -> CompiledPlan:
        if not isinstance(value, dict):
            raise SchemaValidationError("expected object")
        tasks = value.get("tasks")
        final = value.get("final")
        if not isinstance(tasks, list):
            raise SchemaValidationError('"tasks" must be a list')
        if not isinstance(final, dict):
            raise SchemaValidationError('"final" must be an object')
        final_instruction = final.get("instruction")
        if not isinstance(final_instruction, str) or not final_instruction.strip():
            raise SchemaValidationError('final.instruction must be non-empty string')

        nodes: list[TaskNode] = []
        seen: set[str] = set()
        for item in tasks[:max_tasks]:
            if not isinstance(item, dict):
                continue
            tid = item.get("id")
            instr = item.get("instruction")
            deps = item.get("deps", [])
            if not isinstance(tid, str) or not tid.strip():
                raise SchemaValidationError("task.id must be non-empty string")
            if tid in seen:
                raise SchemaValidationError(f"duplicate task id: {tid}")
            if not isinstance(instr, str) or not instr.strip():
                raise SchemaValidationError(f"task {tid} instruction must be non-empty string")
            if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
                raise SchemaValidationError(f"task {tid} deps must be list[str]")
            seen.add(tid)
            nodes.append(TaskNode(task_id=tid, instruction=instr.strip(), deps=[d.strip() for d in deps if d.strip()]))

        if not nodes:
            raise SchemaValidationError("tasks must contain at least one task")

        # Ensure deps refer to existing nodes and graph is acyclic.
        node_ids = {n.task_id for n in nodes}
        for n in nodes:
            for d in n.deps:
                if d not in node_ids:
                    raise SchemaValidationError(f"task {n.task_id} has unknown dep: {d}")
        _topo_sort(nodes)  # validates cycle
        return CompiledPlan(nodes=nodes, final_instruction=final_instruction.strip())

    return structured_complete(
        model,
        [
            Message(
                role="system",
                content=(
                    "Compile a plan into a DAG of tasks with dependencies.\n"
                    "Return ONLY JSON matching the schema."
                ),
            ),
            Message(role="user", content=f"Task:\n{task}\n\nReturn JSON now."),
        ],
        parser=parse,
        schema_hint=DAG_SCHEMA_HINT,
        max_retries=max_retries,
        tracer=tracer,
    )


def execute_dag(
    model: Model,
    compiled: CompiledPlan,
    *,
    tracer: Tracer | None = None,
) -> dict[str, str]:
    order = _topo_sort(compiled.nodes)
    outputs: dict[str, str] = {}

    for node in order:
        dep_text = "\n".join(f"- {d}: {outputs[d]}" for d in node.deps) if node.deps else "(none)"
        prompt = (
            f"Task node: {node.task_id}\n"
            f"Instruction:\n{node.instruction}\n\n"
            f"Dependency outputs:\n{dep_text}\n\n"
            "Return the result text."
        )
        out = model.complete(
            [
                Message(role="system", content="Execute the task node."),
                Message(role="user", content=prompt),
            ],
            tracer=tracer,
        )
        outputs[node.task_id] = out
        if tracer is not None:
            tracer.emit("llm_compiler.node", task_id=node.task_id, deps=len(node.deps))

    final_prompt = (
        f"Final assembly instruction:\n{compiled.final_instruction}\n\n"
        "All task outputs:\n"
        + "\n".join(f"- {tid}: {text}" for tid, text in outputs.items())
    )
    final_out = model.complete(
        [
            Message(role="system", content="Assemble the final result."),
            Message(role="user", content=final_prompt),
        ],
        tracer=tracer,
    )
    outputs["__final__"] = final_out
    if tracer is not None:
        tracer.emit("llm_compiler.final")
    return outputs


def _topo_sort(nodes: Sequence[TaskNode]) -> list[TaskNode]:
    by_id = {n.task_id: n for n in nodes}
    indeg: dict[str, int] = {n.task_id: 0 for n in nodes}
    children: dict[str, list[str]] = {n.task_id: [] for n in nodes}

    for n in nodes:
        for d in n.deps:
            indeg[n.task_id] += 1
            children[d].append(n.task_id)

    queue = [tid for tid, deg in indeg.items() if deg == 0]
    out: list[TaskNode] = []
    while queue:
        tid = queue.pop(0)
        out.append(by_id[tid])
        for c in children[tid]:
            indeg[c] -= 1
            if indeg[c] == 0:
                queue.append(c)

    if len(out) != len(nodes):
        raise SchemaValidationError("cycle detected in DAG tasks")
    return out
