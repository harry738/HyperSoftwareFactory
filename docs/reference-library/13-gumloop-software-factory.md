# 13 Gumloop Engineering — Software Factory

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Title:** Software Factory. Tagline on the page: "Agents that autonomously find, fix, and prove product improvements."
- **Publisher:** Gumloop Engineering. The origin story names CTO **Rahul Behal**. No separate byline date was printed on the page.
- **URL:** https://www.gumloop.com/engineering/software-factory
- **Fetched:** 25 November 2026 (Europe/London) from the public HTML (`<article>` extract). No account, subscription, or interaction was used. A plain WebFetch of the URL returned only a short stub; the full article was taken from the HTML.
- **Figures:** labelled "as of October 28, 2026." The Factory "started merging its first PRs on September 14." Some chart captions are marked **"conceptual, not production telemetry"** — those are not treated as measurements.
- **Added:** 25 November 2026.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Phase 2 (E1.6 first real line of work; checks and proof); Phase 3 (engineer reviews and merges; evidence on the PR); Phase 4 (F3 skills and remembered judgment; F4/F6 telemetry-triggered jobs; provider-agnostic worker). Roster: "Gumloop worker" is an orchestrator, not the coding model. **Human merge is mandatory in their design.**

**Scores:** Relevance H (closest operational narrative in this batch). Actionability H for process; L for adopting Gumloop as a product. Novelty M–H (clear published merge rule plus line-owner model and measured skill hygiene).

**Dedupe:** Reinforces Holmes (proof, gates), Chase (write down judgment), Itamar (factory is the product), and entry 04. Distinct because they **explicitly never self-merge**, which contradicts Rafal's automerge path and the 0xcodez/Tan quote.

**Comparison to the current plan:** `deployable-roadmap.md` already has a plan gate, checks, a first real job, fresh-context review, and later telemetry. `agent-roster.md` already keeps the GitHub token on a script, not a model, and makes the operator the only merger. `llm-provider-integration.md` already treats the coding CLI as a swappable harness. Gumloop is a close story of those same choices, not a reason to change the spine.

## Summary

Gumloop built an internal factory of **lines** (latency, slow APIs, platform, QA), each with a **human line owner**. A trigger (schedule, telemetry, or a ping) opens a Linear issue. A Gumloop workflow acts as engineering manager, starts a coding agent (**Cursor and/or Devin** today; they want Codex or Claude Code later), and opens a PR **with proof** (typically a fail-then-pass test). Quote:

> "An engineer reviews it and merges it. The Factory never merges its own work."

Judgment calls made in Slack are written down and reused. They report writing **94 skills in five weeks**, and that the share of PRs merged with no human code edits rose from **57% to 89%** as skills accumulated. Trimming **AGENTS.md by 44%** was followed by a **20%** drop in median cloud-agent run cost (author-reported association, not a controlled study).

Author-reported metrics (vendor self-report, not independently audited): **571** agent-written PRs in six weeks; **83%** of closed agent PRs had no human code changes (335 clean plus 128 automated review-bot fixes, of 556 closed); **90%** of finished jobs ended with a merged PR; line owners saw about **2.5×** PRs/week; P99 time-to-agent-start fell **24.9s → 4.5s**; they cite about **40%** of database query CPU from the factory. Their advice at the end: find a process you already repeat, write it down, make it a line, and delegate.

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Operator merges; PR evidence pack; skills / AGENTS.md hygiene; orchestrator is not the model; coding agent should be swappable (LLM spec); telemetry as a later intake source (F4/F6); E1.6 as the first "line." |
| **Incorporate** | Keep "the factory never merges its own work" as a stated rule. Remember judgment calls via a curator PR (with Chase, F3) rather than informal chat. Treat AGENTS.md bloat as a cost issue. Start with one repeated, verifiable process (already E1.6). |
| **Inspiration** | Named human line owners; Linear/Slack as the ticketing/chat layer (only if the operator chooses those tools). Their published percentages as a comparison, not a target. |
| **Do not incorporate** | Rebuilding the factory on Gumloop, Linear, or Devin as required products. Auto-merge. Treating conceptual charts or unaudited vendor metrics as facts. |
