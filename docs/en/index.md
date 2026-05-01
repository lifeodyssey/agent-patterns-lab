# Agent Design Patterns Map

This site is a **problem-driven map** of common agent design patterns.

The core idea: *patterns are not “fancier = better”*. They are **responses to new failure modes** that appear when you add tools, longer horizons, retrieval, multiple agents, and production constraints.

## The Evolution Thread (Simple → Complex)

1. **Single-shot** (no loop): fast, cheap, but fragile.
2. **Structured output**: when you need machine-readable JSON, add parsing + repair retries.
3. **Workflows**: when the control flow is known, use Prompt Chaining / Routing.
4. **Agent loop**: when the next step depends on observations, use Tool Calling + ReAct.
5. **Reliability**: when mistakes are costly, add Maker-Checker / Voting / CoVe + retries/circuit breakers.
6. **Memory & Retrieval**: when knowledge is missing, add Retrieval Loop → Agentic RAG + evidence ledger.
7. **Planning & Search**: when tasks are long-horizon, add Plan & Solve / PER / REWOO / DAG / Tree Search.
8. **Multi-agent**: when you need specialization and scale, use Manager-Worker / Agents-as-Tools / Group Chat / Handoff / Magentic.
9. **Governance & Eval**: when shipping, add Policy + Guardrails + HITL + Tracing + Eval Harness.

## Mind Map (Pattern Families)

```mermaid
mindmap
  root((Agent Patterns))
    Workflow
      Prompt Chaining
      Routing
    Agent Loop
      Tool Calling
      ReAct
    Reliability
      Maker-Checker
      Voting(Self-Consistency)
      CoVe(Verification)
      Retry/Backoff
      Circuit Breaker
      Cache
    Memory & Retrieval
      Memory(KV/Session)
      Retrieval Loop
      Agentic RAG(Evidence Ledger)
      Reflexion
      STORM(Research Writing)
    Planning & Search
      Plan & Solve
      PER(Replan)
      REWOO(Batch Tools)
      LLM Compiler(DAG)
      LATS(Tree/Beam Search)
      Self-Discovery(Modules)
    Multi-Agent
      Manager-Worker
      Agents-as-Tools
      Group Chat/Council
      Handoff(Triage)
      Magentic(ledger+stall)
    Governance
      Policy(Tool Allowlist)
      Guardrails(Tripwires)
      HITL(Approval)
    Observability & Eval
      Tracing
      Eval Harness
```

## “If You See X, Use Y” (Decision Tree)

```mermaid
flowchart TD
  A["Start: define the task"] --> B{"Need machine-readable output?"}
  B -->|Yes| SO["Structured Output + Repair"]
  B -->|No| C{"Multi-step reasoning?"}
  C -->|No| SS["Single-shot answer"]
  C -->|Yes| D{"Control flow fixed?"}
  D -->|Yes| WF["Workflow: Prompt Chaining / Routing"]
  D -->|No| E{"Need external actions/tools?"}
  E -->|No| PL["Planning: Plan & Solve / PER"]
  E -->|Yes| RL["Agent loop: Tool Calling + ReAct"]
  RL --> R{"High error cost?"}
  R -->|Yes| REL["Reliability: Maker-Checker / Voting / CoVe + Retry/Circuit"]
  RL --> K{"Missing knowledge?"}
  K -->|Yes| RAG["Retrieval Loop / Agentic RAG"]
  PL --> S{"Need graph/search?"}
  S -->|Yes| SEARCH["LLM Compiler(DAG) / LATS(Tree Search)"]
  RL --> MA{"Need specialization?"}
  MA -->|Yes| MULTI["Manager-Worker / Agents-as-Tools / Group Chat"]
  MULTI --> HO["Handoff (triage/escalation)"]
  MULTI --> MG["Magentic (ledger + stall detection)"]
  REL --> GOV{"Prod safety?"}
  GOV -->|Yes| SAFE["Policy + Guardrails + HITL + Sandbox"]
  SAFE --> EV["Tracing + Eval Harness"]
```

## How This Book Is Organized

- **Building Blocks**: the minimal runtime features that patterns reuse (structured output, tools, loops, tracing, memory, etc.).
- **Patterns**: one page per pattern, focusing on *problem → core loop → trade-offs → evolution path*.
- **Governance & Evaluation**: how to make the system shippable and regressions detectable.

