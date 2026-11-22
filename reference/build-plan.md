# Software Factory — Build Plan

**Version:** v2 (2026-11-22) — replaces the phase tables formerly in section 4 of the reference architecture.
**Status:** Not started. Nothing below is built yet.

---

## Approach

Build a **walking skeleton** first: one work item flowing end to end on one project, with a human reviewing every PR. Then add backpressure, and only then autonomy. Each step must work on real items before the next begins.

Rules for the plan itself:

1. **GitHub is the state store.** A work item is a GitHub issue; its state is its labels and its PR. No separate queue or database until volume demands one.
2. **Backpressure before forward pressure.** Checks, budgets and isolation land before any automation that creates more work.
3. **Deterministic gates before LLM gates.** A test suite, a linter and path rules are cheaper and harder to game than a model's opinion. LLM reviewers add to them; they never replace them.
4. **Enforce with the platform, not with prompts.** "No unreviewed output" is a branch-protection rule. "Reviewers cannot write" is a token scope.
5. **Measure before automating.** A stage is automated only after its manual version has run on at least ten items and the numbers say it is safe.

Pilot project: pick **one** registered project, ideally the one with the best existing test suite. Do not onboard a second until Step 4 exits.

---

## Steps

Each step lists its tasks, then an exit criterion. Do not start a step until the previous one has exited.

### Step 0 — Repo hygiene (done 2026-11-22)

| ID | Task |
|---|---|
| S0.1 | Docs consistent: stage and gate counts, repo names, complexity gate definition |
| S0.2 | Onboarding script fixed, with a self-check (`scripts/test_factory_onboard.py`) |
| S0.3 | LICENSE, `.gitignore`, `requirements.txt` |

### Step 1 — Walking skeleton (autonomy L1)

| ID | Task | Depends on |
|---|---|---|
| S1.1 | Define work-item labels in the pilot repo: `factory:ready`, `factory:building`, `factory:review`, `factory:blocked`, `factory:done` | — |
| S1.2 | Issue template for a spec: goal, acceptance criteria, **public interface** (signatures, routes, schemas), out of scope | — |
| S1.3 | Build workflow: `factory:ready` label triggers a GitHub Actions job that runs Claude Code headless against the issue and opens one PR | S1.1, S1.2 |
| S1.4 | Per-run caps on that job: turn limit, wall-clock timeout, max review-fix cycles = 3. On breach, label `factory:blocked` and comment why | S1.3 |
| S1.5 | Event log: each state change appends one row (item, stage, status, timestamp, cost, tokens, model). A JSONL artifact or one Postgres table; query with SQL | S1.3 |
| S1.6 | Branch protection on the pilot repo's default branch: PR required, one human approval, CI required | — |

**Exit:** ten real issues have gone label → PR → human-reviewed merge. For each, the event log shows cycle time and cost. You have a baseline for *human-edit rate* (PRs you had to change before merging) and *escape rate* (merged PRs later reverted or hot-fixed).

### Step 2 — Deterministic backpressure

| ID | Task | Depends on |
|---|---|---|
| S2.1 | Required CI checks: tests, type-check, lint | S1.6 |
| S2.2 | Complexity check with a deterministic tool, implementing the complexity-delta definition in architecture §2.4 | S2.1 |
| S2.3 | Secret scanning and dependency audit as required checks | S2.1 |
| S2.4 | The build agent runs all of the above locally and iterates before it opens the PR | S2.1–S2.3 |

**Exit:** no factory PR can merge with a failing check, and at least 80% of factory PRs arrive with all checks green on first push.

### Step 3 — Independent verification

| ID | Task | Depends on |
|---|---|---|
| S3.1 | Verifier workflow in a **separate job** with a read-only token (`contents: read`, `pull-requests: write`) and no shared session with the builder | S2 exit |
| S3.2 | Spec-only tester: writes tests from the issue's acceptance criteria and public interface, without the diff. Tests are committed by a narrowly scoped job, not by the verifier | S3.1, S1.2 |
| S3.3 | Code reviewer: standards + spec compliance, posted as a PR review | S3.1 |
| S3.4 | Evidence rule enforced in code: a verdict without an evidence block (test output, log, diff reference) is recorded as INCONCLUSIVE and fails the check | S3.1 |
| S3.5 | Behavioural verifier: runs the change as a user would, for projects with a runnable preview | S3.1 |

