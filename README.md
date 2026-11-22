# 🏭 HyperSoftwareFactory

**A software factory for building, verifying, and merging software with AI agents, and a reference architecture for where it is going.**

The factory takes GitHub issues today, and aims to take raw signals (social intake, bugs, requirements, alerts), and produce deployed, verified, monitored software, using Hermes, Claude Code, and GitHub.

> **Status.** Two things live here:
> - **A working factory** in `factory/` and `.claude/`: issue → intake → spec → build → gate → review → approve → merge. It was validated on Binley, a fictional demonstrator used to test the idea: 11 jobs, now closed (the first is written up in the [pilot report](reference/binley/pilot-report-2026-11-21.md)). It has not yet run on a real project.
> - **A target architecture** in `reference/`: signal intake, council gates, deploy, monitoring, and Kaizen. Those parts are not built. The [build plan](reference/build-plan.md) says what exists, what is next, and how to tell each step is done.

---

## The working factory

`factory/` and `.claude/` are the factory as it ran on the Binley Building Society demonstrator, a fictional case used to validate the idea. `/factory run` takes every open issue labelled `factory` through intake → spec → build → gate → review → approve, one PR per issue, with state in `factory/jobs/` and `factory/bin/job` as its only writer.

- **Install into a project:** copy `factory/` and `.claude/` into the target repo, then write the project's checks into `factory/checks.sh` (it fails until you do) and set `protected_paths`, `sensitive_paths` (files that always get the security reviewer), `dev_server` (the command the UI and UX reviewers browse, `{port}` filled in; Next.js by default, drop it if there are no pages), models and prices in `factory/config.json`. Copy `factory/settings.example.json` to `.claude/settings.json` and add your package manager's commands: it allows the factory scripts, denies `gh pr merge`, and blocks hand merges with a hook. The agents read what belongs in the project, its rules, users and design system from its `AGENTS.md` or `CLAUDE.md`. Binley's `checks.sh` and `config.json` are in `reference/binley/` as a worked example.
- **Dashboard:** `cd factory && python -m http.server`, then open http://localhost:8000/dashboard.html. A live board of every job by stage, with gate and reviewer verdicts, cost and time, and each job's files in a drawer.
- **Windows:** the scripts carry patches marked `# binley:` (see `factory/bin/proc.py` and `factory/test_factory.py`). Setup notes are in [`reference/binley/running-the-factory.md`](reference/binley/running-the-factory.md).
- **Evidence so far:** 11 jobs finished on Binley by 22 Nov 2026: ten merged, one rejected at intake. The pilot was merged by hand after a Windows gate fault; after it the factory merged one PR itself, sent one job back for a CHANGES round, and escalated eight to a human, all under the project's always-stop rules. No job failed the gate. This shows the mechanism works, not that it can be trusted: Binley has no production and no users. Only the first job has a written report, the [pilot report](reference/binley/pilot-report-2026-11-21.md); the [build plan](reference/build-plan.md) has the rest of the numbers and the learnings carried forward.

## Roadmap

The objective is one factory that takes signals to deployed, verified, monitored software across real projects, with the operator setting policy. Binley tested whether the idea works; it does, and it is closed. From here the factory earns autonomy one level at a time, on measured jobs on a real project, not on features shipped. Each step below has an exit criterion and a status per task in the [build plan](reference/build-plan.md). Steps gate autonomy, not code: a later step's task may land early when a real job needs it, but a level is not claimed until its step and every step before it have exited.

