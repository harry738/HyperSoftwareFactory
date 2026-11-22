# 🏭 HyperSoftwareFactory

**A software factory for building, verifying, and merging software with AI agents, and a reference architecture for where it is going.**

The factory takes GitHub issues today, and aims to take raw signals (social intake, bugs, requirements, alerts), and produce deployed, verified, monitored software, using Hermes, Claude Code, and GitHub. The first deployment is **local-first on an operator's desktop**, with no mandatory API billing or cloud control plane.

> **Status.** Two things live here:
> - **A working factory** in `factory/` and `.claude/`: issue → intake → spec → build → gate → review → approve → merge. It has run one pilot job on one project ([pilot report](reference/binley/pilot-report-2026-11-21.md)).
> - **A target architecture** in `reference/`: signal intake, council gates, deploy, monitoring, and Kaizen. Those parts are not built. The [build plan](reference/build-plan.md) says what exists, what is next, and how to tell each step is done.

---

## Local-first: Claude Code Desktop + subscription-based Codex

**Initial operating mode:** open the project in **Claude Desktop's Code tab** or Claude Code CLI on your own Windows PC and run `/factory run` interactively. The same checked-out factory tools and state machine are used. The authenticated operator remains in control of GitHub and manual merging; no hosted factory service is required.

1. **Claude subscription:** Sign in to Claude Desktop / Claude Code with your **Claude Ultra** account and run `/status` to confirm the active plan. Prefer the native Claude Code session to orchestrate its own built-in agents. The operator must not set `ANTHROPIC_API_KEY` for this subscription-only path, because an API key can switch Claude Code to separately billed API usage.
2. **OpenAI subscription:** Install the official **Codex CLI** locally and run `codex` to sign in with your ChatGPT account. Eligible ChatGPT subscriptions include Codex usage subject to limits. The existing factory does **not** yet invoke Codex; a provider adapter is planned and must use officially supported login/SDK interfaces.
3. **Credentials:** Authenticate each official tool directly as the signed-in user. Do not extract session cookies, OAuth tokens or tokens from other apps, share subscription credentials, or silently fall back to separately billed APIs. Keep credentials outside worktrees and agent-visible files.
4. **Quotas and budget:** Subscription usage is metered under provider-specific rate/weekly limits, **not** an unlimited dollar balance. The dashboard's `cost_usd` is an **API-equivalent estimate** for Claude subagents, not a subscription charge or remaining allowance. A plan-limit error must pause or escalate the job; never silently purchase API credits.
5. **Execution:** Start with one local, supervised job (`concurrency: 1`), low-risk code changes, Git worktrees, and manual PR merging. Running a local control plane does not mean model inference happens offline. Cloud runners, paid APIs and unattended service accounts are optional later phases, not prerequisites.

See [Local desktop and subscription architecture](reference/local-desktop-subscription-architecture.md) for setup, provider boundaries and how the optional Codex integration should evolve. See official [Claude Code plan guidance](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-max-or-ultra-plan) and [OpenAI Codex plan guidance](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan).

## The working factory

`factory/` and `.claude/` are the factory as it runs today on the Binley Building Society demonstrator (a fictional reference case). `/factory run` takes every open issue labelled `factory` through intake → spec → build → gate → review → approve, one PR per issue, with state in `factory/jobs/` and `factory/bin/job` as its only writer.

- **Install into a project:** copy `factory/` and `.claude/` into the target repo, then write the project's checks into `factory/checks.sh` (it fails until you do) and set `protected_paths`, `dev_server` (the command the UI and UX reviewers browse, `{port}` filled in; Next.js by default, drop it if there are no pages), models and prices in `factory/config.json`. Intake reads what belongs in the project from its `AGENTS.md` or `CLAUDE.md`. Binley's `checks.sh` and `config.json` are in `reference/binley/` as a worked example.
- **Dashboard:** `cd factory && python -m http.server`, then open http://localhost:8000/dashboard.html. A live board of every job by stage, with gate and reviewer verdicts, cost and time, and each job's files in a drawer.
- **Windows:** the scripts carry patches marked `# binley:` (see `factory/bin/proc.py` and `factory/test_factory.py`). Setup notes are in [`reference/binley/running-the-factory.md`](reference/binley/running-the-factory.md).
- **Evidence so far:** one pilot job, all-PASS path only, merged by hand after a Windows gate fault. Gate failures, change rounds, the security reviewer and unattended merge are not yet exercised.
- **Assurance hardening:** the gate now checks protected additions and rename destinations; reviewers bind their verdicts to an exact commit and requirements snapshot; deterministic risk classification cannot be downgraded by intake; unattended merges are **disabled by default**. See [assurance hardening recommendations](reference/assurance-hardening-recommendations.md).
- **CI:** [portable factory assurance tests](.github/workflows/factory-assurance.yml) run on Linux and Windows. This does not replace full agent integration tests.

