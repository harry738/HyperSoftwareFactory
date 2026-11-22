# HTS/HyperOS Software Factory — Reference Architecture

**Version:** v1 (2026-11-19)
**Status:** Design Draft
**Source:** Synthesis of Factory.ai 2.0, Claude Code Ultracode, Islo security architecture, Matt Pocock skills, Lauren Tan Poteto Mode (pstack), arXiv meta-engineering harness, Dexter Horthy — State of Software Factories / Slop Bench (Agentic AI Foundation, 2026-10)

---

## 1. Architecture Overview

The Software Factory is an end-to-end automated pipeline that takes raw signals (social intake, bugs, requirements, alerts) and produces deployed, verified, monitored software. It is built on our existing toolchain: Hermes, Claude Code, Buzz relay, GitHub, Docker.

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
│     STAGES:   Signal      Plan      Build       Check      Ship      Observe    Improve
│               Intake      & Spec    Floor       + Secure   + Deploy   + Metrics  + Kaizen
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 0.1 Governing Principle: Forward Pressure + Backpressure

Dexter Horthy (CEO of HumanLayer, 2026-10 talk): *"More forward pressure without useful backpressure creates a larger pile of output."*

The factory has two forces:

| Force | What it is | Example |
|---|---|---|
| **Forward pressure** | Creates work — features, bugs, goals | Signals, intake, spec requests |
| **Backpressure** | Makes output meet a standard — tests, reviews, linting, gates | Verification, security gates, Council review |

An agent can iterate against backpressure checks before consuming human attention. The factory **must** provide both forces. Forward pressure without backpressure produces slop — code that compiles but degrades the codebase over time.

**SlopCodeBench (University of Wisconsin, 2026):** Models are tested by extending their own code across successive feature requests — the best model scored 14.8%. Reason: RL rewards one-shot correctness, not maintainability. Bad architecture shows up months later, not in a prompt. The factory's backpressure layer is the structural response to this.

### 0.2 Governing Principle: The Cost Shifts to Reading

Horthy: *"Engineering teams shipping AI-written code still have to read it."*

Producing a large PR is cheap. Understanding it is not. Unreviewed output shifts effort from producer to consumer. The factory counters this with:

1. **Evidence-based verification** — every verifier must show proof, not just claim (PASS/FAIL + evidence block)
2. **Anti-slop lint rules** — ~100 TypeScript rules (Dylan Moloy) that catch architecture decay before merge
3. **Maintainability scoring** — code complexity deltas tracked per PR, trended over time (Section 3.2)
4. **Small PRs** — Poteto Mode's narrow stacked PRs (one change per chain) keep diffs readable

### 0.3 Governing Principle: The Dumb Zone

Model degradation at ~100K tokens of context is real. The factory mitigates this with **plan files that survive context resets** — the handover/vault/spec pattern we already use. A plan file compresses intent into a maintained markdown document, allowing agents to resume from clean context without losing the architecture.

### 1.1 Layered Architecture

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

**Triage rules:**
- Trading content → HTS build queue
- Startup content → HyperOS build queue  
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

**RM Minting** happens here: `grep max RM → mint RM-XXXX → roadmap.yaml entry → commit`

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
    4. Convergence merge → single PR
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
- Max 256 concurrent agents (Claude Code limit)
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

**Maintainability delta:** The Anti-Slop Lint Agent computes a complexity score before and after the PR change (cyclomatic complexity, coupling, file size, tech debt markers). A positive delta (code got more complex) triggers a FLAG — the PR author must justify why the complexity increase is necessary.

### 2.5 Security Gates

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

### 2.7 Observability Layer

Every stage emits structured events. Full system described in Section 3.

### 2.8 Feedback Loop (Gate 4 — weekly)

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

Borrowing from HTS's monitoring dashboard pattern (monitor/collector, metrics_log, health endpoints):

### 3.1 Factory Metrics Schema

Drizzle table `factory_events`:

```typescript
export const factoryEvents = pgTable("factory_events", {
  id: serial("id").primaryKey(),
  // Core identifiers
  project: varchar("project", { length: 32 }).notNull(),  // "hts" | "hyperos" | "propinfo"
  stage: varchar("stage", { length: 16 }).notNull(),  // "intake" | "triage" | "spec" | "gate1" | "build" | "verify" | "gate3" | "deploy" | "monitor"
  status: varchar("status", { length: 16 }).notNull(),  // "entered" | "running" | "passed" | "failed" | "blocked"

  // Work item tracking
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
  totalCostUsd: doublePrecision("total_cost_usd"),  // cumulative for this RM

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

Exposed as Prometheus-style metrics (same pattern as HTS collectors):

```
# Per-stage counters
factory_stage_entered{project="hts",stage="intake"} 47
factory_stage_completed{project="hts",stage="build",status="passed"} 42
factory_stage_completed{project="hts",stage="build",status="failed"} 5

