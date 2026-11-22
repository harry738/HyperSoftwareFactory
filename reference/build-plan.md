# Software Factory — Build Plan

**Version:** v5 (2026-11-22) — Binley is closed as an idea-validation project and its later fixes are harvested into this repo. The plan now carries its learnings forward and earns autonomy on a real project. v4 added a status per task; v3 replaced the phase tables formerly in section 4 of the reference architecture.

---

## Objective

One factory that takes signals (issues, bugs, requirements, alerts) to deployed, verified, monitored software across the operator's real projects, with the operator setting policy and not reviewing every change. That is L4 in the table below.

Binley tested whether the idea works at all. It does. Everything from here is measured on a real project.

## What Binley validated

Binley Building Society is a fictional demonstrator. The factory ran 11 jobs on it by 22 Nov 2026 (jobs 001–011, $27.93 in agent cost, about $2.50 a job).

- Ten merged and one was rejected at intake.
- The factory merged one PR itself with `factory/bin/job merge` (job 005). A person merged the other nine: the pilot after a Windows gate fault, and eight because the approver escalated.
- One job went through a CHANGES round, and five ran the security reviewer.
- No job failed the gate.

Only the pilot has a written report ([pilot report](binley/pilot-report-2026-11-21.md): 38 minutes and $4.45 to an approved PR, 7 of 8 acceptance criteria met). The other figures come from `factory/jobs/` in the Binley factory clone, which this repo does not hold.

**What Binley cannot tell us.** It has no production, no users and no deploy, one stack (Next.js), and issues written by the operator for the factory. So there is no escape rate, no human-edit rate, no rollback and no external intake behind any of the numbers above. They show the mechanism works, not that it can be trusted.

### Learnings carried forward

| # | Learning | Evidence | What we do |
|---|---|---|---|
| 1 | Escalations came from the project's always-stop rules, not from doubts about quality | All eight: five `human-merge` labels, two new CI workflows, one skipped criterion. In six the approver found nothing to change | Check label and path rules in a script before the approver runs (S1.13). Count rule and judgment escalations separately |
| 2 | Enforcing in a script worked each time it replaced a prompt | Binley added, after its trials: an evidence rule for reviews, reviewers by sensitive path, a block on hand merges, a wait for CI before merge | Harvested (S0.6, S0.7). Keep approach rule 4 |
| 3 | The approver was the only defence against a new CI workflow | Two jobs added `.github/workflows/*.yml`; the gate passed both, because it ignores added files | Fix the gate (S1.9) |
| 4 | The gate will not fail by chance | 11 jobs, no gate failure: the builder's Stop hook runs the same checks first | Treat the gate as tamper resistance, and test it with a seeded failure (S1.11) |
| 5 | Acceptance criteria get narrowed or skipped on the way through | Three of 11 jobs (the pilot, 002, 011). The approver caught the two after the pilot | Keep the rule (S1.5) and move it out of the prompt when a check is possible |
| 6 | Windows cost most of the debugging | Half of the pilot's twelve problems were Windows-specific in whole or part: lock, bash lookup, orphaned processes, credential prompt | Fixed in code. The setup script (S1.2) is the remainder |
| 7 | The judgment agents cost more than the build | Pilot: intake, spec and approver were 74% of the cost; the spec alone cost more than the build | Once S1.13 takes the rule checks off the approver, and S1.10 records cost per agent, try cheaper models there |

## Where the code is

`factory/` and `.claude/` in this repo are the factory as Binley left it on 22 Nov 2026, made project-neutral. It has not been installed anywhere else yet.

