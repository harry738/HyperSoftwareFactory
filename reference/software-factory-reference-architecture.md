# Software Factory — Reference Architecture

> **This is the vision, not the plan.** It describes where the factory could go. The [build plan](build-plan.md) is the source of truth for what is being built and in what order, and it wins wherever the two differ. This document is no longer kept in step with it.

**Version:** v1.1 (2026-11-22)
**Status:** Target design. The working factory in `factory/` and `.claude/` implements part of it (issue intake, spec, build, gate, review, approve). The [build plan](build-plan.md) maps each section to what exists and what is next.
**Source:** Synthesis of Factory.ai 2.0, Claude Code Ultracode, Islo security architecture, Matt Pocock skills, Lauren Tan Poteto Mode (pstack), arXiv meta-engineering harness, Dexter Horthy — State of Software Factories / Slop Bench (Agentic AI Foundation, 2026-10)

> **Scope.** This document describes the generic factory. Notes specific to any one project live in that project's repo, not here.
>
> **Unverified claims.** These came from talks and posts and have not been checked against primary sources: the SlopCodeBench 14.8% figure, the "~100 TypeScript rules" lint set, the Antigravity reviewer pattern, and every install command in section 5. Verify each before relying on it.

**Terms.** *Hermes* is the orchestrating agent that triggers runs and sends notifications. *Council* is a panel of models that issues a verdict at a gate: **Fast** = Chair only, **Full** = Chair, Strategist, Pragmatist, Builder. *RM* is a roadmap item, the unit of work (`RM-XXXX`).

**Canonical shape:** 8 stages (Intake, Triage, Spec, Build, Verify, Deploy, Monitor, Learn), 3 council gates (Gate 1 triage, Gate 2 architecture, Gate 3 deploy), 1 weekly Kaizen review, 5 security boundaries.

---

## 1. Architecture Overview

The Software Factory is an end-to-end automated pipeline that takes raw signals (social intake, bugs, requirements, alerts) and produces deployed, verified, monitored software. It is built on Hermes, Claude Code, GitHub and Docker.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         FACTORY ORCHESTRATOR                              │
│               Hermes (orchestrator) + Claude Code (builder)               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  SIGNALS ──▶ INTAKE ──▶ TRIAGE ──▶ SPEC ──▶ BUILD ──▶ VERIFY ──▶ DEPLOY ──▶ MONITOR ──▶ LEARN
│     ▲           GATE 1       │        GATE 2       │      GATE 3     │        │          │
│     │          (Council)     │       (Council)      │     (Council)   │        │          │
│     │                       ▼                      ▼                  ▼        ▼          │
│     └─────────────────────────────────── FEEDBACK LOOP ───────────────────────────────────┘
│                                                                          │
│     Gate 1 sits in Triage, Gate 2 between Spec and Build, Gate 3 between Verify and Deploy.
│     Learn ends in the weekly Kaizen review, which feeds new signals back to Intake.
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Governing Principle: Forward Pressure + Backpressure

Dexter Horthy (CEO of HumanLayer, 2026-10 talk): *"More forward pressure without useful backpressure creates a larger pile of output."*

The factory has two forces:

| Force | What it is | Example |
|---|---|---|
| **Forward pressure** | Creates work — features, bugs, goals | Signals, intake, spec requests |
| **Backpressure** | Makes output meet a standard — tests, reviews, linting, gates | Verification, security gates, Council review |

An agent can iterate against backpressure checks before consuming human attention. The factory **must** provide both forces. Forward pressure without backpressure produces slop — code that compiles but degrades the codebase over time.

**SlopCodeBench (University of Wisconsin, 2026):** Models are tested by extending their own code across successive feature requests — the best model scored 14.8%. Reason: RL rewards one-shot correctness, not maintainability. Bad architecture shows up months later, not in a prompt. The factory's backpressure layer is the structural response to this.

### 1.2 Governing Principle: The Cost Shifts to Reading

Horthy: *"Engineering teams shipping AI-written code still have to read it."*

Producing a large PR is cheap. Understanding it is not. Unreviewed output shifts effort from producer to consumer. The factory counters this with:

1. **Evidence-based verification** — every verifier must show proof, not just claim (PASS/FAIL + evidence block)
2. **Anti-slop lint rules** — ~100 TypeScript rules (Dylan Moloy) that catch architecture decay before merge
3. **Maintainability scoring** — code complexity deltas tracked per PR, trended over time (defined in Section 2.4)
4. **Small PRs** — narrow stacked PRs (one writer per chain) keep diffs readable

