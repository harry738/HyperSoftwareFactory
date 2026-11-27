# 07 Gergely Orosz — Inside OpenAI’s agentic software factory

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Title:** Inside OpenAI’s agentic software factory
- **Author:** Gergely Orosz, The Pragmatic Engineer, based on interviews with seven OpenAI engineering leaders (named in the article)
- **Published:** 15 September 2026. Marked **Paid**.
- **URL:** https://newsletter.pragmaticengineer.com/p/openai-software-factory
- **Added:** 25 November 2026 (Europe/London). No subscription or account interaction was used.

**Coverage limit:** A public fetch returned the introduction and **sections 1–3 in full**, plus the opening sentence of section 4, then stopped. Sections 4–7 (tooling practices, billion-user infra, API performance, how the job is changing) were **not available** in this pass and are not summarised here.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Phase 3 (review, PR load); Phase 4 (F6 deploy/rollback, telemetry, on-call); Phase 1–2 (risk classification, harness, long-running jobs). Risk tiers: high-risk gets stricter review; low-risk paths at OpenAI can auto-approve — **do not copy that default**. Roster: Release/Ops and Sevbot-like helpers must not execute mitigations unless the operator says so.

**Scores:** Relevance H. Actionability M (process lessons; not a drop-in architecture). Novelty M (production-feedback loop is the newest piece vs our plan).

**Dedupe:** Overlaps Holmes (merge risk, review bottleneck), Gumloop (telemetry-driven fixes, human merge), Agent Baseline / Sevbot (propose, don't execute). Not a duplicate.

## Summary (from the public portion only)

Orosz reports that Codex (and ChatGPT Work) became the backbone of work at OpenAI from about January 2026, including among non-engineers, without a top-down mandate. He warns that OpenAI's **internal** Codex is more advanced than the external product.

Section 2, "Death of the IDE & pull requests," is about IDE usage falling and **PR and CI load growing very fast** (an interviewed VP describes roughly a 10x load increase on some systems in about six months). PRs and reviews "need to be rethought." That is a report of strain and a call to reimagine review, not a recommendation that HyperSoftwareFactory drop pull requests.

Section 3 describes OpenAI's "software factory" as agentic feedback loops. Code changes are classified by risk. Some areas may opt in to an agent that auto-approves low-risk PRs — reported as OpenAI practice, **not** recommended here. After a **human** approves a change for production, a deploy agent "handholds" rollout and may build per-change dashboards. **Perf Factory** sifts alerts, de-duplicates, root-causes, and **proposes** fixes. **Sevbot** collects incident context and possible mitigations "**but never executes any**" until an engineer tells it to apply a specific mitigation. Autonomous out-of-hours mitigation is a goal, not the current state.

## Key learnings (quotes from the fetched text)

> "Determines possible mitigations (but never executes any)"

> "After a human approves a change to go to production, it is assigned its own agent"

> "The number of pull requests (PRs) per engineer is growing like a hockey stick"

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Operator merges; risk routing; event log / budgets; F6 planned after the operator promotes; Sevbot's "never execute unless told" matches Release/Ops and fail-closed reviewers in the LLM spec. |
| **Incorporate** | Keep a human in front of production promote (already the rule). Let a helper **propose** incident or perf fixes, never auto-apply (F6 / F4). Per-change proof and dashboards are Phase 4 telemetry inspiration. Plan for higher CI/review load once E1.6 works. |
| **Inspiration** | Long-running /goal threads; role-specific plugins; "per-change autonomous SRE" as a distant idea. |
| **Do not incorporate** | Auto-approve or auto-merge of "low-risk" PRs. Dropping pull requests. Copying OpenAI's unlimited-token, single-harness setup. Acting on the unread paid sections. |

Figures about adoption percentages and 10x load are OpenAI-via-Orosz, not independently re-measured.
