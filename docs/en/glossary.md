# Glossary (Key Terms)

This glossary standardizes terms used across the map and pattern pages.

If you see a term used differently on a page, treat this page as the source of truth.

## What Problem It Solves

Agent systems get confusing fast—not because the patterns are hard, but because teams silently drift on terms:

- “agent” vs “workflow”
- “tool calling” vs “function calling”
- “retrieval loop” vs “agentic RAG”

In a bilingual site, drift is even easier. This page pins down **one preferred term + one meaning** so the rest of the docs stay coherent.

## When to Use

- You’re reading a pattern page and want a fast definition.
- You’re writing/editing a page and need consistent terminology (especially EN↔ZH).
- You’re unsure whether two names are actually the same pattern (often they are).

## How It Works (How to Maintain It)

- Prefer **one canonical name** per concept.
- If a synonym is common, mention it once in **Notes** (don’t create two competing entries).
- Keep entries short: 1–2 sentences + a pragmatic note.
- If a term becomes “big enough”, promote it to its own pattern or building block page.

## Worked Example (Adding a Term)

When you add a new concept, add:

- a short definition
- one pragmatic note (what people confuse it with)
- 1–3 “See also” references

Example:

```text
| **Tool policy** | Rules for which tools are allowed (and with what args). | Usually allowlist-first; pair with guardrails. |
```

## Failure Modes & Mitigations

- **Synonym soup**: enforce one canonical name, list synonyms as notes only.
- **Bilingual drift**: treat EN+ZH pages as a pair; update both in the same change.
- **Over-explaining**: if an entry needs paragraphs, it probably belongs on a dedicated page.

## Core Runtime Terms

| Term | Meaning (short) | Notes |
|---|---|---|
| **Workflow** | A fixed (or limited-branch) control flow defined by code/config. | Easier to test than an agent loop. |
| **Agent** | A controller where the *next step* is decided dynamically by an LLM given the current state. | “Agent” here is about **control flow**, not consciousness. |
| **Agent loop** | A closed loop: decide → act (tool) → observe → update state → repeat. | ReAct is the canonical form. |
| **State** | Everything the controller can “see”: messages + scratchpad/ledger + relevant memory. | Keep it structured when possible. |
| **Action schema** | A machine-readable format for “what to do next” (tool/final/ask). | Prevents brittle text parsing. |
| **Tool calling** | The agent selects a tool/function, provides args, receives an observation. | Also called “function calling”. |
| **Observation** | Tool output appended back into state. | Treat retrieved text as *untrusted input*. |
| **Budget** | Hard limits: max steps / tool calls / tokens / time / cost. | Stops runaway loops. |

## Retrieval & Memory

| Term | Meaning (short) | Notes |
|---|---|---|
| **Retrieval (RAG)** | Fetch external context (docs) and ground generation on it. | Vanilla RAG is often “retrieve once → answer”. |
| **Retrieval loop** | Iterate: retrieve → read → refine query → retrieve again → stop when enough. | A specialized loop for search. |
| **Agentic RAG** | Retrieval is *inside the agent loop*: the model decides when/what to retrieve and when to stop. | Often adds an evidence ledger for auditability. |
| **Evidence ledger** | A structured record mapping claims → supporting sources/snippets/doc_ids. | Mitigates “citation theater” and enables audits. |
| **Memory** | Persisted state across steps or sessions (KV, summaries, episodic notes). | Used by Reflexion and long-horizon agents. |
| **Episodic memory** | “Lessons learned” from past runs stored as text or structured notes. | Reflexion-style learning without weight updates. |

## Reliability & Verification

| Term | Meaning (short) | Notes |
|---|---|---|
| **Maker-Checker** | Generate → critique → revise loop (sometimes multiple rounds). | Also called “reviewer/critic”. |
| **Voting / self-consistency** | Sample multiple candidates and aggregate (vote/rank/merge). | Reduces variance; increases cost. |
| **CoVe (verification chain)** | Draft claims → verify claims (tools/rules) → fix. | Treat verification as a first-class loop. |
| **Retry / backoff** | Re-attempt failed steps with delays or adjusted params. | Combine with budgets + circuit breakers. |
| **Circuit breaker** | Stop or degrade when repeated failures happen (tool outage, rate limit). | Prevents infinite retry storms. |

## Planning & Search

| Term | Meaning (short) | Notes |
|---|---|---|
| **Plan & Solve** | First produce an explicit plan; then execute/answer. | Helps multi-step reasoning. |
| **Planner–Executor–Replanner (PER)** | Plan → execute → replan based on feedback/failures/budget. | Makes re-planning explicit. |
| **ReWOO** | “Reasoning without observation”: draft a tool plan first, then execute tools in a batch. | Can reduce token churn vs ReAct. |
| **LLM Compiler** | Compile a plan into a DAG of tool calls, then execute with dependencies. | Helps parallelism and repeatability. |
| **LATS** | Tree search over trajectories; expand/evaluate/backprop to pick better paths. | High cost; used for hard problems. |

## Multi-Agent

| Term | Meaning (short) | Notes |
|---|---|---|
| **Manager–Worker** | A coordinator decomposes tasks and delegates to specialist workers. | Useful for specialization + parallelism. |
| **Agents-as-Tools** | Treat each specialist agent as a callable tool behind an orchestrator. | Simplifies routing + governance. |
| **Group chat / council** | Multiple agents discuss/critique; a selector merges or chooses. | Can resemble “debate” or “committee”. |
| **Handoff / triage** | Route the task to the best next agent (or a human) based on signals. | Prevents the “one agent for everything” trap. |

## Governance, Observability, Evaluation

| Term | Meaning (short) | Notes |
|---|---|---|
| **Policy** | Rules for allowed tools, parameter bounds, and permissions by route/task. | “Allowlist-first” for safety. |
| **Guardrails** | Input/output/tool tripwires (block, redact, ask approval). | Catch prompt injection, unsafe actions, leaks. |
| **HITL** | Human-in-the-loop approvals for risky actions (writes, money, prod). | Must support resume after approval. |
| **Tracing** | Structured logs of steps, tool calls, decisions, and timing. | Enables debugging and evals. |
| **Eval harness** | A reproducible task suite + scoring + regression reports. | Lets you prove improvements over time. |

## “Human voice” (Docs)

| Term | Meaning (short) | Notes |
|---|---|---|
| **Template-y writing** | Copy-paste structure that reads generic and low-signal. | Fix by adding concrete failure modes and worked examples. |
| **Banned phrase list** | Words/phrases you prohibit to reduce AI-ish filler. | Enforce at generation or in polish. |

## References

- Agentic RAG (overview): https://www.ibm.com/think/topics/agentic-rag
- Agentic RAG (glossary-style): https://exploreagentic.ai/glossary/agentic-rag/
- Agentic RAG (public-sector risks): https://www.gov.uk/government/publications/ai-insights/ai-insights-agentic-rag-html
- Reflexion (paper): https://arxiv.org/abs/2303.11366
- Plan-and-Solve (paper): https://arxiv.org/abs/2305.04091
- ReWOO (paper): https://arxiv.org/abs/2305.18323
- LATS (paper): https://arxiv.org/abs/2310.04406
- “Human voice” editing habits (practical): https://www.microsoft.com/en-us/microsoft-copilot/copilot-101/humanize-ai-text