### 1.3 Governing Principle: The Dumb Zone

Model degradation at ~100K tokens of context is real. The factory mitigates this with **plan files that survive context resets** — the handover/vault/spec pattern we already use. A plan file compresses intent into a maintained markdown document, allowing agents to resume from clean context without losing the architecture.

### 1.4 Layered Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     L7: ORCHESTRATOR                       │
│         Hermes — routing, state machine, cron, Buzz       │
├──────────────────────────────────────────────────────────┤
│                    L6: DECISION LAYER                       │
│         Product Council — 4-model debate, gates, verdicts  │
├──────────────────────────────────────────────────────────┤
│                    L5: BUILD FLOOR                          │
│         Claude Code Ultracode — parallel subagents, TDD    │
│         Poteto Mode — playbook routing, Overnight Mode    │
├──────────────────────────────────────────────────────────┤
│                    L4: VERIFICATION LAYER                   │
│         Independent test agents, code review, security     │
│         Matt Pocock /code-review, Trail of Bits skills    │
├──────────────────────────────────────────────────────────┤
│                    L3: SECURITY GATES                       │
│         Islo-inspired: microVM, egress, supply chain,      │
│         credential injection, budget ceilings              │
├──────────────────────────────────────────────────────────┤
│                    L2: INFRASTRUCTURE                       │
│         GitHub, Docker, Postgres, Buzz relay, CI/CD        │
├──────────────────────────────────────────────────────────┤
│                    L1: OBSERVABILITY                        │
│         Factory metrics DB, health endpoints, dashboards,  │
│         cost tracker, lifecycle status, alerting           │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Stage Details

### 2.1 Signal Intake

All signals that enter the factory:

| Source | Format | Agentic handling |
|---|---|---|
| Social intake (X, Instagram, TikTok, GitHub) | Links + metadata | Extract → classify (trading / startup / general) |
| Bug reports | GitHub issue or chat | Route: bug → Poteto `bug-fix` playbook |
| Customer feedback | Chat / email | Triage → spec or reject |
| Monitoring alerts | Watchdog Bot | Route: incident → RCA playbook |
| Kaizen findings | Weekly report | Route: system improvement → council |
| Manual (you) | "Build this" | Direct to spec queue (skip triage) |

**Trust boundary:** everything from outside (social posts, emails, web pages, issue text from strangers) is untrusted input and may contain instructions aimed at the agents. Raw external content is summarised into a fixed schema by a model call that has no tools. Only that summary reaches any agent that can write code, mint work, or call tools. Manual signals from the operator are the only trusted source.

**Triage rules:**
- Content is routed to a project by the slug in `config/projects.yaml` (for example `alpha`)  
- Bug → Poteto `bug-fix` playbook (investigation before fix)
- Alert → Ops playbook (diagnose before resolve)
- Unclear → Council fast mode (Chair only, 2 min verdict)

### 2.2 Spec & Architecture (Gates 1 & 2)

```
Signal → Fast Council (Gate 1)
   ├─ Reject → archived with reason
   ├─ Tier 3 → backlog queue
   └─ Tier 1-2 → Spec Writer
                    │
                    ├─ /grill-me (stress test the plan)
                    ├─ /to-spec (formal spec)
                    ├─ /to-tickets (break into tasks)
                    └─ /domain-modeling (if architecture)
                         │
                         ▼
                    Full Council (Gate 2 — architecture only if Tier 1 or cross-cutting)
                         │
                         ├─ Approved with conditions → Build Queue
                         └─ Rework → back to Spec
```

**RM minting** happens here. The ID must come from an atomic source, because parallel runs that each "grep the max RM" will mint duplicates. Use the GitHub issue number as the ID and derive `RM-XXXX` from it, then write the `roadmap.yaml` entry.

**Spec contract:** every spec states its acceptance criteria and its **public interface** (function signatures, routes, schemas). The spec-only Tester in Section 2.4 cannot write compilable tests without it.

### 2.3 Build Floor (parallel execution)

Once a spec clears Gate 2, it enters the build queue:

