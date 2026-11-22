# Competitor list — the factory itself

The active list of systems that run coding agents unattended. The weekly Kaizen market watch (build plan F4) keeps it current through a PR: it adds entries, retires them, and updates the notes. Feature detail is in the [feature comparison](feature-comparison.md).

Last checked: 2026-11-22. Every entry was read from the system's own docs or repo on that date.

| System | Kind | How it is consumed | Where to watch | Why it matters to us |
|---|---|---|---|---|
| OpenAI Symphony | Open source (Apache-2.0), engineering preview | Central daemon that polls a tracker and gives each issue its own workspace | https://github.com/openai/symphony | Closest published design for a script-driven loop: stall and turn timeouts, backoff, reconcile from the tracker |
| agent-orchestrator | Open source (Apache-2.0) | Central daemon with worktrees and a Windows installer | https://github.com/OrchestratorInc/agent-orchestrator | Routes CI failures and review comments back to the agent; derives status from an append-only log |
| Gas Town and Beads | Open source (MIT) | Central daemon and CLI managing several repos | https://github.com/gastownhall/gastown | Merge queue that re-verifies; a dependency-aware work tracker with persistent memory |
| OpenHands | Open source (MIT), plus a hosted cloud | Docker app; a container per conversation | https://github.com/OpenHands/OpenHands | Container isolation, typed event stream, chat and schedule triggers |
| claude-code-action | Open source (MIT) | GitHub Action per repo; the runner is the isolation | https://github.com/anthropics/claude-code-action | The CI-hosted alternative to a central factory |
| StrongDM Attractor | Spec only (Apache-2.0) | A pipeline described as a graph and walked deterministically | https://github.com/strongdm/attractor | Checkpoint after every node; goal gates; holdout scenarios in its factory write-up |
| Devin (Cognition) | Commercial, hosted | Cloud VM per session; web, chat, API | https://docs.devin.ai | Per-session spend cap, recorded test runs as proof, reacts to PR review |
| GitHub Copilot cloud agent | Commercial, hosted | Cloud sandbox or Actions runner | https://docs.github.com/en/copilot | Deterministic security checks on its own output; the agent may not merge its own PR |
| OpenAI Codex cloud | Commercial, hosted | Cloud workspace per task | https://learn.chatgpt.com/docs/cloud | Setup scripts and network policy per environment |
| Cursor cloud agents | Commercial, hosted | Isolated VM per agent | https://cursor.com/docs/cloud-agent | Automations with memory; review rules learned from merged and closed PRs |
| Factory Droids | Commercial | CLI, app and managed computer | https://docs.factory.com | Repo readiness score before work starts |
| Claude Code cloud sessions and scheduled tasks | Commercial, hosted | Managed VM, or self-hosted | https://code.claude.com/docs/en/claude-code-on-the-web | Auto-fix on PR review and CI; network levels; the same engine we build on |
| Stripe Minions | Internal, described publicly | Central service with pre-warmed devboxes | https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents | Largest public deployment: deterministic steps around agent loops, two CI rounds, a person reviews every PR |

## Retired

| System | When | Note |
|---|---|---|
| Google Jules | Read-only from 11 Nov 2026, shut down 31 Dec 2026 | Its changelog points users to a successor product, not yet reviewed |
| vibe-kanban | 2026 | Its README says the project is sunsetting |
