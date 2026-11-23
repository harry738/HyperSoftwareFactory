# Feature comparison — systems that run coding agents unattended

A snapshot taken on 2026-11-22, used to check the [build plan](build-plan.md). The living list of systems is [competitors.md](competitors.md).

**How to read it.** Every cell comes from the system's own docs, README or official blog, read on that date by a research pass. Nothing was tested hands-on, and vendor claims were not independently verified. **Y** yes, **P** partial, **N** the docs or spec say no, **?** not verified. "Ours" is what the build plan commits to, most of which is not built yet.

## What it changed in the plan

| Common feature the plan lacked | Systems that have it | What the plan does |
|---|---|---|
| Setup script or cached environment per project | 9 | Added: a `setup.sh` per project and a shared package cache (E1.5) |
| Steering a run while it is in progress | 9 | Not building. Feedback goes in between rounds; the largest deployment omits it on purpose |
| Start a run from chat | 8 | Through Hermes (F2) |
| Start a run on a schedule | 8 | Added to the engine track (E5.3) |
| React to human review comments on its own PR | 8 | Added: the feedback loop (E2.4) |
| Network allowlist for the agent's machine | 7, every commercial one | Added (E6.1) |
| Start a run by API or webhook | 7 | Not building. Labelling an issue is the API |
| React to CI failures on its own PR | 6 | Added: the feedback loop (E2.4) |
| Memory across tasks | 5 | Added as a curated learnings file per project (F3) |
| Mobile or push notifications | 5 | Through Hermes (F2) |