```
Spec + tickets → Claude Code Ultracode session
   │
   1. Wayfinder (Matt Pocock) — plan multi-session if large
   2. Generate workflow script (Claude dynamic workflow)
   3. Fan-out parallel subagents:
     ┌──────────┬──────────┬──────────┬──────────┐
     │ Agent A  │ Agent B  │ Agent C  │ Agent D  │
     │ module X │ module Y │ module Z │ tests Y  │
     │ TDD      │ TDD      │ TDD      │ TDD      │
     └────┬─────┴────┬─────┴────┬─────┴────┬─────┘
          │ verify   │ verify   │ verify   │ verify
          └────┬─────┴────┬─────┴────┬─────┴────┘
    4. Integrate → one PR, or one stacked chain of narrow PRs for large specs
    5. Matt Pocock /code-review on PR
```

**Poteto Mode routing per sub-task:**
- Bug fix → `bug-fix` playbook (reproduce → investigate → fix → verify)
- Feature → `feature` playbook (spec → test → implement → verify)
- Refactor → `refactoring` playbook (characterisation tests first → refactor → compare)
- Performance → `perf-issue` playbook (profile → identify → fix → benchmark)

**Context7 documentation injection:** Every build subagent loads **Context7** (Upstash MCP server) before writing implementation code. Context7 provides current, version-specific library documentation and code examples from official sources. This eliminates hallucinated deprecated API calls. Agents run `resolve-library-id` + `query-docs` tool calls before any library usage.

**Modern Web Guidance (MWG):** Before writing web features, agents consult **Google Chrome's Modern Web Guidance** (v1.0, Apache 2.0, 100+ guides). MWG provides expert-verified patterns for accessibility, CSS, HTML, performance, security, forms, and more. Agents reference MWG guides instead of generating outdated JS patterns. The project's Baseline target (declared in `CLAUDE.md` or `AGENTS.md`) determines which Browser APIs are available.

**Rules:**
- Concurrency cap set per project; start at 1 and raise it only when builds are reliable
- Parallel subagents work on disjoint modules only. Two agents never write the same files; anything that touches shared code is done by one writer after the parallel work lands
- 3 review-fix cycles max per sub-task
- Each subagent in isolated worktree copy
- No mid-run user input
- Runtime behavioral verification (run the change like a real user)

**Overnight Mode (Lauren Tan pattern):**
- `/poteto-mode i'm going to bed. land the stack`
- Agent stacks narrow PRs, one writer per chain
- Handles CI flakes: fresh build, never retry loop
- Same failure twice → reads the logs, fixes root cause
- Runs change like real user before landing
- Lands bottom-up, one PR at a time
- Morning: /ketchup (what landed, what parked, what needs human)

### 2.4 Verification Layer (independent)

Structural separation from build agents:

```
PR → Verifier Pool (separate agents, separate session, no shared history)
   │
   ├── Tester Agent
   │   Writes tests from spec ONLY (never sees implementation)
   │   Catches: does it meet the spec? Any edge cases missed?
   │
   ├── Code Reviewer Agent (Matt Pocock /code-review)
   │   Dual-axis: code standards + spec compliance
   │   Catches: anti-patterns, tech debt, logic errors
   │
   ├── Anti-Slop Lint Agent
   │   ~100 TypeScript rules (Dylan Moloy) + project-specific rules
   │   Catches: architecture decay, complexity creep, consistency violations
   │   Scored: output includes complexity delta vs pre-PR state
   │
   ├── Security Scanner Agent (Trail of Bits skills)
   │   Supply chain audit, credential leak check, egress analysis
   │   Catches: vulnerable deps, hardcoded secrets, data leaks
   │
   └── Behavioural Verifier Agent (Poteto Mode)
       Runs the change like a user would
       Catches: runtime errors, UX issues, integration breaks
```

**Read-only reviewer permissions:** Verifiers inspect but cannot mutate code. Implemented via:
1. **Separate permission scopes** — reviewer agents use read-only GitHub tokens (no write access to the repo)
2. **Read-only file system** — verifier containers mount the working directory as read-only
3. **Google Antigravity pattern** (Google Cloud Tech, Nov 2026) — isolated context windows per agent, reviewers physically cannot modify files because their tools have no write capability
This prevents the "reviewer that also fixes" pattern, which undermines structural separation.

**Evidence-based verification:** Every verifier emits `PASS / FLAG / FAIL` WITH an evidence block — the actual test output, log snippet, or diff that proves the verdict. A bare "PASS" with no evidence is treated as INCONCLUSIVE. This prevents rubber-stamping.

**Scoring:** Each verifier emits structured output. 3-review-fix loop cap before escalation.

