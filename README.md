# 🏭 HyperSoftwareFactory

**Build, verify, and deploy software autonomously — across multiple projects.**

A production-grade automated pipeline that takes raw signals (social intake, bugs, requirements, alerts) and produces deployed, verified, monitored software. Built on Hermes, Claude Code, and GitHub.

---

## Quick Start

```bash
# Clone
git clone https://github.com/harry738/HyperSoftwareFactory.git
cd HyperSoftwareFactory

# Add a new project to the factory
python3 scripts/factory-onboard.py --interactive

# Then tell the factory:
# "run intake for <project-name>"
```

## Architecture

```
SIGNALS ─▶ INTAKE ─▶ SPEC ─▶ BUILD ─▶ VERIFY ─▶ DEPLOY ─▶ MONITOR ─▶ LEARN
                │          │         │          │          │            │
            Gate 1      Gate 2    Build    Gate 3     Metrics      Kaizen
           (Council)  (Council)  Floor   (Council)  Dashboard     Feedback
```

7 stages, 4 council gates, 5 security boundaries.

[Read the full reference architecture →](reference/software-factory-reference-architecture.md)

## Contents

| Directory | What's in it |
|---|---|
| [`reference/`](reference/) | Full architecture docs, integrations (Context7, Modern Web Guidance) |
| [`config/`](config/) | Central project registry (`projects.yaml`) |
| [`scripts/`](scripts/) | Onboarding wizard |
| [`factory/`](factory/) | The working factory: `bin/job` (state machine), `bin/gate`, `bin/route`, `bin/frontier`, `checks.sh`, `config.json`, live `dashboard.html` |
| [`.claude/agents/`](.claude/agents/) | Factory agents: intake, spec-writer, builder, code/security/UI/UX reviewers, approver |
| [`.claude/skills/`](.claude/skills/) | `factory` skill (`/factory run`) plus vetted, pinned skills (to-spec, to-tickets, tdd, deslop, ...) |
| [`reference/binley/`](reference/binley/) | First real use: pilot report, bootstrap prompt, how to run it on Windows |

## The working factory (L3, in use)

`factory/` and `.claude/` are the factory as it runs today on the Binley Building Society demonstrator (a fictional reference case). `/factory run` takes every open issue labelled `factory` through intake → spec → build → gate → review → approve, one PR per issue, with state in `factory/jobs/` and `factory/bin/job` as its only writer.

- **Install into a project:** copy `factory/` and `.claude/` into the target repo, then edit `factory/checks.sh`, `factory/config.json` (protected paths, models, prices) and the project paragraph in `.claude/agents/intake.md`. The copies here carry Binley's values as the worked example.
- **Dashboard:** `cd factory && python -m http.server`, then open http://localhost:8000/dashboard.html. A live board of every job by stage, with gate and reviewer verdicts, cost and time, and each job's files in a drawer.
- **Windows:** the scripts carry patches marked `# binley:` (see `factory/bin/proc.py` and `factory/test_factory.py`). Setup notes are in [`reference/binley/running-the-factory.md`](reference/binley/running-the-factory.md).

## How It Works

### Signal Intake
Social links, bug reports, customer feedback, and alerts enter through a triage queue. Classified and routed to the appropriate project.

### Council Gates (2 tiers)
- **Fast Council** (Chair-only) — triage verdicts in <2 min, ~$0.50
- **Full Council** (4 models: Chair, Strategist, Pragmatist, Builder) — architecture review in <10 min, ~$3-7

### Build Floor
Approved specs decompose into parallel Claude Code subagents (Ultracode pattern, up to 256 concurrent). Each subagent:
- Loads **Context7** (Upstash MCP) for current, version-specific library documentation — eliminates hallucinated deprecated API calls
- Consults **Modern Web Guidance** (Google Chrome v1.0, 100+ guides) for web best practices — accessibility, performance, security, Baseline-aware
- Follows Poteto Mode playbooks (bug → investigate → fix → verify / feature → spec → test → implement)
- Runs in isolated worktree, max 3 review-fix cycles

### Independent Verification
Structural separation with read-only reviewers:
- **Tester** — writes tests from spec only (never sees implementation)
- **Code Reviewer** — dual-axis: standards + spec compliance
- **Anti-Slop Lint** — ~100 TypeScript rules + complexity delta tracking
- **Security Scanner** — supply chain, credentials, egress
- **Behavioural Verifier** — runs the change like a user would

Reviewers have read-only permissions — they physically cannot modify code.

### Security Boundaries

| Boundary | What it blocks |
|---|---|
| **Isolation** | Agent can't touch host or other tenants |
| **Egress** | Default-deny gateway, allowlist only |
| **Supply chain** | Read-only package registries, unapproved hosts denied |
| **Credentials** | Placeholder in sandbox, gateway injects real key |
| **Budget** | Hard USD/token/time per run, pinned model versions |

### Observability
Every stage emits structured events. Prometheus metrics track: stage durations, LLM cost per feature, cycle time, agent utilization, code complexity deltas.

### Kaizen Feedback Loop
Weekly council reviews build failures, deploy incidents, cost data, and cycle times. Systemic issues mint new improvement items.

## Hard Constraints

1. **No unreviewed output** — every PR reviewed by at least one independent verifier
2. **Evidence-based verification** — bare "PASS" is treated as INCONCLUSIVE
3. **Anti-slop gate** — complexity delta > 0.5 blocks for architecture review
4. **Max 3 review-fix loops** — prevents infinite agent cycles
5. **All secrets stay outside sandbox** — credential injection pattern only

## Maturation Levels

| Level | Autonomy | Human involvement |
|---|---|---|
| **L1** | Assisted — human reviews every PR | High |
| **L2** | Parallel agents + Poteto Mode | Human reviews only PRs |
| **L3** | Independent verifier + security gates | Auto-merge low-risk |
| **L4** | Full autonomous loop | Human sets policy only |

## Integrations

| Tool | Stage | What it provides |
|---|---|---|
| **Context7** (Upstash) | Build Floor | Current, version-specific library docs via MCP — free tier: 1,000 calls/month |
| **Modern Web Guidance** (Google Chrome) | Build Floor + Verification | 100+ expert-verified web best practices across 17 disciplines — Apache 2.0 |
| **Crawl4AI** | Research Scan | JS-rendered page extraction with optional Chrome cookie authentication |
| **TestSprite 4.0** | Verification (recommended) | Independent testing agent — 94% bug-finding accuracy, $4.60/200 tests |

## Project Configuration

Projects are registered in [`config/projects.yaml`](config/projects.yaml). Each project gets its own GitHub repo, roadmap, and build queue.

Add new projects with:
```bash
python3 scripts/factory-onboard.py --interactive
```

## Contributing

1. Read the [reference architecture](reference/software-factory-reference-architecture.md) to understand the 7 stages, 4 council gates, and 5 security boundaries
2. Open an issue to discuss your proposed change
3. Submit a PR with design changes or new integrations

## Origin

Designed for agentic software development. Sources: Factory.ai 2.0, Claude Code Ultracode, Islo security architecture, Matt Pocock skills, Lauren Tan Poteto Mode (pstack), Dexter Horthy — State of Software Factories (Agentic AI Foundation, 2026), Google Antigravity patterns, arXiv meta-engineering harness.

**License:** MIT, except `factory/`, `.claude/agents/` and `.claude/skills/factory/`, which are GPLv3 (see [`factory/LICENSE`](factory/LICENSE); from zazencodes-season-3 `src/software-factory-claude-code-v2`, with local patches). Vendored skills keep their own MIT licences in `.claude/skills/`.