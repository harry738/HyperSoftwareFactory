# Software Factory — Build Plan

**Version:** v3 (2026-11-22) — replaces the phase tables formerly in section 4 of the reference architecture, and accounts for the working factory imported from the Binley pilot.

---

## Where we are

The walking skeleton exists. `factory/` and `.claude/` run a GitHub issue through intake → spec → build → gate → review → approve → merge, orchestrated by one Claude Code session (`/factory run`), with state in `factory/jobs/` and `factory/bin/job` as its only writer.

Evidence: **one pilot job** on Binley ([pilot report](binley/pilot-report-2026-11-21.md)). 38 minutes and $4.45 to an approved PR, 7 of 8 acceptance criteria met. It exercised the all-PASS path only, and the merge was done by hand after a Windows gate fault.

| Target capability (architecture §) | Working factory today | Gap |
|---|---|---|
| Work-item state machine | `factory/bin/job`, illegal moves refused, live dashboard | Windows job lock gives up after ~10s; `job advance` not safe to re-run |
| Intake and triage (§2.1) | `intake` agent on labelled GitHub issues; issue text quoted as data | No social/email/alert intake; no council |
| Spec (§2.2) | `spec-writer` agent | Spec can narrow acceptance criteria without escalation |
| Build (§2.3) | `builder` in a worktree per job, `max_rounds: 3`, `concurrency: 1` | Not exercised: change rounds, resume |
| Deterministic gate | `factory/bin/gate` runs `checks.sh`, fails closed until configured; `protected_paths` | No complexity or secret-scan check by default |
| Independent verification (§2.4) | Code, security, UI, UX reviewers routed by risk and surface; missing-review guard | Reviewers have Bash and Write, so read-only is by instruction, not enforced. A reviewer passed without opening the page. No spec-only tester |
| Security boundaries (§2.5) | Worktree per job on the operator's machine | No budget cap, timeout, egress control, or credential isolation |
| Risk-tiered merge (§2.6) | Risk from the intake agent; approver merges or escalates | Risk is model-judged, not path-based. Unattended merge blocked by the permission classifier. No deploy, no rollback |
| Observability (§3) | Per-job cost and time, dashboard | No cross-job event log; prices in `config.json` unverified |
| Multi-project | Copy `factory/` and `.claude/` into each repo | `config/projects.yaml` is not read by the factory |
| Kaizen (§2.8) | Hand-written pilot report | Not automated |

## Approach

1. **Harden what runs before adding stages.** One all-PASS job is not evidence. Every step below ends in a number of real jobs.
2. **Backpressure before forward pressure.** Checks, budgets and isolation land before anything that creates more work.
3. **Deterministic gates before LLM gates.** `checks.sh` and path rules are cheaper and harder to game than a model's opinion.
4. **Enforce in scripts and platform settings, not in prompts.** The factory already does this for state; extend it to reviewers, budgets and merge.
5. **One project until Step 4 exits.** Then use the second project to decide how the registry and the per-repo install fit together.

---

## Steps

Do not start a step until the previous one has exited.

### Step 0 — Repo hygiene (done 2026-11-22)

| ID | Task |
|---|---|
| S0.1 | Docs consistent: stage and gate counts, repo names, complexity gate definition |
| S0.2 | Onboarding script fixed, with a self-check (`scripts/test_factory_onboard.py`) |
| S0.3 | LICENSE, `.gitignore`, `requirements.txt` |
| S0.4 | Working factory imported; README separates what runs from what is planned |

### Step 1 — Make the skeleton reliable (autonomy L1)

Mostly the pilot report's own recommendations.

| ID | Task | Source |
|---|---|---|
| S1.1 | Decide who merges: a permission rule for `factory/bin/job merge`, or every job stops at `approve` for you | Pilot rec. 1 |
| S1.2 | Git sign-in through `gh` for every clone the factory runs in, set by a setup script rather than by hand | Pilot rec. 2 |
| S1.3 | One lock around `checks.sh` per worktree, so the builder and its Stop hook cannot run `npm ci` at once | Pilot rec. 4 |
| S1.4 | Make `job advance` safe to re-run (post the issue comment last, or skip if one exists) | Pilot rec. 7 |
| S1.5 | Rule for narrowed criteria: a spec that weakens an acceptance criterion is a rescope and must be escalated | Pilot rec. 8 |
| S1.6 | Verify the prices in `factory/config.json` against the published price list | Pilot rec. 10 |
| S1.7 | Per-job caps enforced by `factory/bin/job`: wall-clock timeout and USD budget in `config.json`; breach moves the job to `needs-human` | Architecture §2.5 |
| S1.8 | Branch protection on the project's base branch: PR required, gate status required | Architecture §2.4 |

**Exit:** ten real issues through the factory, including at least one gate failure, one CHANGES round, and one escalation. For each: cycle time, cost, whether you had to edit the PR (*human-edit rate*), and whether it was later reverted or hot-fixed (*escape rate*).

### Step 2 — Stronger deterministic backpressure

| ID | Task | Depends on |
|---|---|---|
| S2.1 | Add a complexity check to the project's `checks.sh`, implementing the complexity-delta definition in architecture §2.4 with an off-the-shelf tool | S1 exit |
| S2.2 | Add secret scanning and dependency audit to `checks.sh` | S1 exit |
| S2.3 | Ship these as commented examples in the template `factory/checks.sh` | S2.1, S2.2 |