**Complexity delta (definition):** for the files a PR touches, `delta = (C_after − C_before) / C_before`, where `C` is total cyclomatic complexity measured by a deterministic tool, not by a model. So `0.02` means 2% more complex and `0.5` means 50% more.
- `delta ≤ 0` → PASS
- `0 < delta ≤ 0.5` → FLAG: the PR must state why the increase is needed
- `delta > 0.5` → FAIL: blocked for architecture review
- PRs that only add new files have no `C_before`; they are FLAGged for review, never auto-failed

Coupling, file size and tech-debt markers are reported alongside but do not gate.

**Enforcement:** the rules in this section are enforced by the platform, not by agent instructions: branch protection requires the verifier checks, and verifier jobs run with read-only tokens.

### 2.5 Security Gates

The "Tech" column is the long-term target. The [build plan](build-plan.md) starts with simpler equivalents: ephemeral CI runners, environment-scoped secrets, runner-enforced budgets, an egress allowlist. Isolation and budgets must be in place **before** any autonomous build runs.

| Boundary | Enforcement | Tech |
|---|---|---|
| **Isolation** | Each agent job → dedicated microVM or container | Docker + compose per job |
| **Egress** | Default-deny gateway, allowlist only | iptables / Istio |
| **Supply chain** | Read-only registries, unapproved hosts denied | npm/pip read-only mode |
| **Credentials** | Placeholder in sandbox, gateway injects real key | Vault + proxy |
| **Budget** | Hard USD/token/time per run | Enforced by Hermes job runner |

### 2.6 Deployment (Gate 3)

```
Verified PR → Risk assessment:
   ├─ LOW (docs, config, tests, refactors with char tests)
   │     → Auto-merge → CI → Docker build → Deploy → Health check
   │
   ├─ MEDIUM (new feature, existing module change)
   │     → Fast Council (Chair only) → if approved → merge → deploy
   │
   └─ HIGH (guard changes, money path, new venue, auth)
         → Full Council (4-model) → verdict → merge → deploy
```

**Risk tier is computed from changed paths**, using per-project glob rules in `config/projects.yaml`. A change matching no rule is MEDIUM. A model may raise a tier but never lower it. HIGH always needs the operator's approval, whatever the Council says.

**Rollback:** every deploy keeps the previous release. If the post-deploy health check fails, the pipeline rolls back automatically, labels the item blocked, and alerts.

### 2.7 Observability Layer

Every stage emits structured events. Full system described in Section 3.

### 2.8 Feedback Loop (weekly Kaizen review)

```
Production signals → Kaizen report:
   ├─ Build failures (by type, by module, by agent model)
   ├─ Deploy incidents (correlated with PR, author, time)
   ├─ Review patterns (common failure modes)
   ├─ Cost data (LLM spend per PR, per stage, per model)
   ├─ Cycle time (signal → spec → build → verify → deploy)
   │
   ▼
Council review (Saturday):
   ├─ What systemic issues?
   ├─ Should we change process?
   ├─ New RM items minted?
   │
   ▼
New signals → Intake
```

---

## 3. Factory Observability

Borrowing an existing monitoring pattern (collector, metrics log, health endpoints):

### 3.1 Factory Metrics Schema

Drizzle table `factory_events`. It is **append-only**: one row per stage transition, never updated. Current state and cumulative cost are derived by query. Start with this one table and SQL; the metrics, endpoints and dashboard in 3.2–3.6 come later (build plan S6.7).

```typescript
export const factoryEvents = pgTable("factory_events", {
  id: serial("id").primaryKey(),
  // Core identifiers
  project: varchar("project", { length: 32 }).notNull(),  // the project's slug
  stage: varchar("stage", { length: 16 }).notNull(),  // "intake" | "triage" | "gate1" | "spec" | "gate2" | "build" | "verify" | "gate3" | "deploy" | "monitor" | "learn"
  status: varchar("status", { length: 16 }).notNull(),  // "entered" | "running" | "passed" | "failed" | "blocked"

  // Work item tracking
  workItemId: varchar("work_item_id", { length: 64 }).notNull(),  // stable from intake onward, e.g. "alpha#412"
  signalId: varchar("signal_id", { length: 32 }),  // source reference
  rmNumber: varchar("rm_number", { length: 8 }),  // RM-XXXX
  prNumber: integer("pr_number"),
  branch: varchar("branch", { length: 128 }),

  // Timing
  enteredAt: timestamp("entered_at").notNull().defaultNow(),
  completedAt: timestamp("completed_at"),
  durationSeconds: integer("duration_seconds"),  // computed on completion

  // Financial tracking
  llmCostUsd: doublePrecision("llm_cost_usd"),  // cost for this stage

  // Error tracking
  error: text("error"),
  errorCategory: varchar("error_category", { length: 32 }),  // "test_failure" | "timeout" | "review_rejected" | "ci_failure" | "deploy_failure"
  loopCount: integer("loop_count"),  // how many review-fix cycles

  // Agent tracking
  agentModel: varchar("agent_model", { length: 64 }),  // which model ran this stage
  subagentCount: integer("subagent_count"),  // for build stage — parallel subagents
  tokensUsed: integer("tokens_used"),

  // Metadata
  verdict: varchar("verdict", { length: 32 }),  // council verdict if applicable
  stageDetail: jsonb("stage_detail"),  // stage-specific payload
  tags: jsonb("tags"),  // flexible labels
});
```