Also taken: stall detection and retry with backoff (Symphony), a checkpoint after every stage (Attractor), a readiness check at onboarding (Factory), evidence on the PR (Devin, Cursor, Symphony), follow-up issues for out-of-scope findings (Symphony), and holdout tests the builder never sees (StrongDM's factory write-up).

## Where the plan is ahead

- **Risk tiers and routing by surface and path.** No system documents risk tiers. Copilot forbids its agent from approving or merging its own PR; Stripe sends everything to human review.
- **Specialist reviewers that cannot write and must cite evidence.** The others document a single review agent, sometimes with a separate security pass.
- **Per-stage time, turn and cost caps, with a daily budget.** Only Devin documents a per-session spend cap.
- **Gate config kept outside the repo, with always-stop rules by label and path.** Most keep agent config inside the repo.
- **Holdout tests, and deploy with rollback (both planned).** No product documents deploy or rollback.

## Where the plan is alone

No system lets agents approve and merge their own work without heavy mechanical checks. The Dev council's merge power has no public precedent, which is why the plan starts it in shadow and grades every verdict.

## Matrix 1 — open source and self-hosted

Sym = OpenAI Symphony, AO = agent-orchestrator, GT = Gas Town and Beads, OH = OpenHands (including its cloud), CCA = claude-code-action, Att = StrongDM Attractor (a spec).

| Feature | Sym | AO | GT | OH | CCA | Att | Ours |
|---|---|---|---|---|---|---|---|
| Trigger: issue label, assignment or state | Y | P | ? | Y | Y | N | Y |
| Trigger: chat | N | ? | ? | Y | N | N | Via Hermes |
| Trigger: schedule | N | P | ? | Y | Y | N | Y |
| Trigger: API or webhook | N | ? | ? | Y | Y | P | N |
| Trigger: CI failure | N | ? | ? | ? | P | N | Y, on its own PR |
| Trigger: alerts or monitoring | N | ? | ? | P | ? | N | Later |
| Trigger: PR comment mention | N | ? | ? | Y | Y | N | N |
| Repo onboarding flow | P | ? | Y | Y | Y | N | Y |
| Setup script or snapshot | Y | ? | ? | Y | P | N | Y |
| Secrets management | P | ? | ? | Y | Y | N | P |
| Network egress policy | N | ? | ? | ? | ? | N | Y |
| Readiness or repo-health check | N | ? | P | ? | N | N | Y |
| Isolation | per-issue directory | worktree, hosted sandbox | worktree | Docker or cloud sandbox | Actions runner | unspecified | worktree in a container |
| Parallel tasks | Y | Y | Y | Y | P | P | Y |
| Resume or steer mid-run | N | Y | Y | Y | P | Y | Resume only |
| Plan or sub-tasks shown | N | Y | Y | ? | Y | P | P |
| Multi-model or agent-agnostic | N | Y | Y | Y | P | Y | Council seats only |
| Reacts to CI failures on its PR | P | Y | P | ? | P | N | Y |
| Reacts to human review comments | P | Y | ? | P | P | N | Y |
| Iterates until checks pass | P | Y | P | Y | ? | Y | Y |
| Iteration limits | Y | ? | ? | P | Y | Y | Y |
| Independent review agents | N | Y | ? | Y | Y | P | Y |
| Tests separate from implementation | N | ? | ? | ? | ? | P | Later |
| Evidence artifacts on the PR | Y | ? | ? | ? | P | P | Text first |
| Security scanning | N | ? | ? | ? | P | N | P |
| Auto-merge | Y | P | Y | ? | ? | N | Earned, LOW tier |
| Merge queue | N | ? | Y | ? | ? | N | N |
| Risk tiers | N | ? | ? | ? | P | N | Y |
| Deploy and rollback | N | ? | ? | ? | ? | N | Later |
| Per-task time limit | Y | ? | P | ? | ? | Y | Y |
| Per-task cost cap | N | ? | ? | N | P | N | Y |
| Account-level spend controls | N | ? | ? | Y | ? | N | Y |
| Audit log | P | ? | P | Y | P | P | Y |
| Approval policies | P | Y | P | P | Y | Y | Y |
| Persistent memory | N | ? | Y | P | ? | N | Curated file |
| Rules files | Y | P | P | Y | P | P | Y |
| Feedback captured from reviews | N | ? | ? | ? | ? | N | Y |
| Dashboard | P | Y | Y | Y | N | P | Y |
| Per-task timeline or trace | P | Y | Y | Y | P | Y | Y |
| Analytics | N | ? | P | P | N | N | Weekly report |
| Notifications | N | Y | P | P | P | N | Via Hermes |
| Interfaces | optional HTTP dashboard | CLI, desktop, mobile | CLI, TUI, web | web, API, chat | GitHub UI | library | CLI, static web page |

## Matrix 2 — commercial and hosted

Dev = Devin, Cop = GitHub Copilot cloud agent, Cdx = OpenAI Codex cloud, Cur = Cursor cloud agents, Fac = Factory Droids, CC = Claude Code cloud sessions and scheduled tasks, Str = Stripe Minions (internal, from its public write-up).

| Feature | Dev | Cop | Cdx | Cur | Fac | CC | Str |
|---|---|---|---|---|---|---|---|
| Trigger: issue label or assignment | Y | Y | P | Y | Y | Y | P |
| Trigger: chat | Y | Y | Y | Y | Y | Y | Y |
| Trigger: schedule | Y | Y | Y | Y | Y | Y | ? |
| Trigger: API or webhook | Y | Y | P | Y | Y | Y | P |
| Trigger: CI failure | Y | Y | ? | Y | P | P | Y |
| Trigger: alerts or monitoring | Y | P | ? | Y | Y | P | ? |
| Trigger: PR comment mention | Y | Y | P | Y | ? | P | ? |
| Repo onboarding flow | Y | P | Y | Y | Y | Y | ? |
| Setup script or snapshot | Y | Y | Y | Y | Y | Y | Y |
| Secrets management | Y | ? | Y | Y | P | Y | ? |
| Network egress policy | Y | Y | Y | Y | Y | Y | Y |
| Readiness or repo-health check | ? | ? | ? | ? | Y | ? | ? |
| Isolation | cloud VM | cloud sandbox or Actions runner | cloud workspace per task | isolated VM | OS sandbox or managed computer | managed VM or self-hosted | devbox |
| Parallel tasks | Y | ? | P | Y | P | Y | Y |
| Resume or steer mid-run | Y | Y | Y | Y | Y | Y | N |
| Plan or sub-tasks shown | P | ? | ? | ? | Y | P | ? |
| Multi-model or agent-agnostic | ? | P | ? | Y | Y | N | ? |
| Reacts to CI failures on its PR | Y | Y | ? | Y | P | Y | Y |
| Reacts to human review comments | Y | Y | ? | Y | ? | Y | Y |
| Iterates until checks pass | P | P | ? | P | P | P | Y |
| Iteration limits | P | P | ? | Y | ? | ? | Y |
| Independent review agents | Y | Y | Y | Y | Y | Y | ? |
| Tests separate from implementation | P | ? | ? | ? | P | ? | ? |
| Evidence artifacts on the PR | Y | P | ? | Y | ? | ? | ? |
| Security scanning | P | Y | Y | P | Y | ? | ? |
| Auto-merge | P | P | ? | ? | ? | ? | N |
| Merge queue | ? | ? | ? | ? | ? | ? | ? |
| Risk tiers | ? | ? | ? | ? | P | ? | ? |
| Deploy and rollback | ? | ? | ? | ? | ? | ? | ? |
| Per-task time limit | P | Y | ? | ? | ? | P | ? |
| Per-task cost cap | Y | ? | ? | ? | ? | ? | ? |
| Account-level spend controls | Y | ? | P | Y | Y | P | ? |
| Audit log | ? | Y | P | Y | Y | ? | ? |
| Approval policies | Y | Y | P | P | Y | Y | P |
| Persistent memory | Y | Y | P | Y | ? | ? | ? |
| Rules files | Y | Y | Y | Y | Y | Y | Y |
| Feedback captured from reviews | P | P | ? | Y | ? | ? | ? |
| Dashboard | Y | Y | Y | Y | Y | Y | Y |
| Per-task timeline or trace | Y | Y | P | Y | P | Y | Y |
| Analytics | P | Y | P | P | Y | ? | ? |
| Notifications | Y | ? | P | Y | ? | ? | P |
| Interfaces | web, CLI, API, chat | web, mobile, IDE, CLI, API | web, desktop, mobile, IDE, CLI | web, mobile, IDE, API | CLI, app, IDE, API | web, mobile, desktop, CLI | chat, CLI, web |

## Differentiators considered

| Idea | Who has it | Decision |
|---|---|---|
| Repo readiness score with automatic fixes | Factory | A checklist at onboarding (E1.2); no score, no auto-fix |
| Recorded test runs as proof | Devin, Cursor, Symphony | Text evidence on the PR first (E4.3); images when there is somewhere to host them |
| Bisecting merge queue | Gas Town | Not building; the merge step already re-checks against the latest base |
| Review rules learned from merged and closed PRs | Cursor | The curated learnings file (F3) is the first step |
| Deterministic security checks before the PR | Copilot | Per project, in its `checks.sh`; the readiness checklist reports the gap |
| Preflight filter and a rate limit per automation | Devin | Covered by the intake stage, concurrency and the daily budget |
| Context gathered by code before the run, and automatic fixes for known CI failures | Stripe | Not yet; revisit when the event log shows repeated failures |
| Agents file follow-up tickets for out-of-scope work | Symphony | Added (E4.4) |

## Published outcome numbers

All vendor-reported unless noted.

- **Stripe:** over 1,300 agent-written PRs merged a week, every one reviewed by a person.
- **Cognition:** Devin's PR merge rate was 67%, up from 34% a year earlier.
- **Cursor:** cloud agents wrote more than half of the PRs merged to its own codebase by July 2026.
- **OpenAI:** landed PRs up 500% in three weeks "among some teams" using Symphony.
- **StrongDM:** a benchmark of $1,000 of tokens a day per engineer, with code neither written nor reviewed by people.
- No vendor published a figure for review burden.

## Sources

- OpenAI Symphony: https://github.com/openai/symphony and https://openai.com/index/open-source-codex-orchestration-symphony/
- agent-orchestrator: https://github.com/OrchestratorInc/agent-orchestrator
- Gas Town and Beads: https://github.com/gastownhall/gastown and https://github.com/gastownhall/beads
- OpenHands: https://docs.openhands.dev
- claude-code-action: https://github.com/anthropics/claude-code-action
- StrongDM Attractor and factory write-up: https://github.com/strongdm/attractor and https://factory.strongdm.ai/
- Devin: https://docs.devin.ai and https://cognition.com/blog/devin-annual-performance-review-2025
- GitHub Copilot cloud agent: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent
- OpenAI Codex cloud: https://learn.chatgpt.com/docs/cloud
- Cursor: https://cursor.com/docs/cloud-agent, https://cursor.com/docs/bugbot and https://cursor.com/blog/cloud-agent-environment
- Factory: https://docs.factory.com and https://docs.factory.com/agent-readiness/overview.md
- Claude Code: https://code.claude.com/docs/en/claude-code-on-the-web, https://code.claude.com/docs/en/headless and https://code.claude.com/docs/en/sandboxing
- Stripe Minions: https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents and https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2
- Published practice: https://www.anthropic.com/engineering/building-effective-agents, https://openai.com/index/harness-engineering/, https://www.humanlayer.dev/blog/12-factor-agents and https://dora.dev/guides/dora-metrics/
