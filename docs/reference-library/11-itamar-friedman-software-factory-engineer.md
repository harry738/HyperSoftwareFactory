# 11 Itamar Friedman — Software Factory Engineer: Job Description

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Author:** Itamar Friedman ([@itamar_mar](https://x.com/itamar_mar)), CEO and co-founder of Qodo.
- **Posted:** 5 November 2026, 14:54 UTC (14:54 UK time, Europe/London)
- **X post:** https://x.com/itamar_mar/status/2118356299612033305
- **X Article used here:** "Software Factory Engineer: Job Description" — https://x.com/i/article/2118356086592971130
- **Also linked, not fully ingested:** a 26 October 2026 LinkedIn article "Path to L4: The Autonomous Software Factory." Claims in this note come from the X Article, not that LinkedIn piece.
- **Added:** 25 November 2026. Nothing was posted or replied to on X.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Agent roster (who owns architecture, knowledge, verification, policy, production feedback, economics); Phase 3 (independent verification — "The author should not self-approve"); Phase 1 (autonomy as executable policy, plan gate); Phase 4 (F3 knowledge, F6 production feedback, event-log / cost-per-accepted-change). Risk tiers already exist; L4 autonomy is **not** a near-term factory goal.

**Scores:** Relevance H. Actionability H (role framing for the roster and metrics). Novelty M (formalises rules we already have).

**Dedupe:** Overlaps Holmes (gates, verification), Chase / F3 (knowledge with provenance), Agent Baseline (policy as executable constraints), Gumloop (factory is the product). Complements the roster rather than replacing it.

## Summary

Friedman describes a **Software Factory Engineer** at "L4 Autonomous Software Factory": the factory can independently execute, verify and deliver **defined classes of changes within boundaries**, and must escalate when stakes or uncertainty exceed delegated authority. The primary artefact is **the factory itself** — designed, tested, observed and maintained.

Six areas of ownership:

1. **Architecture and orchestration** — how work is classified, routed, planned, executed, verified, integrated, documented.
2. **Context and organizational knowledge** — skills, conventions, system context, operational knowledge, with **provenance and owner authority** (maps cleanly to Chase's curator, not the builder).
3. **Independent verification** — static analysis, tests, security, policy, review. Quote: **"The author should not self-approve."**
4. **Autonomy boundaries as executable policies** — what may proceed automatically, what needs human approval, what is forbidden. Written so they can be inspected and updated.
5. **Production feedback** — "The factory’s responsibility does not end at merge." Observability, incidents, user feedback should return as work and (when appropriate) as knowledge updates.
6. **Factory performance and economics** — cost per accepted change, escaped defects, time-to-fix, human burden. Output volume is not success.

The article also describes the engineer as a partner to leadership on risk appetite, and has a tongue-in-cheek "bonus" section (e.g. DeepSeek Harness). Do not treat jokes as requirements.

This is a role and bar, not a toolchain pitch. L4 in the article is a destination, not something HyperSoftwareFactory should claim now.

## Key learnings (quotes)

> "The author should not self-approve."

> "The factory’s responsibility does not end at merge."

> "output volume is not a success metric."

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Builder is not the merger; Security and Test/QA and the fresh-context reviewer are separate; risk policy is written (Always / Ask First / Never; low/med/high); F3 and F6 already point past merge; event log and budgets already planned. |
| **Incorporate** | Name cost per **accepted** change, escaped defects, and human burden in later dashboard tiles (output volume is not the goal). Treat knowledge as having an owner and a source, not just a file the builder appends. Keep escalation when uncertainty exceeds the delegated tier. |
| **Inspiration** | The Software Factory Engineer as a named job title for the operator plus the roster. The unread LinkedIn "Path to L4" article. |
| **Do not incorporate** | Treating L4 autonomy as a near-term goal. Letting the authoring agent approve its own work. Using volume of PRs as the success metric. |