# Timing histograms (bucketed)
factory_stage_duration_seconds{project="hts",stage="intake"}_bucket{le="60"} 45
factory_stage_duration_seconds{project="hts",stage="build"}_bucket{le="3600"} 30

# Cost metrics
factory_llm_cost_usd_total{project="hts",stage="build"} 123.45
factory_stage_cost_usd_total{project="hts",stage="council"} 45.67

# Cycle time (signal to deploy)
factory_cycle_time_seconds{project="hts"} 86400

# Current WIP by stage
factory_wip{project="hts",stage="build"} 3
factory_wip{project="hts",stage="verify"} 2

# Maintainability (anti-slop tracking)
factory_complexity_delta{project="hts"} 0.02  # avg complexity increase per PR
factory_complexity_flag_rate{project="hts"} 0.12  # fraction of PRs flagged
factory_review_evidence_rate{project="hts"} 0.95  # fraction of verifications with evidence
```

### 3.3 Health Endpoints

Same pattern as HTS `/api/health.*`:

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

Same pattern as HTS Watchdog Bot — events that trigger alerts:

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

### 3.6 Dashboard Layout (borrowing from Infradeck & HTS)

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

### Phase 1 — Foundation (Week 1)

| # | Task | Effort | Depends On | Outcome |
|---|---|---|---|---|
| 1.1 | Create `factory_events` table (Drizzle migration) | 1h | None | Metrics schema in Postgres |
| 2.1 | Install Matt Pocock skills (`claude plugin install`) | 10min | None | /grill-me, /to-spec, /to-tickets, /tdd, /code-review |
| 3.1 | Install Poteto Mode (`npx skills add potetos-for-everyone`) | 10min | None | Playbook routing, Overnight Mode |
| 4.1 | Create `FactoryMetricsCollector` (borrow HTS collector pattern) | 2h | 1.1 | Metrics emitted per stage event |
| 5.1 | Add factory health endpoints `/api/health.factory.*` | 3h | 1.1 | Live factory status visible |

**Phase 1 Gate:** Factory metrics visible on dashboard, skills installed, baseline captured.

### Phase 2 — Intake Automation (Week 1-2)

| # | Task | Effort | Depends On | Outcome |
|---|---|---|---|---|
| 2.1 | Wire social intake → factory triage queue | 2h | 1.2, 4.1 | Social links auto-enter intake |
| 2.2 | Fast Council (Chair-only) for triage verdicts | 3h | 2.1 | Signals get RM or reject within 2 min |
| 2.3 | `/to-spec` + `/to-tickets` pipeline from triaged signal | 2h | 2.2 | Spec + tickets auto-generated |
| 2.4 | RM minting automation (grep → mint → roadmap.yaml) | 2h | 2.3 | RM auto-minted from ticket |

**Phase 2 Gate:** Signal → RM minted in under 5 min, fully automated.

### Phase 3 — Build Floor (Week 2-3)

| # | Task | Effort | Depends On | Outcome |
|---|---|---|---|---|
| 3.1 | Generate Claude Code workflow from spec + tickets | 4h | 2.3, 2.4 | Ultracode workflow auto-generated |
| 3.2 | Wire Poteto Mode playbook routing per sub-task | 3h | 3.1 | Bug/feature/refactor auto-routed |
| 3.3 | Convergence merge → PR with verification checks | 3h | 3.2 | One PR per spec with verified sub-tasks |
| 3.4 | Matt Pocock /code-review wired as verify stage | 1h | 3.3 | Dual-axis review auto-triggered |

**Phase 3 Gate:** Signal → PR in one autonomous run (build floor completes without human intervention).

### Phase 4 — Verification & Security (Week 3-4)

| # | Task | Effort | Depends On | Outcome |
|---|---|---|---|---|
| 4.1 | Independent test agent (writes tests from spec only) | 4h | 3.3 | Structural separation: tester ≠ implementer |
| 4.2 | Trail of Bits security skills installed + wired | 1h | 4.1 | Vulnerable deps caught |
| 4.3 | Credential injection gateway (envoy sidecar pattern) | 4h | 4.2 | Secrets never in agent sandbox |
| 4.4 | Budget ceilings per run (USD, tokens, time, loops) | 2h | 4.3 | Run killed if exceeds budget |

**Phase 4 Gate:** Full verification pipeline with security gates and structural agent separation.

### Phase 5 — Deployment Gates (Week 4-5)

| # | Task | Effort | Depends On | Outcome |
|---|---|---|---|---|
| 5.1 | Risk classifier for PRs (low/medium/high) | 2h | 4.1 | Auto-classify PR risk tier |
| 5.2 | Low-risk auto-merge + deploy pipeline | 3h | 5.1 | Docs/config deploy without human |
| 5.3 | Medium-risk Fast Council gate | 2h | 5.2 | Chair rules on deploy in < 2 min |
| 5.4 | High-risk Full Council gate | 2h | 5.3 | 4-model debate on critical changes |

**Phase 5 Gate:** PR → Deploy with appropriate human involvement per risk level.

### Phase 6 — Feedback Loop (Week 5-6)

| # | Task | Effort | Depends On | Outcome |
|---|---|---|---|---|
| 6.1 | Kaizen auto-report from factory_events | 3h | 1.1 | Weekly report auto-generated |
| 6.2 | Failure classification pipeline | 3h | 6.1 | Build failures classified (test/spec/agent) |
| 6.3 | Cost analytics dashboard (per RM, per stage, per model) | 4h | 1.1, 6.2 | Financial transparency |
| 6.4 | Council auto-intake from Kaizen | 2h | 6.2, 5.4 | New RM items from failures |

**Phase 6 Gate:** Factory self-improves without human intervention.

---

## 5. Skills & Tools Inventory

### Installed Now

| Tool | Installed | Use |
|---|---|---|
| Matt Pocock skills | ❌ | /grill-me, /to-spec, /to-tickets, /tdd, /code-review, /wayfinder |
| Poteto Mode (pstack) | ❌ | Playbook routing, Overnight Mode, runtime verification |
| Trail of Bits skills | ❌ | Security auditing |
| Superpowers (obra/superpowers) | ❌ | Systematic debugging, brainstorming |
| Humanizer (blader/humanizer) | ✅ | Startup stack |
| Frontend Design (Anthropic) | ✅ | Startup stack |

| New Installations Needed

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

# Phase 2 — setup per repo
cd ~/hyper-trading-system && /setup-matt-pocock-skills  # once per repo

# Add Baseline target to CLAUDE.md / AGENTS.md
echo "# This project's Baseline target is Baseline 2024." >> CLAUDE.md
echo "# Follow Modern Web Guidance for all web platform features." >> CLAUDE.md
```

