# 🏭 HyperSoftwareFactory

**A reference architecture for building, verifying, and deploying software with AI agents — across multiple projects.**

The factory takes raw signals (social intake, bugs, requirements, alerts) and aims to produce deployed, verified, monitored software, using Hermes, Claude Code, and GitHub.

> **Status: design stage.** This repo holds the architecture, a build plan, a project registry, and an onboarding script. The pipeline itself is not built yet. The [build plan](reference/build-plan.md) says what to build, in what order, and how to tell each step is done.

---

## Quick Start

```bash
git clone https://github.com/harry738/HyperSoftwareFactory.git
cd HyperSoftwareFactory
pip install -r requirements.txt

# Register a project with the factory
python scripts/factory-onboard.py --interactive
```

The script adds the project to [`config/projects.yaml`](config/projects.yaml) and writes draft roadmap files to `onboarding/<slug>/` for you to review and push to the project repo. It pushes nothing itself. The repo check needs an authenticated GitHub CLI (`gh auth login`).

## Architecture

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
| [Build plan](reference/build-plan.md) | Walking-skeleton sequence with exit criteria per step |
| [Multi-project architecture](reference/factory-multi-project-architecture.md) | How one factory serves many project repos |
| [Context7](reference/context7-docs-mcp.md), [Modern Web Guidance](reference/modern-web-guidance-google-mwg.md) | Planned build-floor integrations |

## How It Is Designed To Work

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

These are enforced by the platform (branch protection, token scopes, runner budgets), not by agent instructions.

## Autonomy Levels

| Level | What runs without you | Earned by |
|---|---|---|
| **L1** | Build to PR; you review every PR | Build plan Step 1 |
| **L2** | Build + checks + verifiers | Step 3 |
| **L3** | Low-risk merge and deploy | Step 5 |
| **L4** | Intake to deploy for low-risk work; you set policy | Step 6 |

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
```

## Contributing

1. Read the [reference architecture](reference/software-factory-reference-architecture.md) and the [build plan](reference/build-plan.md)
2. Open an issue to discuss your proposed change
3. Submit a PR

## Origin

Synthesised from public material on agentic software development: Factory.ai, Claude Code, Islo's security architecture, Matt Pocock's skills, Lauren Tan's Poteto Mode, and Dexter Horthy's talk on software factories.

**License:** [MIT](LICENSE)
