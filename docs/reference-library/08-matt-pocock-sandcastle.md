# 08 Matt Pocock — Sandcastle (open-source agent sandbox runner)

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Author:** Matt Pocock ([@mattpocockuk](https://x.com/mattpocockuk)), AI Hero / Total TypeScript. Verified account.
- **X post:** 29 April 2026, 15:10 UTC (16:10 UK time, BST). https://x.com/mattpocockuk/status/2049506712801935611
- **Post text:** "I built my own software factory, and I open-sourced it. It's called Sandcastle. Here's how to use it:" plus a video. The `t.co` link only redirects back to the same video; there was no separate docs URL on the post.
- **Video:** about 11 minutes 25 seconds (6,848,00 ms). **Not watched** in this review. Claims about current behaviour are taken from official docs and the GitHub README as fetched on 25 November 2026, which may have moved on since the April video.
- **Official docs:** https://www.aihero.dev/sandcastle
- **Repo:** https://github.com/mattpocock/sandcastle — MIT, TypeScript, `sandcastle.run()`. API snapshot 25 November 2026 was not re-polled for stars here; use the docs/README as the feature source.
- **Later colour only (not treated as shipped v1):** a 4 November 2026 LinkedIn note by Pocock describing a planned v1 (built-in harnesses, Inngest/Trigger.dev templates, HITL over Slack/Discord, skills as `CodeReview()` / `ImplementSpec()`). Third-party write-ups also said those v1 items were a plan, not a release. Do not treat them as current features.
- **Added:** 25 November 2026. Nothing was posted or replied to on X.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Phase 2 (E6 isolation, worktrees); agent roster (builder in a sandbox); LLM provider spec (agent-provider agnostic: `claudeCode()`, `codex()`, etc.). Not a Phase 0 merge-policy change.

**Scores:** Relevance M–H (isolation pattern). Actionability M (we already have worktrees and a container/allowlist). Novelty L–M versus the existing E6 plan and entry 04 (OpenHands / worktree tools).

**Dedupe:** Overlaps E6, Sandcastle-like worktree tools in the market scan, and Piotr's isolated pods. Not a substitute for the control plane.

**What was and was not covered:** Post text and official docs/README were read. The April how-to video was not watched. If the operator needs the video itself, it would have to be supplied as a file.

## Summary

Sandcastle is a TypeScript library for running AI coding agents in isolated sandboxes. You call `sandcastle.run()`; it starts an agent (Claude Code, Codex, and others via a provider function) inside a sandbox, applies a branch strategy, and can merge commits back according to that strategy.

Branch strategies documented today: **head** (write to the current workdir), **merge-to-head** (temporary worktree branch, merge back, keep the branch on failed merge), and **named branch**. Sandbox providers include OS process sandboxes (Bubblewrap on Linux/WSL2, Seatbelt on macOS), Docker/Podman, and cloud providers (Daytona, E2B, Fly.io Sprites, Modal, Vercel). It is provider-agnostic by design.

This is a **harness for isolated agent runs**, not a full factory control plane (no issue triage, no operator merge gate, no F3 curator). The April post called it a "software factory"; the current docs describe a sandbox orchestrator. Some documented strategies merge back automatically — that must not replace the operator's merge rule.

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Isolated worktrees and a container/allowlist are already in the plan (E6). Claude Code remains the default harness in the LLM spec. |
| **Incorporate** | Optionally study Sandcastle's branch-strategy and provider-agnostic sandbox APIs as a **library**, not a replacement for `factory run`. Prefer strategies that leave a PR for the operator over silent merge-to-head on `main`. |
| **Inspiration** | Planned v1 HITL and skill-as-function ideas, if and when they ship. |
| **Do not incorporate** | Replacing the Python factory runner with a TypeScript library. Auto-merging agent commits to the main branch. Installing cloud sandbox vendors without the operator's yes. |
