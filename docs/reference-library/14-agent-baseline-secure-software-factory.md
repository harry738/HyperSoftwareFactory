# 14 Agent Baseline — The Secure Software Factory: A Reference Architecture

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Title:** The Secure Software Factory: A Reference Architecture
- **Publisher:** Agent Baseline (https://agentbaseline.org/reference-architecture)
- **Version:** 1, dated **13 October 2026**, status **"Open for comment."**
- **Authors listed on the page** (affiliations as printed there): people from Docker, Keycard, Barclays, Socket, and Secure Theory. This note does not restate individual names.
- **Fetched:** 25 November 2026 from the public page. No comment, subscription, or other interaction was used. A longer PDF may exist; **only the web page was read**. Claims that appear only in an unread PDF are not used here.
- **Added:** 25 November 2026.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Agent roster (scripted factory run is L2; agents must not hold the GitHub token or grant themselves access); E6 (sandbox and network boundaries); LLM spec (`data_leaving_lan` deny; providers are backends); Phase 0 (#26 fail-closed merge); event log (Observe); F4 untrusted intake. Entry 03 (layered guardrails, cheapest first, fail closed).

**Scores:** Relevance H. Actionability H (document boundaries; map autonomy levels). Novelty M (formalises existing rules; first dedicated architecture paper in this library).

**Dedupe:** The market scan (entry 04) already mentioned a LinkedIn "Insecure Agents / Agent Baseline" item in passing. This is the first full read of the reference-architecture page, so it deserves its own entry. Overlaps entry 03, the LLM spec, E6, and (later) Prismor as a possible enforcement hook — Prismor is a product; this is a model.

**Comparison to the current plan:** The roster already keeps the GitHub token on the orchestrator script; reviewers fail closed; the operator merges. The LLM spec already defaults `data_leaving_lan` to deny. E6 is the sandbox/allowlist. HyperSoftwareFactory as designed is closest to **L2 Workflow-Orchestrated**, not L3.

## Summary

The page sets out a reference architecture for a **secure software factory** for agentic coding. It starts from six outcomes: **Discover, Constrain, Authorize, Validate, Observe, Respond.** The organizing sentence:

> "The agent proposes, policy authorizes, and infrastructure enforces."

Four **boundaries** must be explicit:

1. **Sandbox** — what the agent process can touch on the machine.
2. **Network** — where it can send data (maps to `data_leaving_lan` and egress allowlists).
3. **Supply chain** — what it may install or pull.
4. **Identity and access** — who the agent is, and what tokens it does (not) hold.

Three **autonomy levels**:

- **L1 Human-Orchestrated** — a person starts each step.
- **L2 Workflow-Orchestrated** — a recorded workflow chooses the next step and the tools; the agent works inside that path.
- **L3 Agent-Orchestrated** — the agent may choose the next step, but **must not grant itself access**.

The page says the work started from observed failures (it cites an example of an agent that deleted a production database in nine seconds). That example is taken only as printed on the page.

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | L2 matches scripted `factory run`. Token isolation matches "infrastructure enforces." Fail-closed reviewers and #26 match Authorize / Validate. Event log matches Observe. LLM egress default matches the network boundary. Entry 03 already says cheapest-first, fail-closed. |
| **Incorporate** | Document the four boundaries in the roster, the LLM spec, and the E6 notes (as a short map, not new official IDs). Explicitly label the current design as **L2**, and say L3 is out of scope until the operator asks. Keep "the agent must not grant itself access" as a standing rule. |
| **Inspiration** | The six-outcome vocabulary (Discover…Respond) as headings in later security notes. |
| **Do not incorporate** | Jumping to L3 agent-orchestrated control flow. Treating the page as a mandate to buy the authors' products (Docker, Keycard, Socket, and so on). Acting on unread PDF material. |
