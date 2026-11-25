# 09 Rafal Wilinski — Runlayer software factory (multi-source intake)

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Author:** Rafal Wilinski ([@rafalwilinski](https://x.com/rafalwilinski)), founding engineer at Runlayer, ex-AI agents lead at Zapier. Verified account.
- **Posted:** 13 October 2026, 09:35 UTC (10:35 UK time, BST).
- **X post:** https://x.com/rafalwilinski/status/2109940991868252302
- **Full text:** in the post's `note_tweet` (the 280-character preview is truncated mid-sentence).
- **Video:** about 41 seconds. **Not watched.** Notes below use the long post text, public replies, and the linked Agentation site.
- **Linked product:** https://www.agentation.com/ — "Visual feedback for agents." Pins on UI elements become structured context (selectors, source paths, notes). Free for internal use; commercial licence if redistributed in a product you sell.
- **Public replies read (not engaged with):** 18 replies in the conversation, including the author's own reply. The author wrote: "some paths have strict codeowners, nothing gets merged without their signoff. review agent is also tuned to know which paths are critical/hot/risky + which features are beta or GA or prototype." Other replies asked about rollback ownership, automerge drift, and enablement lag; those are questions, not facts.
- **Added:** 25 November 2026. Nothing was posted or replied to on X.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Phase 4 (F4/F8 intake, changelog / F3 enablement); Phase 1 (dedupe against open issues/PRs; route auth/hotpath to humans — maps to Tier 3 / always-stop); Phase 3 (adversarial review, screenshots on PRs). **Do not** tag this as a model for unattended merge.

**Scores:** Relevance H for intake and routing. Actionability M (process yes; auto-merge no). Novelty M (multi-source signals and UI pins are the new bits).

**Dedupe:** Overlaps Holmes and Gumloop on PR proof and human review; overlaps F4/F8 on external signals. The "91 PRs merged" automerge path conflicts with the operator's merge rule and with Gumloop's "Factory never merges its own work."

**What was and was not covered:** Long post text, replies, and Agentation's public page were read. The 41-second video was not watched.

## Summary

Wilinski's claim is that a software factory need not start at a prompt or end at merge to main. Runlayer's factory (author's account of their own system) takes signals from customer calls (Fireflies), customer Slack, red CI on main, @-mentions, DMs, and **UI pins on production** via Agentation (element, page, and note go to a webhook and start an agent).

Every ask is checked against Linear and open PRs to dedupe. Small, clear work is built immediately. Bigger work, or anything near **auth or hotpath**, goes to engineers with a write-up or draft PR. A sandboxed agent reproduces, fixes, tests, and opens a PR with screenshots or a walkthrough. Another agent does an adversarial review. The author says **small, non-risky changes are approved and automerged**; a follow-up agent handles review comments, CI, and conflicts; humans jump in only when requested; after merge it goes to prod, a QA fuzzing agent pokes it, and stakeholders are DMed. He reports **one agent got 91 PRs merged in a 24-hour stretch** (author claim, not audited). Enablement lagged, so they keep an append-only changelog and a Friday video summary.

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Path-based always-stop for auth/hotpath (Tier 3). Sandbox, tests, and a second reviewer. PR screenshots already proposed. Proposals are never auto-queued today. |
| **Incorporate** | Dedupe new intake against open issues and PRs (Phase 1 / F8). UI-pin or structured visual feedback is optional later inspiration (Agentation is a third-party tool with its own licence). An append-only changelog plus a short digest (F3 / enablement), because speed can outrun the team. Codeowners-style stop on sensitive paths (author's reply). |
| **Inspiration** | Fireflies/Slack as signal sources — only via official APIs, and only if the operator agrees. Post-merge notify. |
| **Do not incorporate** | Automerge, even for "small" changes. Auto-deploy to production. "Humans jump in only when requested" as the default. The 91-PR figure as a target. |

Treat all throughput figures as the author's report.