### 3.2 Factory Metrics

Exposed as Prometheus-style metrics:

```
# Per-stage counters
factory_stage_entered{project="alpha",stage="intake"} 47
factory_stage_completed{project="alpha",stage="build",status="passed"} 42
factory_stage_completed{project="alpha",stage="build",status="failed"} 5

# Timing histograms (bucketed)
factory_stage_duration_seconds{project="alpha",stage="intake"}_bucket{le="60"} 45
factory_stage_duration_seconds{project="alpha",stage="build"}_bucket{le="3600"} 30

# Cost metrics
factory_llm_cost_usd_total{project="alpha",stage="build"} 123.45
factory_stage_cost_usd_total{project="alpha",stage="council"} 45.67

# Cycle time (signal to deploy)
factory_cycle_time_seconds{project="alpha"} 86400

# Current WIP by stage
factory_wip{project="alpha",stage="build"} 3
factory_wip{project="alpha",stage="verify"} 2

# Maintainability (anti-slop tracking)
factory_complexity_delta{project="alpha"} 0.02  # avg complexity increase per PR
factory_complexity_flag_rate{project="alpha"} 0.12  # fraction of PRs flagged
factory_review_evidence_rate{project="alpha"} 0.95  # fraction of verifications with evidence
```

### 3.3 Health Endpoints

Namespaced health endpoints:

| Endpoint | What it shows |
|---|---|
| `/api/health.factory` | Overall factory status: queue depth, agent availability, green/amber/red |
| `/api/health.factory.intake` | Intake queue: pending, triaging, completed today |
| `/api/health.factory.build` | Build floor: running agents, queued, completed, failed |
| `/api/health.factory.verify` | Verification: pending, in-progress, pass/fail rates |
| `/api/health.factory.cost` | Financials: LLM spend per RM, per PR, per stage |
| `/api/health.factory.pipeline` | DAG of every RM in flight: which stage, blocked at, time in stage |

### 3.4 Lifecycle Status Per RM

Every RM in flight has a status visible on a dashboard:

```
RM-0549 │ Research Evidence Module │ Tier 1
──────────────────────────────────────────────────
  INTAKE  │ 08:12 │ ✅ Entered   │ Triage → Spec
  GATE 1  │ 08:13 │ ✅ Passed    │ Council fast: Approved
  SPEC    │ 08:30 │ 🔄 Running   │ /to-spec + /to-tickets
  GATE 2  │       │ ⏳ Pending   │ Waiting for spec
  BUILD   │       │ ⏳ Pending   │ 
  VERIFY  │       │ ⏳ Pending   │
  GATE 3  │       │ ⏳ Pending   │
  DEPLOY  │       │ ⏳ Pending   │
──────────┴──────────────────────────────────────────
  Cost so far: $0.82 (Council $0.65 + Spec $0.17)
  Agents used: 1 council, 1 spec
  Cycle time: 2h 18m (running)
```

### 3.5 Alerting

Events that trigger alerts:

| Event | Severity | Action |
|---|---|---|
| Build stage failed 3x consecutively | 🔴 Critical | Escalate to human |
| Review-fix loop exceeded cap (3) | 🔴 Critical | PR blocked, human review |
| LLM spend per PR exceeds threshold | 🟡 Warning | Flag for cost review |
| Stage duration exceeds 2× expected | 🟡 Warning | Investigate bottleneck |
| Agent error rate > 10% in build stage | 🟠 High | Check model availability |
| CI flake detected (retry succeeded) | 🔵 Info | Log pattern |
| New RM minted | 🔵 Info | Log + dashboard update |
| Maintainability complexity delta > 0.5 | 🟠 High | PR blocked, architecture review needed |
| Any verifier emits PASS without evidence | 🔴 Critical | Verification failure — agent gamed the gate |