---

## 6. Implementation Notes

### HTS Borrows

The factory reuses these HTS patterns directly:

| HTS Pattern | Factory Equivalent |
|---|---|
| `metrics_log` table | `factory_events` table |
| `collector.ts` (Prometheus metrics) | `FactoryMetricsCollector` |
| `/api/health.*` endpoints | `/api/health.factory.*` |
| Watchdog Bot alerting | Factory alert rules |
| Buzz relay dispatch (cron/notifications) | Factory event dispatch |
| Settings toggles (`gen_*` flags) | Factory feature toggles |
| Product Council run script | Factory gate script (same council.py) |
| Handover protocol | Spec + Build handover (same format) |
| QA reviewer agent | Independent verifier agent pool |

### Hard Constraints

1. **JEV stays shadow-only** — no gating until calibration holds
2. **Council verdicts are advisory** — you may override with documented mitigation
3. **No live capital changes** from autonomous factory — deploy gates block high-risk to you
4. **Max 3 review-fix loops** — prevents infinite agent cycles
5. **All secrets stay outside sandbox** — credential injection pattern only
6. **Evidence-based verification** — every PASS must include evidence. A bare "PASS" is treated as INCONCLUSIVE.
7. **Anti-slop gate** — any PR that increases complexity delta > 0.5 is blocked for architecture review. No exceptions.
8. **No unreviewed output** — every PR is reviewed by at least one independent verifier before merge.

---

## 7. Next Steps

### Immediate (Phase 1 today)

1. ✅ Design documented (this file)
2. ❌ Install Matt Pocock skills
3. ❌ Install Poteto Mode
4. ❌ Create `factory_events` table
5. ❌ Build `FactoryMetricsCollector`

### This week

- Build Phase 1: foundation + observability
- Wire intake automation
- First end-to-end test: link → triage → spec → RM
- Run one small RM through full pipeline manually

### Next sprint

- Phase 2-3: Build floor + parallel agents
- Install Overnight Mode
- First autonomous build session