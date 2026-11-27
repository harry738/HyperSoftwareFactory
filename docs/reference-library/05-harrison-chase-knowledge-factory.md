# 05 Harrison Chase — How to build a knowledge factory

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Title:** How to build a knowledge factory
- **Author:** Harrison Chase ([@hwchase17](https://x.com/hwchase17)), LangChain. Verified account.
- **Posted:** 21 November 2026, 16:40 UTC (16:40 UK time, Europe/London)
- **X post:** https://x.com/hwchase17/status/2124181216719151585
- **Linked X Article (full text used below):** https://x.com/i/article/2124180107669766144
- **Added to this library:** 25 November 2026 (Europe/London)
- **Ingestion:** tags, scores, dedupe, review date below. Nothing was posted, liked, or replied to on X.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Phase 4 (F3 learnings); Phase 1 (skills / AGENTS.md); agent roster (Research / F4 watcher vs a separate curator, not the builder); untrusted intake (F4/F8). Risk tiers: not a merge-policy change.

**Scores:** Relevance H. Actionability H (sharpens F3 without new official IDs). Novelty M (overlaps Horthy compound lessons / planned F3).

**Dedupe:** Complements entry 01 (Horthy learnings in-repo) and planned F3. Not a duplicate of 01. Later overlap with Gumloop "remember the judgment call" and Itamar's organizational knowledge (entries 13 and 11).

## Summary

Chase argues that making AI work inside a company is less about better models or "just more context" and more about **knowledge**: how the company works, its operating standards, where data lives, and how it is accessed. That knowledge is often tacit and scattered. A **knowledge factory** is the system that collects, curates and maintains a representation of it for agents.

He distinguishes context (what an agent has for one task) from knowledge (reusable understanding that can become context later). He maps this onto software factories: the best engineers should build the factory; agents do more of the work. For general knowledge work, the scarce resource is the same kind of factory for tacit knowledge.

Three kinds of knowledge: **skills** (procedures), **domain knowledge** (slow-changing facts and policies), and **data access guidance** (how to query systems of record — do not keep a separate stale copy of quickly changing data).

Three factory pieces: (1) agents **flag** missing or wrong knowledge; (2) a separate **curator** agent, on a cadence, updates the store from raw sources, traces, and flags — the doing-agents should not maintain it themselves, or it becomes contradictory; (3) **storage** can be skills in GitHub, a wiki, OKF / Context Hub, or a graph — do not be overly prescriptive about format yet.

The goal is not to document everything first. Start with one recurring workflow; doing the work reveals gaps; closing them improves the next run. Figures about LangChain's own GTM / LangSmith Engine use are the author's account of their internal systems, not a product we must adopt.

## Key learnings (quotes from the X Article)

> "In order to make AI work for your company, the missing bit is not better models, it’s not just more context - it’s better knowledge."

> "Asking agents - who are mainly trying to accomplish their own goals - to properly update and maintain this knowledge will cause it to become unruly and full of contradictions. Rather - you will want a curator agent that runs in the background, on some cadence, to update this knowledge."

> "The goal isn’t to document everything before agents can start working. It’s to build a system where doing the work reveals what knowledge is missing, and resolving those gaps makes future work better. Start with one recurring workflow."

## What applies to HyperSoftwareFactory (review bar)

| Bar | Mapping (proposals only; no new E/F numbers) |
|---|---|
| **Direct match** | Planned **F3** weekly learnings; skills already live in the repo; the event log is a trace source; the builder is already separated from reviewers; the operator merges. E1.6 (first real job) is the "one recurring workflow." |
| **Incorporate** | Give agents a structured way to **flag** missing or wrong knowledge. A **separate curator** (not the builder) periodically reads flags and the event log and opens a learnings or skills PR for the **operator** to merge. Do not let implementers write the knowledge store. Prefer access guidance over copying live data (relevant to Context7 / F4). |
| **Inspiration only** | LangSmith Context Hub, OKF, Slack/Notion as raw sources. Not a proposal to buy those products. |
| **Do not incorporate** | A curator that merges its own updates. |

`principles.md` is still deferred until the operator says the reference set is complete.
