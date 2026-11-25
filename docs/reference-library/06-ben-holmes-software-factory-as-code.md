# 06 Ben Holmes — How to build a software factory you'll actually use

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Title:** How to build a software factory you'll actually use
- **Author:** Ben Holmes ([@BHolmesDev](https://x.com/BHolmesDev)), "The Whiteboard Guy and Factory Foreman" at Warp. Verified account.
- **Posted:** 24 November 2026, 22:11 UTC (22:11 UK time, Europe/London)
- **X post:** https://x.com/BHolmesDev/status/2125351601431089418
- **X Article:** https://x.com/i/article/2125313266192887808
- **Same article on the Warp blog:** https://www.warp.dev/blog/program-software-factory-as-code (24 November 2026). Claims below are taken from the article text (X Article and blog agree).
- **Also linked:** https://www.warp.dev/merge-risk (merge-risk skill; not separately audited here)
- **Added:** 25 November 2026 (Europe/London). Nothing was posted or replied to on X.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Phase 1 (triage, specs, plan-approval gate, structured workflow as code); Phase 2 (checks, verification); Phase 3 (PR evidence, merge-risk headings, fresh-context review); risk tiers (Impact / Rollback cost alongside existing low/medium/high). Agent roster: foreman vs builder sandboxes (orchestrator script vs builder; do not give the builder the merge token).

**Scores:** Relevance H. Actionability H. Novelty M (reinforces already-planned gates and the PR evidence pack).

**Dedupe:** Overlaps entry 04 (Cursor artefacts, Spec Kit, review bottleneck), the Gemini/deployable plan (triage, specs, plan gate), and later Gumloop (proof on the PR, human merges). Not a duplicate; this is the clearest "factory as code + human gates + verification + merge risk" write-up in the set.

## Summary

Holmes says teams often start with a backlog-to-PR loop and end up with a "slop cannon." A factory he would actually use focuses on centralized knowledge of how agents should work, and a step-by-step workflow the team can measure and improve.

He encodes the pipeline as a **YAML blueprint** with named stages, structured inputs/outputs, and separate **workers** (sandboxes / context windows): a foreman at the front door and a builder that writes code. Then he adds **triage** and **spec** stages before implementation so product decisions are made with a human, not "vibe'd" by the implementer. Specs can be committed as code. He teaches agents to **verify with computer use** (screenshots, recordings, a Visual proof section on the PR) because reviewers should not have to pull a branch the author never tested. Finally, a **merge-risk** skill scores Alignment, Impact, Verification, Rollback cost, and Error detection, and asks the implementer to mitigate before opening the PR.

The article is also a Warp Factories / Learn-course pitch. Treat Warp-specific YAML and "under a dollar per issue" as author examples, not factory requirements. Course screenshots are labelled as course examples.

## Key learnings (quotes from the article)

> "many teams end up with a black box they don’t trust, or a “slop cannon” producing PRs no one reads."

> "This is how you end up with a slop cannon: agents pumping out changes without human judgment. We need a way to “gate” our implementation agent before it runs wild."

> "As long as you cover a) structured workflows, b) human judgement, and c) verification, you’ll have all the tools you need."

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Scripted stages already planned; triage / questionnaire / plan gate (Phase 1); separate reviewer (Phase 3); PR artefact pack already proposed; risk routing already exists. |
| **Incorporate** | Commit specs on a branch before implementation when the request is ambiguous (Phase 1). Attach fail-then-pass tests and, for UI work, screenshots or browser notes (Phase 3; already a market-scan proposal). Put Impact and Rollback cost headings on PRs, especially Tier 2/3. Keep verification instructions as a project skill, not a Warp dependency. |
| **Inspiration** | YAML blueprint visualizer; Warp merge-risk skill download; computer-use in a vendor VM. E6 and project checks already cover isolation and tests. |
| **Do not incorporate** | Replacing `factory run` with Warp Factories. Auto-merge. A TypeScript-only factory toolchain. |

The 39–12s media in the article were not treated as a separate transcript; the full article text was used.