### 3.6 Dashboard Layout

```
┌────────────────────────────────────────────────────┐
│  FACTORY DASHBOARD            Last updated: 08:15  │
├────────────────────────────────────────────────────┤
│                                                    │
│  QUEUE                              TODAY'S COST    │
│  ┌────────────────────────┐       ┌──────────────┐  │
│  │ Intake:  3 pending     │       │ Council: $4.12│  │
│  │ Build:   2 running     │       │ Build:  $8.50│  │
│  │ Verify:  1 running     │       │ Total: $14.23│  │
│  │ Gate 3:  0 pending     │       └──────────────┘  │
│  └────────────────────────┘                         │
│                                                    │
│  PIPELINE (RMs in flight)           CYCLE TIME      │
│  ┌─────────────────────────────┐  ┌──────────────┐  │
│  │ RM-0549 ■■■■□□□□ BUILD     │  │ Avg: 6h 42m  │  │
│  │ RM-0550 ■■■□□□□□ GATE 2   │  │ Min: 1h 12m  │  │
│  │ RM-0548 ■■■■■■■■ DEPLOYED │  │ Max: 23h 8m  │  │
│  │ RM-0547 ■■■■■■■■ DEPLOYED │  └──────────────┘  │
│  └─────────────────────────────┘                    │
│                                                    │
│  AGENT UTILIZATION              RECENT FAILURES    │
│  ┌────────────────────────┐   ┌──────────────────┐  │
│  │ Claude Code:  2 in use │   │ Build: test flake │  │
│  │ Council:      1 active │   │ Verify: timeout  │  │
│  │ Verifier:     1 idle   │   │ CI: dep install  │  │
│  └────────────────────────┘   └──────────────────┘  │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 4. Build Plan

Moved to [build-plan.md](build-plan.md). It replaces the earlier six-phase tables with a walking-skeleton sequence, unique task IDs, and a measurable exit criterion per step.

---

## 5. Skills & Tools Inventory

### Status

| Tool | Installed | Use |
|---|---|---|
| Matt Pocock skills | ❌ | /grill-me, /to-spec, /to-tickets, /tdd, /code-review, /wayfinder |
| Poteto Mode (pstack) | ❌ | Playbook routing, Overnight Mode, runtime verification |
| Trail of Bits skills | ❌ | Security auditing |
| Superpowers (obra/superpowers) | ❌ | Systematic debugging, brainstorming |
| Humanizer (blader/humanizer) | ✅ | Startup stack |
| Frontend Design (Anthropic) | ✅ | Startup stack |

### Installations needed

These commands are unverified. Check each tool's own README for the current install command before running it.

```bash
# Phase 1 — install these first
claude plugin install mattpocock-skills@claude-plugins-official
npx skills add potetos-for-everyone/potetos-for-everyone
npx skills add trailofbits/skills  # security auditing
npx skills add obra/superpowers    # debugging, brainstorming

# Phase 1b — documentation & best practices (new)
npx @google/modern-web-guidance setup   # Chrome MWG skills (~205 tokens)
npm install -g ctx7                      # Context7 CLI + MCP server
ctx7 setup                               # adds rules and skills to Claude Code

# Setup per project repo
cd <project-repo> && /setup-matt-pocock-skills  # once per repo

# Add Baseline target to CLAUDE.md / AGENTS.md
echo "# This project's Baseline target is Baseline 2024." >> CLAUDE.md
echo "# Follow Modern Web Guidance for all web platform features." >> CLAUDE.md
```

---

## 6. Implementation Notes

### Hard Constraints

Generic (every project):

1. **No unreviewed output** — every PR is reviewed by at least one independent verifier before merge.
2. **Evidence-based verification** — every PASS must include evidence. A bare "PASS" is treated as INCONCLUSIVE.
3. **Anti-slop gate** — complexity delta > 0.5 (Section 2.4) blocks the PR for architecture review.
4. **Max 3 review-fix loops** — prevents infinite agent cycles.
5. **All secrets stay outside the sandbox** — credential injection pattern only.
6. **Council verdicts are advisory to the operator** — the operator may override with a documented mitigation. A Council can never approve a HIGH-risk change on its own.

---

## 7. Next Steps

See the [build plan](build-plan.md). The walking skeleton exists; the engine track comes next.