**Exit:** on twenty PRs, compare verifier verdicts with your own review. Record how often the verifiers caught what you caught and how often they flagged noise. Proceed only if they miss fewer than one in ten of the issues you found.

### Step 4 — Isolation, credentials, budgets

| ID | Task | Depends on |
|---|---|---|
| S4.1 | All agent jobs on ephemeral runners; no agent runs on a machine that holds other projects or personal credentials | S1.3 |
| S4.2 | Secrets scoped by GitHub environment; build and verify jobs get no deploy secrets | S4.1 |
| S4.3 | Hard USD budget per run and per day per project, enforced by the runner (kill the job), configured in `projects.yaml` | S1.5 |
| S4.4 | Egress allowlist for agent jobs (package registries, GitHub, model API) | S4.1 |
| S4.5 | Pin model versions per stage in config | — |

**Exit:** a deliberately runaway test run is killed by the budget; a test run that tries to read a deploy secret or reach an unlisted host fails.

The microVM, service-mesh and credential-gateway designs in architecture §2.5 are the long-term target. Build them only if a threat model for a specific project shows the above is not enough.

### Step 5 — Risk-tiered merge and deploy (autonomy L3)

| ID | Task | Depends on |
|---|---|---|
| S5.1 | Per-project config in `projects.yaml`: `risk_paths` (high/medium globs), `deploy` target, `budget`, `baseline_target` | S4 exit |
| S5.2 | Risk tier computed from changed paths only. Anything matching no rule is MEDIUM. A model may raise a tier, never lower it | S5.1 |
| S5.3 | LOW tier auto-merges after all checks and verifiers pass | S5.2, S3 exit |
| S5.4 | Deploy with a post-deploy health check and **automatic rollback** to the previous release on failure | S5.1 |
| S5.5 | HIGH tier always requires your approval, whatever any council says | S5.2 |

**Exit:** twenty LOW-tier PRs auto-merged with zero escapes, and one rehearsed rollback.

### Step 6 — Intake, council, Kaizen (toward L4)

| ID | Task | Depends on |
|---|---|---|
| S6.1 | Intake trust boundary: external content (social posts, emails, web pages) is summarised by a tool-less model call into a fixed schema. Only that summary, never the raw content, reaches an agent that can write code or mint work | — |
| S6.2 | Triage: summary → issue draft with project slug and tier. Human confirms until triage accuracy is measured | S6.1 |
| S6.3 | Fast Council for triage and MEDIUM-tier merges; Full Council for architecture. Log every verdict and whether you overrode it | S6.2, S5 exit |
| S6.4 | Work-item IDs minted atomically (GitHub issue number is the ID; `RM-XXXX` is derived from it, not from a grep) | S6.2 |
| S6.5 | Weekly Kaizen report from the event log: failures by category, cost per item, cycle time, escape rate, council override rate | S1.5 |
| S6.6 | Second project onboarded | S5 exit |
| S6.7 | Prometheus metrics, health endpoints and the dashboard from architecture §3 | when SQL over the event log stops being enough |

**Exit:** a signal reaches production without you touching it, for LOW-tier work only, and the Kaizen report shows escape rate no worse than the Step 1 baseline.

---

## Autonomy levels and how to earn them

| Level | What runs without you | Earned by |
|---|---|---|
| **L1** | Build to PR | Step 1 exit |
| **L2** | Build + checks + verifiers; you review PRs only | Step 3 exit |
| **L3** | LOW-tier merge and deploy | Step 5 exit |
| **L4** | Intake to deploy for LOW tier; you set policy | Step 6 exit, sustained for four weeks |

Demotion rule: any escape on an auto-merged PR drops that project one level until the cause is fixed and recorded.

## Deliberately deferred

| Item | Add when |
|---|---|
| Parallel subagent fan-out within one spec | Single-agent builds are reliable and specs are large enough to split on disjoint modules |
| Overnight Mode / stacked PR chains | L2 is stable |
| Full metrics stack and dashboard | More than one project, or more items in flight than you can read in a query result |
| MicroVM isolation, credential-injection gateway | A project's threat model requires it |
| Third-party testing services | Step 3 shows the spec-only tester misses too much |

## Open questions to settle before Step 1

1. Which project is the pilot?
2. Where does Hermes sit? Recommended: Hermes triggers runs and sends notifications, while GitHub holds all state, so a Hermes outage loses nothing.
3. Which model plays each council seat, and what is the monthly budget ceiling?