## Contents

| Path | What's in it |
|---|---|
| [`factory/`](factory/) | The working factory: `bin/job` (state machine), `bin/gate`, `bin/route`, `bin/frontier`, `checks.sh`, `config.json`, live `dashboard.html` |
| [`.claude/agents/`](.claude/agents/) | Factory agents: intake, spec-writer, builder, code/security/UI/UX reviewers, approver |
| [`.claude/skills/`](.claude/skills/) | `factory` skill (`/factory run`) plus vetted, pinned skills (to-spec, to-tickets, tdd, deslop, ...) |
| [`reference/binley/`](reference/binley/) | First real use: pilot report, bootstrap prompt, how to run it on Windows |
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
| [Assurance hardening recommendations](reference/assurance-hardening-recommendations.md) | Reviewed findings, safeguards, limitations and verification criteria |
| [Local desktop + subscriptions](reference/local-desktop-subscription-architecture.md) | Claude Ultra and ChatGPT Codex authentication, initial runtime and future adapters |
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

## Deterministic assurance and merge policy

The working factory now separates **agent verdicts** from **enforced merge controls**:

1. `factory/bin/gate` rejects added, removed, renamed or modified files matching `protected_paths`, including newly created workflow files.
2. When entering the review stage, `factory/bin/job` records the head/base commit SHAs and SHA-256 of `issue.md` and `spec.md`. Reviewers must include `COMMIT: <full SHA>`; a changed commit or requirements snapshot invalidates approval.
3. `risk_paths` in `factory/config.json` sets a path-based risk floor; intake may raise but not lower the tier. Unmatched paths are MEDIUM. Configure sensitive paths for each project.
4. Specifications must declare `SCOPE_CHANGE: no|yes` and trace original criteria. Any declared rescope or missing traceability requires human review; **semantic equivalence is not yet independently proved**.
5. `merge_policy.allow_unattended` defaults to `false`. Approved jobs are escalated for **manual GitHub merge** rather than self-merging.

These controls are not a security sandbox: reviewers still have broad file and shell permissions, runtime credentials are not isolated, and GitHub branch protection must be configured by an administrator. Do not enable unattended merging until the [hardening plan](reference/assurance-hardening-recommendations.md) is validated.

## Hard Constraints

1. **No unreviewed output** — every PR is reviewed by at least one independent verifier
2. **Evidence-based verification** — a bare "PASS" is treated as INCONCLUSIVE
3. **Anti-slop gate** — a complexity increase above 50% on touched files blocks the PR for architecture review
4. **Max 3 review-fix loops** — prevents infinite agent cycles
5. **All secrets stay outside the sandbox**

The target is to enforce these by the platform (branch protection, token scopes, runner budgets), not by agent instructions. The working factory enforces a missing-review guard, capped build rounds, protected paths and commit-bound verdict metadata; read-only reviewers, evidence quality and strong isolation are still pending.

## Autonomy Levels

| Level | What runs without you | Earned by |
|---|---|---|
| **L1** | Build to PR; you review every PR | Build plan Step 1 |
| **L2** | Build + checks + verifiers | Step 3 |
| **L3** | Low-risk merge and deploy | Step 5 |
| **L4** | Intake to deploy for low-risk work; you set policy | Step 6 |

The working factory has the machinery for L2 and an approver. On evidence it is still a supervised pilot: one job, merged by hand. Unattended merging remains disabled by default.

## Planned Integrations

None of these is wired in yet, and their claims are the vendors' own.

| Tool | Stage | What it provides |
|---|---|---|
| **Context7** (Upstash) | Build | Current, version-specific library docs via MCP |
| **Modern Web Guidance** (Google Chrome) | Build + Verify | Web platform best practices, Baseline-aware |
| **Crawl4AI** | Intake research | JS-rendered page extraction |

## Development

```bash
python scripts/test_factory_onboard.py                     # self-check for onboarding
python -m unittest discover -s factory -p test_assurance.py -v  # portable assurance regression tests
python factory/test_factory.py                             # Windows integration checks; run in a configured project
```

## Contributing

1. Read the [reference architecture](reference/software-factory-reference-architecture.md) and the [build plan](reference/build-plan.md)
2. Open an issue to discuss your proposed change
3. Submit a PR

## Origin

Synthesised from public material on agentic software development: Factory.ai, Claude Code, Islo's security architecture, Matt Pocock's skills, Lauren Tan's Poteto Mode, and Dexter Horthy's talk on software factories.

**License:** [MIT](LICENSE), except `factory/`, `.claude/agents/` and `.claude/skills/factory/`, which are GPLv3 (see [`factory/LICENSE`](factory/LICENSE); from zazencodes-season-3 `src/software-factory-claude-code-v2`, with local patches). Vendored skills keep their own MIT licences in `.claude/skills/`.