| Step | Goal | Autonomy | Status |
|---|---|---|---|
| 0 | Close out Binley: harvest its later fixes, neutral agents, template permission rules | – | Tasks done; exits with the first install |
| 1 | Reliable on the first real project: install, protected-path fix, always-stop rules in a script, per-job time and USD caps, branch protection, event log | L1 | Not started on a real project. S1.3 and S1.4 are done in code; Binley's 11 jobs do not count toward the exit |
| 2 | Deterministic backpressure: complexity delta, secret scan and dependency audit in `checks.sh` | L1 | Not started |
| 3 | Verification you can trust: evidence rule, reviewers can't change the branch, spec-only tester, security reviewer exercised | L2 | Landed early: S3.1 (reviewer browser, one shared dev server), S3.2 (evidence rule), S3.6 (reviewers by sensitive path); S3.5 done on Binley |
| 4 | Isolation and concurrency: dedicated clone with no deploy secrets, daily budget, watchdog, `concurrency` 2 then 3 | L2 | Landed early: S4.1 (job lock waits, child processes die with the script) |
| 5 | Risk-tiered merge and deploy: path-based risk floor, LOW merges unattended, HIGH always stops, deploy with rollback | L3 | Not started |
| 6 | Second project, external intake, weekly Kaizen report, councils if the data asks for them | L4 | Not started |

### Now

Task IDs are the build plan's.

- **Close the protected-path gap (S1.9).** `factory/bin/gate` checks modified and deleted files only, so a new file under a protected glob (a new `.github/workflows/*.yml`) passes. The approver caught both cases on 22 Nov; the gate should.
- **Move the always-stop rules into a script (S1.13).** All eight Binley escalations came from a label or a path rule that the approver applied from its prompt.
- **Pick the first real project and install there (S1.12).** See the build plan's open question 1. Every job stops at `approve` for you until S1.9 and S1.13 are in.
- **Then the rest of Step 1:** a seeded gate failure (S1.11), the event log with human-edit, escape and escalation rates (S1.10), per-job time and USD caps (S1.7), the git sign-in script (S1.2), verified prices (S1.6) and branch protection (S1.8).

### Later

Parallel builders within one spec, council gates, Prometheus metrics, microVM isolation, Context7 and Modern Web Guidance are deferred until the data calls for them. The build plan says what would trigger each.

## Contents

| Path | What's in it |
|---|---|
| [`factory/`](factory/) | The working factory: `bin/job` (state machine), `bin/gate`, `bin/route`, `bin/frontier`, `checks.sh`, `config.json`, `settings.example.json`, live `dashboard.html` |
| [`.claude/agents/`](.claude/agents/), [`.claude/hooks/`](.claude/hooks/) | Factory agents: intake, spec-writer, builder, code/security/UI/UX reviewers, approver; a hook that blocks hand merges |
| [`.claude/skills/`](.claude/skills/) | `factory` skill (`/factory run`) plus vetted, pinned skills (to-spec, to-tickets, tdd, deslop, ...) |
| [`reference/binley/`](reference/binley/) | The idea validation, now closed: pilot report, bootstrap prompt, how to run it on Windows |
| [`reference/`](reference/) | Target architecture, build plan, planned integrations |
| [`config/`](config/), [`scripts/`](scripts/) | Central project registry (`projects.yaml`) and its onboarding script |

## Project registry

```bash
pip install -r requirements.txt
python scripts/factory-onboard.py --interactive
```

The script adds a project to [`config/projects.yaml`](config/projects.yaml) and writes draft roadmap files to `onboarding/<slug>/` for you to review and push to the project repo. It pushes nothing itself. The repo check needs an authenticated GitHub CLI (`gh auth login`). The working factory does not read this registry yet; it is installed per project.

## Target architecture

```
SIGNALS ─▶ INTAKE ─▶ TRIAGE ─▶ SPEC ─▶ BUILD ─▶ VERIFY ─▶ DEPLOY ─▶ MONITOR ─▶ LEARN
                       │           │                  │                         │
                    Gate 1      Gate 2             Gate 3                    Weekly
                   (triage)  (architecture)       (deploy)                   Kaizen
```

8 stages, 3 council gates, 1 weekly Kaizen review, 5 security boundaries.

| Document | What it covers |
|---|---|
| [Reference architecture](reference/software-factory-reference-architecture.md) | Stages, gates, verification, security, observability |
| [Build plan](reference/build-plan.md) | What exists, what is next, exit criteria per step |
| [Multi-project architecture](reference/factory-multi-project-architecture.md) | How one factory serves many project repos |
| [Context7](reference/context7-docs-mcp.md), [Modern Web Guidance](reference/modern-web-guidance-google-mwg.md) | Planned build-floor integrations |

## How The Target Is Designed To Work