**Exit:** at least 80% of jobs pass the gate on the builder's first push, and no job has merged with a finding these checks would have caught.

### Step 3 — Verification you can trust (autonomy L2)

| ID | Task | Depends on |
|---|---|---|
| S3.1 | Give the UI and UX reviewers a browser, and one dev server per worktree shared between them and stopped by port | Pilot rec. 3, 6 |
| S3.2 | Evidence rule in `factory/bin/job`: a review file without an evidence block (test output, log, screenshot path, diff reference) is recorded as INCONCLUSIVE, and a reviewer that could not exercise the change must say so | Architecture §2.4 |
| S3.3 | Reviewers cannot change the branch: after review, the script verifies the worktree's HEAD and tree are unchanged, and fails the round if not | Architecture §2.4 |
| S3.4 | Spec-only tester: an agent that writes tests from the spec's acceptance criteria and public interface, without the diff. Requires the spec template to state the public interface | Architecture §2.2, §2.4 |
| S3.5 | Run an issue with a security surface, so the security reviewer is exercised | Pilot rec. 9 |

**Exit:** on twenty jobs, compare reviewer verdicts with your own review. Proceed only if the reviewers miss fewer than one in ten of the issues you found.

### Step 4 — Isolation and concurrency

| ID | Task | Depends on |
|---|---|---|
| S4.1 | Make the Windows job lock wait instead of failing, and kill child processes when a script is stopped | Pilot rec. 5 |
| S4.2 | Raise `concurrency` to 2, then 3, only after S4.1 | S4.1 |
| S4.3 | Run the factory from a dedicated clone under an account or machine that holds no deploy secrets and no other projects' credentials | — |
| S4.4 | Daily USD budget per project, enforced by the scripts | S1.7 |
| S4.5 | Decide whether to move runs to ephemeral CI runners. Do it if the factory must run unattended overnight or S4.3 proves too weak | S4.3 |

**Exit:** twenty jobs at `concurrency` 3 with no lock crash, no port clash, and no orphaned process; a deliberately runaway job is stopped by its budget.

The microVM, service-mesh and credential-gateway designs in architecture §2.5 are the long-term target. Build them only if a threat model for a specific project shows the above is not enough.

### Step 5 — Risk-tiered merge and deploy (autonomy L3)

| ID | Task | Depends on |
|---|---|---|
| S5.1 | `risk_paths` in `factory/config.json`: high and medium globs. `factory/bin/route` computes the tier floor from changed paths; the intake agent may raise it, never lower it. No match = MEDIUM | S4 exit |
| S5.2 | LOW tier merges unattended after gate, reviews and approver all pass | S5.1, S3 exit |
| S5.3 | HIGH tier always stops for you, whatever the approver says | S5.1 |
| S5.4 | Deploy step with a post-deploy health check and automatic rollback to the previous release | S5.1 |

**Exit:** twenty LOW-tier jobs merged unattended with zero escapes, and one rehearsed rollback.

### Step 6 — Second project, intake, council, Kaizen (toward L4)

| ID | Task | Depends on |
|---|---|---|
| S6.1 | Install the factory in a second project. Decide then whether `config/projects.yaml` drives installs and updates, or is dropped | S5 exit |
| S6.2 | A way to update an installed factory from this repo without losing the project's `checks.sh` and `config.json` | S6.1 |
| S6.3 | Intake trust boundary for external content (social posts, emails, web pages): a tool-less model call summarises it into a fixed schema, and only the summary becomes a GitHub issue | — |
| S6.4 | Cross-job event log (one append-only row per stage transition) written by `factory/bin/job` | — |
| S6.5 | Weekly Kaizen report from that log: failures by category, cost per job, cycle time, escape rate, human-edit rate | S6.4 |
| S6.6 | Council gates, if the Kaizen data shows single-agent intake or approval is the weak point | S6.5 |
| S6.7 | Monitoring alerts as an intake source | S5.4 |

**Exit:** a signal reaches production without you touching it, for LOW-tier work only, with escape rate no worse than the Step 1 baseline.

---

## Autonomy levels and how to earn them

| Level | What runs without you | Earned by |
|---|---|---|
| **L1** | Issue to approved PR; you merge | Step 1 exit |
| **L2** | As L1, with reviewers you have measured | Step 3 exit |
| **L3** | LOW-tier merge and deploy | Step 5 exit |
| **L4** | Signal to deploy for LOW tier; you set policy | Step 6 exit, sustained for four weeks |

Current level on evidence: **L1, not yet earned** (one job of the ten).

Demotion rule: any escape on an unattended merge drops that project one level until the cause is fixed and recorded.

## Deliberately deferred

| Item | Add when |
|---|---|
| Parallel subagent fan-out within one spec | Single-builder jobs are reliable and specs are large enough to split on disjoint modules |
| Council (multi-model debate) | Kaizen data shows where a single agent's judgment fails |
| Prometheus metrics and health endpoints | The dashboard and the event log stop being enough |
| MicroVM isolation, credential-injection gateway | A project's threat model requires it |
| Context7, Modern Web Guidance | A job fails for a stale-API or web-platform reason they would have prevented |

## Open questions

1. Who merges (S1.1)? This blocks unattended runs.
2. Where does Hermes sit? Recommended: Hermes starts `/factory run` and sends notifications, while `factory/jobs/` and GitHub hold all state, so a Hermes outage loses nothing.
3. Which project is second, and does it need the central registry?
