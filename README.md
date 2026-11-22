# 🏭 Software Factory

**Build, verify, and deploy software autonomously — across multiple projects.**

The Software Factory is an end-to-end automated pipeline that takes raw signals (social intake, bugs, requirements, alerts) and produces deployed, verified, monitored software. It runs on our existing toolchain: Hermes, Claude Code, Buzz relay, GitHub, Docker.

---

## Quick Start

```bash
# Add a new project to the factory
python3 scripts/factory-onboard.py --interactive

# Then tell the factory:
# "run intake for <project-name>"
```

## Core Architecture

```
SIGNALS ─▶ INTAKE ─▶ SPEC ─▶ BUILD ─▶ VERIFY ─▶ DEPLOY ─▶ MONITOR ─▶ LEARN
                │          │         │          │          │            │
            Gate 1      Gate 2    Build    Gate 3     Metrics      Kaizen
           (Council)  (Council)  Floor   (Council)  Dashboard     Feedback
```

[Read the full reference architecture →](reference/software-factory-reference-architecture.md)

## Contents

| Directory | What's in it |
|---|---|
| [`reference/`](reference/) | Full architecture docs, multi-project setup, integrations |
| [`config/`](config/) | Central project registry (`projects.yaml`) |
| [`scripts/`](scripts/) | Onboarding wizard, orchestration tools |
| [`README.md`](README.md) | This file — entry point for new readers |

## Key Documents

- **[Reference Architecture](reference/software-factory-reference-architecture.md)** — Complete design: 7 stages, 4 council gates, 5 security boundaries, independent verification, observability, 6-phase build plan
- **[Multi-Project Architecture](reference/factory-multi-project-architecture.md)** — How HyperAISystemsOS orchestrates multiple GitHub repos (HTS, propInfo, etc.) from one config
- **[Context7 Integration](reference/context7-docs-mcp.md)** — Current, version-specific library documentation for build agents
- **[Modern Web Guidance (MWG)](reference/modern-web-guidance-google-mwg.md)** — Google Chrome's web best practices skill pack (Baseline-aware, 100+ guides)

## How It Works

### 1. Signal Intake
Social links, bug reports, customer feedback, and alerts enter through a triage queue. Content is classified (trading / startup / bug / feature) and routed to the appropriate project.

### 2. Spec & Council Gates
Raw signals are triaged by the Product Council (4 LLMs: Chair, Strategist, Pragmatist, Builder) at two gates:
- **Gate 1 (Fast)** — should we build this? 2 min verdict
- **Gate 2 (Full)** — does the architecture hold? 10 min verdict

### 3. Build Floor
Approved specs decompose into parallel Claude Code subagents. Each subagent:
- Loads **Context7** for current library docs
- Consults **Modern Web Guidance** for web best practices
- Follows Poteto Mode playbooks (bug/feature/refactor)
- Runs in isolated worktree, max 3 review-fix cycles

### 4. Independent Verification
Structural separation: testers write tests from spec only (never see implementation), reviewers have read-only permissions (physically cannot modify code), security scans check supply chain and credentials.

### 5. Deployment Gates (by risk)
- **Low** (docs, config, tests) → auto-merge
- **Medium** (new features) → Fast Council
- **High** (money path, auth, guards) → Full Council

### 6. Observability
Every stage emits structured events to `factory_events` (Postgres). Prometheus metrics track: stage durations, LLM cost per RM, cycle time, agent utilization, code complexity deltas. Dashboard shows all projects in one view.

### 7. Kaizen Feedback Loop
Weekly council reviews: build failures, deploy incidents, cost data, cycle times. Systemic issues mint new RM items.

## Project Configuration

Each project is registered in [`config/projects.yaml`](config/projects.yaml):

```yaml
projects:
  hts:
    name: "Hyper Trading System"
    repo: "harry738/hyper-trading-system"
    roadmap: "docs/product/roadmap.yaml"
    inbox: "docs/product/roadmap-inbox/"
    council_enabled: true
    sprint_cadence: weekly
    alert_channel: "telegram:[YOUR_TELEGRAM_CHAT_ID]"
```

Add new projects with:

```bash
python3 scripts/factory-onboard.py --interactive
```

## Security Boundaries

| Boundary | What it blocks |
|---|---|
| **Isolation** | Agent can't touch host or other tenants |
| **Egress** | Default-deny gateway, allowlist only |
| **Supply chain** | Read-only package registries |
| **Credentials** | Placeholder in sandbox, gateway injects real key |
| **Budget** | Hard USD/token/time per run |

## Hard Constraints

1. No unreviewed output — every PR reviewed by at least one independent verifier
2. Evidence-based verification — bare "PASS" is treated as INCONCLUSIVE
3. Anti-slop gate — complexity delta > 0.5 blocks for architecture review
4. Max 3 review-fix loops — prevents infinite agent cycles
5. Council verdicts are advisory — you may override with documented mitigation
6. No live capital changes from autonomous factory

## Maturation Levels

| Level | Autonomy | Human involvement |
|---|---|---|
| **L1** (current) | Henry reviews every PR | High |
| **L2** | Poteto Mode + parallel agents | Henry reviews only PRs |
| **L3** | Independent verifier + security gates | Auto-merge low-risk |
| **L4** | Full autonomous loop | Human sets policy only |

## Contributing

This is an open architecture. To contribute:
1. Read the reference architecture
2. Understand the 4 council gates and 5 security boundaries
3. Submit a PR with design changes or new integrations

## Origin

Designed for the HTS (Hyper Trading System) ecosystem. Sources: Factory.ai 2.0, Claude Code Ultracode, Islo security architecture, Matt Pocock skills, Lauren Tan Poteto Mode, Dexter Horthy — State of Software Factories, Google Antigravity patterns.

**License:** MIT