| Target capability (architecture §) | In this repo today | Gap |
|---|---|---|
| Work-item state machine | `factory/bin/job`, illegal moves refused, live dashboard; the job lock waits, `job advance` and worktree cleanup are safe to re-run, and one stuck job does not stop the queue | Not run above `concurrency` 1 |
| Intake and triage (§2.1) | `intake` agent on labelled GitHub issues; issue text quoted as data | No social/email/alert intake; no council |
| Spec (§2.2) | `spec-writer` agent; the approver is told to escalate a spec that narrows a criterion | That rule is in a prompt, not a script |
| Build (§2.3) | `builder` in a worktree per job, `max_rounds: 3`, `concurrency: 1` | One CHANGES round so far |
| Deterministic gate | `factory/bin/gate` runs `checks.sh` under a per-worktree lock, fails closed until configured; `protected_paths` | A new file, or one renamed in, under a protected path passes. No complexity or secret-scan check by default |
| Independent verification (§2.4) | Code, security, UI, UX reviewers routed by risk and surface, and by `sensitive_paths`; missing-review guard; a review with no `## Evidence` citing a path and line is refused; UI and UX reviewers drive the page on one shared dev server, and a reviewer that cannot open it sends the job to a human | Reviewers have Bash and Write, so read-only is by instruction, not enforced. No spec-only tester |
| Security boundaries (§2.5) | Worktree per job on the operator's machine | No budget cap, timeout, egress control, or credential isolation |
| Risk-tiered merge (§2.6) | Risk from the intake agent; approver merges or escalates; `job merge` waits for required CI; template permission rules and a hook that blocks hand merges | Risk is model-judged, and the always-stop rules live in the approver's prompt. No deploy, no rollback |
| Observability (§3) | Per-job cost and time, dashboard | No cross-job event log; human-edit and escape rates not recorded; prices in `config.json` unverified |
| Multi-project | Copy `factory/` and `.claude/` into each repo | Never installed outside Binley. `config/projects.yaml` is not read by the factory |
| Kaizen (§2.8) | Hand-written pilot report | Not automated |

## Approach

1. **Harden what runs before adding stages.** Eleven jobs on a demonstrator are not evidence. Every step below ends in a number of jobs on a real project.
2. **Backpressure before forward pressure.** Checks, budgets and isolation land before anything that creates more work.
3. **Deterministic gates before LLM gates.** `checks.sh` and path rules are cheaper and harder to game than a model's opinion.
4. **Enforce in scripts and platform settings, not in prompts.** The factory already does this for state; extend it to reviewers, budgets and merge.
5. **One real project until Step 4 exits.** Then use the second to decide how the registry and the per-repo install fit together.

---

## Steps

Steps gate autonomy, not code. A task from a later step may land early when a real job needs it, as several pilot fixes did. An autonomy level is not claimed until its step and every step before it have exited.

Status is **Done** (in this repo), **Partly**, or **Open**. Task IDs are stable and do not imply order within a step.

### Step 0 — Close out Binley

Take everything Binley learned into the project-neutral factory, so the next install starts from the best version.

| ID | Task | Status |
|---|---|---|
| S0.1 | Docs consistent: stage and gate counts, repo names, complexity gate definition | Done |
| S0.2 | Onboarding script fixed, with a self-check (`scripts/test_factory_onboard.py`) | Done |
| S0.3 | LICENSE, `.gitignore`, `requirements.txt` | Done |
| S0.4 | Working factory imported; README separates what runs from what is planned | Done |
| S0.5 | Agents project-neutral: the approver and the security, UI and UX reviewers read the project's rules from `AGENTS.md` (or `CLAUDE.md`) and `sensitive_paths`, not from Binley's file list, label and audience | Done |
| S0.6 | Harvest Binley's later factory fixes into the neutral copy: evidence rule for reviews, reviewers added by `sensitive_paths`, `job merge` waits for required CI, worktree cleanup safe to repeat, one stuck job no longer stops `job queue`, rejection clears `ready-for-agent`, the Stop hook skips checks that already passed on the same commit | Done |
| S0.7 | Template permission rules and hook: allow the factory scripts including `job merge`, deny `gh pr merge` and force-push, block hand merges, add `.claude/*` to `protected_paths` | Done: `factory/settings.example.json` and `.claude/hooks/no-hand-merge.py`. The rules are a template, not live in this repo |

**Exit:** the factory installs into the first real project by copying, with edits only to `checks.sh`, `config.json` and the permission rules. Outside `reference/binley/`, nothing names Binley except the `# binley:` patch markers.

The tasks are done and `factory/test_factory.py` passes. The exit itself waits on the first install (S1.12).

### Step 1 — Reliable on the first real project (autonomy L1)