### Signal intake
Social links, bug reports, customer feedback, and alerts enter a triage queue and are routed to a project. External content is untrusted: it is summarised by a tool-less model call before any agent that can write code sees it.

### Council gates (2 tiers)
- **Fast Council** (Chair only) — triage and medium-risk verdicts
- **Full Council** (Chair, Strategist, Pragmatist, Builder) — architecture review

Council verdicts are advisory. High-risk changes always need the operator's approval.

### Build floor
An approved spec is built by Claude Code in an isolated worktree, following a playbook per task type (bug → reproduce → investigate → fix → verify; feature → spec → test → implement), with at most 3 review-fix cycles. Parallel subagents come later and only on disjoint modules.

### Independent verification
Verifiers run in a separate job with read-only tokens, so they cannot modify the code they review:
- **Tester** — writes tests from the spec only, never from the implementation
- **Code Reviewer** — standards + spec compliance
- **Anti-Slop Lint** — lint rules + complexity delta
- **Security Scanner** — supply chain, credentials, egress
- **Behavioural Verifier** — runs the change as a user would

### Security boundaries

| Boundary | What it blocks |
|---|---|
| **Isolation** | Agent can't touch the host or other projects |
| **Egress** | Default-deny, allowlist only |
| **Supply chain** | Unapproved package hosts denied |
| **Credentials** | Real secrets never enter the agent sandbox |
| **Budget** | Hard USD/token/time cap per run, pinned model versions |

### Observability and Kaizen
Every stage transition appends one event row. A weekly review reads failures, cost, cycle time, and escape rate from that log and mints improvement items.

## Hard Constraints

1. **No unreviewed output** — every PR is reviewed by at least one independent verifier
2. **Evidence-based verification** — a bare "PASS" is treated as INCONCLUSIVE
3. **Anti-slop gate** — a complexity increase above 50% on touched files blocks the PR for architecture review
4. **Max 3 review-fix loops** — prevents infinite agent cycles
5. **All secrets stay outside the sandbox**

The target is to enforce these by the platform (branch protection, token scopes, runner budgets), not by agent instructions. The working factory enforces 1, 2 and 4 in its scripts today.

## Autonomy Levels

| Level | What runs without you | Earned by |
|---|---|---|
| **L1** | Issue to approved PR; you merge | Build plan Step 1 exit |
| **L2** | As L1, with reviewers you have measured | Step 3 exit |
| **L3** | LOW-tier merge and deploy | Step 5 exit |
| **L4** | Signal to deploy for LOW tier; you set policy | Step 6 exit, sustained for four weeks |

The working factory has the machinery for L2 and an approver that can merge. Levels are per project and earned on a real one, so none is earned yet: Binley showed the mechanism works, including one unattended merge, but no real project has run a job.

## Planned Integrations

None of these is wired in yet, and their claims are the vendors' own.

| Tool | Stage | What it provides |
|---|---|---|
| **Context7** (Upstash) | Build | Current, version-specific library docs via MCP |
| **Modern Web Guidance** (Google Chrome) | Build + Verify | Web platform best practices, Baseline-aware |
| **Crawl4AI** | Intake research | JS-rendered page extraction |

## Development

```bash
python scripts/test_factory_onboard.py   # self-check for the onboarding script
python factory/test_factory.py           # factory script checks; run inside a Node project after `npm ci`
```

## Contributing

1. Read the [reference architecture](reference/software-factory-reference-architecture.md) and the [build plan](reference/build-plan.md)
2. Open an issue to discuss your proposed change
3. Submit a PR

## Origin

Synthesised from public material on agentic software development: Factory.ai, Claude Code, Islo's security architecture, Matt Pocock's skills, Lauren Tan's Poteto Mode, and Dexter Horthy's talk on software factories.

**License:** [MIT](LICENSE), except `factory/`, `.claude/agents/` and `.claude/skills/factory/`, which are GPLv3 (see [`factory/LICENSE`](factory/LICENSE); from zazencodes-season-3 `src/software-factory-claude-code-v2`, with local patches). Vendored skills keep their own MIT licences in `.claude/skills/`.