| ID | Task | Source | Status |
|---|---|---|---|
| S1.1 | Decide who merges: a permission rule for `factory/bin/job merge`, or every job stops at `approve` for you | Pilot rec. 1 | Decided for Binley (the rule, limited by the approver's always-stop list). The rule ships in the template (S0.7). For a real project, see open question 2 |
| S1.2 | Git sign-in through `gh` for every clone the factory runs in, set by a setup script rather than by hand | Pilot rec. 2 | Partly: the scripts make git fail instead of prompting, and the two commands are in `binley/running-the-factory.md`. No script |
| S1.3 | One lock around `checks.sh` per worktree, so the builder and its Stop hook cannot run `npm ci` at once | Pilot rec. 4 | Done |
| S1.4 | Make `job advance` safe to re-run (post the issue comment last, or skip if one exists) | Pilot rec. 7 | Done |
| S1.5 | Rule for narrowed criteria: a spec that weakens an acceptance criterion is a rescope and must be escalated | Pilot rec. 8 | Partly: in the approver's prompt, not enforced by a script |
| S1.6 | Verify the prices in `factory/config.json` against the published price list | Pilot rec. 10 | Open |
| S1.7 | Per-job caps in `config.json`: wall-clock timeout and USD budget, checked by `factory/bin/job` at every transition; breach moves the job to `needs-human`. `job` runs between stages, so this does not stop a stage that is still running (see S4.6) | Architecture §2.5 | Open |
| S1.8 | Branch protection on the project's base branch: PR required, and `checks.sh` run in CI as a required check | Architecture §2.4 | Partly: `job merge` waits for required CI. Each project needs its own ruleset and CI workflow |
| S1.9 | The gate rejects a new file, or one renamed in, under `protected_paths`. Today it checks modified and deleted files only, so a new `.github/workflows/*.yml` passes | Learning 3 | Open, in Binley too |
| S1.10 | Cross-job event log: one append-only row per stage transition, written by `factory/bin/job`, with human-edit and escape recorded per job. Moved up from S6.4, because this step's exit needs the numbers | Architecture §3 | Open |
| S1.11 | Seed a gate failure: run an issue that needs a change under a protected path | Learning 4 | Open |
| S1.12 | Install the factory in the first real project, with its own `checks.sh`, `protected_paths`, `sensitive_paths` and branch ruleset | — | Open, waits on open question 1 |
| S1.13 | Always-stop rules in a script: `factory/bin/job` sends a job to a human on a `human-merge` label or a change under an always-stop path, before the approver runs | Learning 1 | Open |

**Exit:** ten real issues through the factory on that project, including at least one gate failure, one CHANGES round, and one escalation. For each: cycle time, cost, whether you had to edit the PR (*human-edit rate*), whether it was reverted or hot-fixed within 14 days of merge (*escape rate*), and whether it was escalated, by a rule or by the approver's judgment (*escalation rate*).

Binley's 11 jobs validated the mechanism and do not count toward this.

### Step 2 — Stronger deterministic backpressure

| ID | Task | Depends on | Status |
|---|---|---|---|
| S2.1 | Add a complexity check to the project's `checks.sh`, implementing the complexity-delta definition in architecture §2.4 with an off-the-shelf tool | S1 exit | Open |
| S2.2 | Add secret scanning and dependency audit to `checks.sh` | S1 exit | Open |
| S2.3 | Ship these as commented examples in the template `factory/checks.sh` | S2.1, S2.2 | Open |

**Exit:** over at least ten jobs, 80% or more pass the gate on the builder's first push, and no job has merged with a finding these checks would have caught.

### Step 3 — Verification you can trust (autonomy L2)

| ID | Task | Depends on | Status |
|---|---|---|---|
| S3.1 | Give the UI and UX reviewers a browser, and one dev server per worktree shared between them and stopped by port | Pilot rec. 3, 6 | Done |
| S3.2 | Evidence rule in `factory/bin/job`: a review file without an evidence block (test output, log, screenshot path, diff reference) is not accepted, and a reviewer that could not exercise the change must say so | Architecture §2.4 | Done: a review with no `## Evidence` citing a path and line is refused, and a reviewer that cannot open the page writes BLOCKED and the job goes to a human |
| S3.3 | Reviewers cannot change the branch: after review, the script verifies the worktree's HEAD and tree are unchanged, and fails the round if not | Architecture §2.4 | Open |
| S3.4 | Spec-only tester: an agent that writes tests from the spec's acceptance criteria and public interface, without the diff. Requires the spec template to state the public interface | Architecture §2.2, §2.4 | Open |
| S3.5 | Run an issue with a security surface, so the security reviewer is exercised | Pilot rec. 9 | Done on Binley: five jobs |
| S3.6 | Sensitive-path routing: a change under a sensitive path gets the security reviewer whatever intake said | Learning 2 | Done: `sensitive_paths` and `sensitive_reviewers` in `config.json` |

**Exit:** on twenty jobs, review each PR yourself before reading the reviewers' verdicts, then compare. Proceed only if you found at least ten issues in total and the reviewers missed fewer than one in ten of them.

### Step 4 — Isolation and concurrency

| ID | Task | Depends on | Status |
|---|---|---|---|
| S4.1 | Make the Windows job lock wait instead of failing, and kill child processes when a script is stopped | Pilot rec. 5 | Done |
| S4.2 | Raise `concurrency` to 2, then 3, only after S4.1 | S4.1 | Open |
| S4.3 | Run the factory from a dedicated clone under an account or machine that holds no deploy secrets and no other projects' credentials | — | Open |
| S4.4 | Daily USD budget per project, enforced by the scripts | S1.7 | Open |
| S4.5 | Decide whether to move runs to ephemeral CI runners. Do it if the factory must run unattended overnight or S4.3 proves too weak | S4.3 | Open |
| S4.6 | Watchdog that stops a running stage when its job breaches the S1.7 caps | S1.7 | Open |

**Exit:** twenty jobs at `concurrency` 3 with no lock crash, no port clash, and no orphaned process; a deliberately runaway job is stopped by its budget.

The microVM, service-mesh and credential-gateway designs in architecture §2.5 are the long-term target. Build them only if a threat model for a specific project shows the above is not enough.

### Step 5 — Risk-tiered merge and deploy (autonomy L3)

| ID | Task | Depends on | Status |
|---|---|---|---|
| S5.1 | `risk_paths` in `factory/config.json`: high and medium globs. `factory/bin/route` computes the tier floor from changed paths; the intake agent may raise it, never lower it. No match = MEDIUM | S4 exit | Open |
| S5.2 | LOW tier merges unattended after gate, reviews and approver all pass | S5.1, S3 exit | Open |
| S5.3 | HIGH tier always stops for you, whatever the approver says | S5.1 | Open; S1.13 is its first half |
| S5.4 | Deploy step with a post-deploy health check and automatic rollback to the previous release | S5.1 | Open |

**Exit:** twenty LOW-tier jobs merged unattended with zero escapes, and one rehearsed rollback. Zero in twenty shows the escape rate is probably under about 14%, not that it is zero.

### Step 6 — Second project, intake, council, Kaizen (toward L4)

| ID | Task | Depends on | Status |
|---|---|---|---|
| S6.1 | Install the factory in a second real project. Decide then whether `config/projects.yaml` drives installs and updates, or is dropped | S5 exit | Open |
| S6.2 | A way to update an installed factory from this repo without losing the project's `checks.sh` and `config.json` | S6.1 | Open |
| S6.3 | Intake trust boundary for external content (social posts, emails, web pages): a tool-less model call summarises it into a fixed schema, and only the summary becomes a GitHub issue | — | Open |
| S6.4 | Moved to S1.10 | — | — |
| S6.5 | Weekly Kaizen report from the event log: failures by category, cost per job, cycle time, escape rate, human-edit rate, escalation rate | S1.10 | Open |
| S6.6 | Council gates, if the Kaizen data shows single-agent intake or approval is the weak point | S6.5 | Open |
| S6.7 | Monitoring alerts as an intake source | S5.4 | Open |

**Exit:** a signal reaches production without you touching it, for LOW-tier work only, with escape rate no worse than the Step 1 baseline.

---

## Autonomy levels and how to earn them

Levels are per project, and are earned on a real one.

| Level | What runs without you | Earned by |
|---|---|---|
| **L1** | Issue to approved PR; you merge | Step 1 exit |
| **L2** | As L1, with reviewers you have measured | Step 3 exit |
| **L3** | LOW-tier merge and deploy | Step 5 exit |
| **L4** | Signal to deploy for LOW tier; you set policy | Step 6 exit, sustained for four weeks |

Current level: **none earned**. Binley showed the mechanism works, including one unattended merge, but no real project has run a job.

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

1. Which real project is first? It needs real users or a production, a deploy that can be rolled back (for S5.4), a test suite that can become `checks.sh`, and a small blast radius. The registry lists the Hyper Trading System and HyperAISystemsOS. HTS moves live capital, so its always-stop list would be long.
2. Does the factory merge unattended on a real project from day one? Recommended: no. Every job stops at `approve` until S1.9 and S1.13 are in, because until then a prompt is the only thing holding the always-stop rules. That is also what L1 says.
3. Where does Hermes sit? Recommended: Hermes starts `/factory run` and sends notifications, while `factory/jobs/` and GitHub hold all state, so a Hermes outage loses nothing.
4. Does the second real project need the central registry (S6.1)?
