# Software Factory — Build Plan

**Version:** v6.6 (2026-11-25) — the one roadmap. It consolidates the v6.5 release sequence, the deployable-roadmap phases, the agent roster, the feature list, the provider spec and the two Gemini plans; their decisions are in [Roadmap decisions](#roadmap-decisions) and the old files are archived under `docs/archive/roadmap-proposals-2026-11-25/`. v6.5 (2026-11-25) — six evidence-gated releases; assurance, isolation, scale and delivery engineering prioritised. v6.4 (2026-11-24) — adds four engine tasks from Binley's 24 Nov run (E2.5, E2.6, E3.5, E5.5). v6.3 (2026-11-24) adds FullAuto mode: an option the operator selects for a job, a run or a project, under which no job waits for a person, inside a policy the operator writes. v6.2 (2026-11-24) adds the lessons from Binley's second overnight run (23 Nov) to the engine track. v6.1 (2026-11-23) sets the operating model (a central factory, deployed as a container), puts the core engine first on a three-week timebox, and orders the features that follow. It was checked against thirteen comparable systems ([feature comparison](feature-comparison.md)). v5 closed Binley as the idea validation.

This repo is public. Nothing here names a real project, a private repo or a local path; those live in the factory's private home (see below).

---

## Objective

One factory that takes signals (issues, bugs, requirements, market changes) to deployed, verified, monitored software across the operator's own projects, with the operator setting policy and not reviewing every change.

## Release roadmap — authoritative sequence

This sequence supersedes the previous feature order and three-week estimate. E1–E6, F1–F8 and A1–A8 remain the detailed backlog and historical implementation record. No status has been promoted by this documentation change.

| Release | Capability focus | Exit criterion |
|---|---|---|
| R1 — Reliable factory | E1.6, CI failure classification, fail-closed merge, bounded checks, reproducible runtime, isolated workers (E2/E3/E6) | Ten supervised real jobs including seeded gate failure, CHANGES, escalation, runaway-stage kill and restart recovery; demonstrate credential/workspace isolation. |
| R2 — Verified factory | E4, structured specifications, independent holdout tests (F5), security and architecture gates, commit-bound evidence | Every accepted criterion has evidence; independently measure reviewer effectiveness; no missing required CI or stale review accepted. |
| R3 — Scalable factory | E5, durable scheduler, host-aware workers, conflict resolution, reserved budgets, second project (F7) | Three concurrent jobs across two projects without state corruption or budget-reservation violations; demonstrate worker-loss recovery. |
| R4 — End-to-end delivery factory | Hermes (F2), Operations Centre (E6.4), existing CI/CD, staging health checks and rollback (F6) | One issue reaches healthy staging; rehearse rollback and record outcome. |
| R5 — Learning factory | Project knowledge packs, Kaizen (F3/A8), controlled evaluations, shadow Dev council (F1) | Measurable improvement against baseline; independently recorded operator/council verdicts. |
| R6 — Evidence-gated autonomous factory | FullAuto (A1–A7), LOW-risk unattended merge and controlled deploy, market watch (F4), external intake (F8) | Per-project evidence gates met, sustained LOW-tier performance, proven recovery and explicit operator policy. |

## Roadmap decisions

Taken in v6.6. Each can be reversed by a reviewed change to this file, not by a proposal doc.

| # | Question | Decision |
|---|---|---|
| 1 | Which sequence is the spine? | The R1–R6 release table above. E/F/A identifiers stay as backlog IDs. |
| 2 | One phase vocabulary? | R1–R6 only. The deployable Phases 0–4 and the README tracks are retired; their items are mapped below. |
| 3 | Where do the deployable Phase 1 standards go? | R2.4: `AGENTS.md` checklist, Tier 1–3 mapped to low/medium/high, plan gate, ADR templates. |
| 4 | Is the model-provider layer in scope? | Spec at [reference/llm-provider-integration.md](llm-provider-integration.md). Scheduled as R5.3, after the durable scheduler (R3.1). Not before R3. |
| 5 | What may merge and deploy without a person? | Merging follows the R1.7 policy and the autonomy level, and always-stop rules come first. Deploy only in R4, with a rehearsed rollback. No unattended deploy before R6. |
| 6 | Fail-closed merge (issue #26)? | R1.2, first in order. An unattended merge needs the boolean `true` in `config.json`; a missing or other value means a person merges. |
| 7 | Can a council REWRITE exceed the round cap? | No. It stays inside the three-round cap, as [CONTEXT.md](../CONTEXT.md) requires. A sensitive path may be `stop` only (A2). |
| 8 | What happens to the Gemini plans? | 1.1 and 1.3 go to R2.4; 2.3 to R2.1; 3.2 to R2.3; 4.1 to R5.1; 4.2 to R5.2. Not adopted: the pnpm/Vitest/`tsc` stack rule, a global 90% coverage gate, multi-tenant scope, and the "autonomous" wording. Own projects only. |
| 9 | Where do the contested features go? | F5 holdout checks in R2. F7 second project and E5 concurrency in R3. F2 Hermes and F6 deploy in R4. F4 market watch and F8 intake in R6. |
| 10 | Which headline metric and thresholds? | The North Star in the measurement section. The L1–L4 thresholds in the evidence track of this file, not the README. Serial merging (R1.9) is not a merge queue. |

### Mapping of retired items

| Retired item | Where it lives now |
|---|---|
| Deployable Phase 0, standing gates (the fail-closed default, and the rule that the operator merges) | R1.2 and R6.1 |
| Deployable Phase 1, plan gate and Tier 1–3 | R2.4 |
| Deployable Phase 2, concurrency and flaky checks | E5.1 and R1.6 |
| Deployable Phase 3, artefact pack and the curator role | R5.1 |
| Deployable Phase 4, holdout checks, deploy and second project | R2 (F5), R4 (F6) and R3 (F7) |
| Agent roster, role cards and the model binding table | R2.4 and R5.2 |
| Feature list, its legend and delivery order | Replaced by the release table; the legend is kept in the decisions above |
| Gemini plans | Decision 8 |

### Priority engineering backlog

| ID | Priority | Work item | Acceptance / dependency |
|---|---|---|---|
| R1.1 | P0 | First real run (E1.6), readiness doctor, CI parity | Confirm target required checks and scoped credentials; capture complete issue-to-PR evidence. |
| R1.2 | P0 | Fail-closed merge defaults and config validation | Missing/invalid unattended setting denies automation; unknown policy or missing required CI never grants approval. Implemented in v6.6 (`job` and `run` allow an unattended merge only for the boolean `true`); its test is not yet verified, so the row is not Done. |
| R1.3 | P0 | CI classification and merge integrity (E2.6/E5.4/E5.5) | Separate code, infrastructure, quota, pending/missing checks; pause infra failures; pin expected head SHA; re-review material changes. |
| R1.4 | P0 | Bounded gate and budgets (E2/E3/E5.2) | Gate/lock timeout and cancellation; atomic aggregate budget reservations; treat unknown usage conservatively. |
| R1.5 | P0 | Runtime security (E6) | Trusted control plane; OS-enforced per-job/stage isolation, scoped mounts, explicit environment allowlists, independent reviewer/gate outputs, egress limits, no host credentials or Docker socket. Central container alone is packaging, not isolation. |
| R1.6 | P0 | Flaky checks (E3.5) | Record both attempts and instability; no unconditional PASS after a rerun; explicit quarantine policy and follow-up ticket. |
| R1.7 | P0 | PR policy | An ordered rule list per project in `config.json`; the first match wins. A rule is a condition and one action from a fixed set: `notify`, `label`, `rerun`, `update`, `round`, `merge`, `stop-line`. A script evaluates it at the start of every `factory run`, for every open PR in the project, not only factory jobs. No match means `notify`. `merge` applies only where the policy and the autonomy level both allow it. `rerun` applies only to failures R1.3 classifies as transient (a lost runner, a container that did not start); quota and billing failures pause. Depends on R1.3. |
| R1.8 | P0 | Stop the line | When the same check fails on three or more open PRs, or the base branch is red, no build round starts for that check and the operator is told once. Depends on R1.7. |
| R1.9 | P0 | One PR at a time | Merging is serial: bring the PR up to date with the base branch, wait for green, merge, then re-check the next PR. Always-stop rules and the R1.7 policy outrank it. Depends on R1.2 and R1.3. |
| R2.1 | P0 | Specification contract | Stable requirement/acceptance IDs, dependency and architecture/security constraints, out-of-scope and approved scope changes; no silently dropped criteria. Selectively adopt Spec Kit patterns. |
| R2.2 | P0 | Independent assurance (E3/E4/F5) | Holdout tests from spec without diff, inaccessible to builder; regression, SAST, secrets/dependency scanning, architecture/complexity, UI/accessibility as relevant. Trace criteria to tests or justified evidence. |
| R2.3 | P0 | Commit-bound PR evidence (E4.3/E4.4) | Candidate SHA, spec/check/reviewer evidence, independent reviewer evaluation; nonblocking findings become nonqueued issues. |
| R2.4 | P0 | Project standards (deployable Phase 1; Gemini 1.1, 1.3) | `AGENTS.md` and `CONTEXT.md` checklist with the readiness doctor; Tier 1–3 mapped to low, medium and high risk; a plan gate before any `src/` edit (the spec must exist first); ADR templates. The acceptance test is a spec before any source change on a sample of issues. |
| R3.1 | P1 | Durable scheduler (E5/F7) | Atomic claims, worker leases/heartbeat, recovery, priority/dependencies, physical-host capacity, project limits, reserved budgets; start with two then three disjoint jobs. |
| R4.1 | P1 | Release engineering (F6) | Existing CI/CD adapters, environment contracts, artifact identity, staging health checks, approved production boundary and rehearsed rollback. |
| R4.2 | P1 | Operations Centre and Hermes (E6.4/F2) | Read-only queue, worker health, costs, quality, evidence and release state; schedules and notifications without handing Hermes GitHub credentials; authenticated audited actions later. |
| R5.1 | P1 | Project knowledge engine (F3) | Versioned role-specific context packs: requirements, ADRs, API contracts, dependencies, security, tests and learnings. Markdown/YAML/code index first. |
| R5.2 | P1 | Kaizen and evaluations (F3/A8/F1) | Metrics from R1; regression corpus, controlled prompt/model/skill experiments, root cause, reviewed improvement PRs, shadow-only council. |
| R5.3 | P1 | Model-provider layer | Schema first, then adapters, per [reference/llm-provider-integration.md](llm-provider-integration.md). Retry the same model on 429 and 5xx; never fall back on 400, auth, policy or budget errors; data leaving the LAN denied by default. Not before R3.1. |
| R6.1 | P2 | Governed autonomy (A1–A7) | Separate implementation and activation; LOW tier initially; isolation, required CI, assurance, rollback and per-project evidence before operator opt-in. |
| R6.2 | P2 | External intake (F4/F8) | Tool-less summarisation of untrusted inputs, provenance, deduplication, approved proposals; no automatic queueing before policy permits. |

### Measurement and policy decisions

**North Star:** verified business outcomes delivered per unit of cost. Measure accepted requirements, cost per verified outcome, escaped defects and requirement coverage, operator minutes per accepted change, issue-to-deployment lead time, and change failure/recovery rates. Report sample sizes and definitions; missing metrics are unknown, not zero. Existing L1–L4 criteria remain additional autonomy gates.

Two v6.4 conflicts require an explicit policy decision: council rewrites beyond the three-round cap, and FullAuto judgement of sensitive/always-stop paths. Until a separately reviewed policy change, the stricter CONTEXT.md rules govern: no extra autonomous round and no override of always-stop paths. No council or model can override mechanical controls. Decline or operator handoff is preferable to an unsafe merge.

Source-level review: [aa8fe5e](https://github.com/harry738/HyperSoftwareFactory/commit/aa8fe5e0b83778bab4fead22e51b8619d4e43d6b). Not a live execution or penetration test; recheck the latest code before closing findings.

## Operating model

```
                    ┌──────────────── factory container (local Docker Desktop) ───────────────┐
 GitHub issues ───▶ │  factory run ──▶ intake ▶ spec ▶ build ▶ gate ▶ reviewers ▶ approver    │ ──▶ PR
 schedule / Hermes  │      │            (each stage is one headless Claude Code run)          │
                    │      ├─ per-project config  (private factory home, not the project repo) │
                    │      ├─ clones, worktrees, job state, event log                          │
                    │      └─ council slot ──▶ Dev council ──▶ MERGE / REWRITE / ESCALATE      │
                    └─────────────────────────────────────────────────────────────────────────┘
```

| Decision | What it means |
|---|---|
| Central, not per repo | One factory serves every project. Nothing from the engine is copied into a project repo. |
| Claude Code is the development engine | Every stage (intake, spec, build, review, approve) is a headless Claude Code run with its own agent definition. |
| The loop is a script | `factory run` owns the control flow and starts one stage at a time. No model decides what happens next. |
| Deployed as a container | Central control plane on local Docker Desktop with per-job or per-stage isolated workers before expanding trust. Linux/WSL first; central packaging alone is not an isolation boundary. |
| A private factory home | A small private repo holds the real project registry and each project's `checks.sh`, `setup.sh` and path rules. This public repo holds the engine and examples only. Secrets are in neither. |
| Project config stays out of the project | The builder cannot change the checks or rules it is judged by, because they are not in its worktree. |
| What a project repo does hold | Its own `AGENTS.md`, a `CONTEXT.md` (what the product is, its hard rules), a learnings file and a competitor list. All four are protected paths: agents read them, and they change only through a reviewed PR. |
| Interface | A command line (`factory onboard`, `factory run`, `factory status`) and the dashboard page. The dashboard is also the web console: served from the container and reachable from the operator's other devices through a private tunnel (E6.4). A web app for onboarding is a later feature. |
| Own projects only | Generality is added when a second project forces it. |
| Our own engine | Kept under GPLv3 in `factory/`. Designs are borrowed from other projects; whole tools are adopted only for components such as the sandbox. |

**Hermes.** Hermes runs a council and a Kaizen loop in the operator's current setup, by hand. The plan splits the two by what is at stake:

- **The Dev council runs in the engine, as a script.** It is meant to earn merge power, so it gets the same guarantees as the rest of the merge path: fixed control flow, enforced limits, and grading in the event log.
- **The market watch stays in Hermes.** It is not in the merge path, and Hermes already does the research. It drops its digest, competitor-list changes and proposals in a folder; the engine opens the PR and the issues, so Hermes holds no GitHub token.
- **Hermes also starts scheduled runs and sends notifications.**

All state stays in the factory and GitHub, so a Hermes outage loses nothing.

## What Binley validated

Binley Building Society is a fictional demonstrator. The factory ran 11 jobs on it by 22 Nov 2026 (about $2.50 a job in agent cost): ten merged, one rejected at intake. The factory merged one PR itself; a person merged the other nine, eight of them because the approver escalated under the project's always-stop rules. One job went through a CHANGES round, five ran the security reviewer, and none failed the gate. Only the first job has a written report ([pilot report](binley/pilot-report-2026-11-21.md)).

A second overnight run on 23 Nov put 18 more jobs through for $90.15, at `concurrency` 1. A job took between 15 minutes and 1.5 hours, mostly waiting on agents. Learnings 8 to 13 come from it.

Binley has no production, no users and no deploy. Its numbers show the mechanism works, not that it can be trusted, and its jobs do not count toward any autonomy level.

| # | Learning | What we do |
|---|---|---|
| 1 | Every escalation came from an always-stop rule, not from doubt about quality | Check label and path rules in a script before any model is asked (E3.1) |
| 2 | Enforcing in a script worked each time it replaced a prompt | Keep doing it: caps, rules, reviewer limits and merge all move into the engine |
| 3 | The approver was the only defence against a new CI workflow | Fixed: the gate rejects new files under protected paths |
| 4 | The gate will not fail by chance, because the builder runs the same checks first | Test it with a seeded failure (evidence track) |
| 5 | Acceptance criteria get narrowed or skipped on the way through (three of 11 jobs) | The approver escalates it today; the Dev council sees the original issue in its packet |
| 6 | Windows cost most of the debugging | The engine moves to Linux; the Windows patches are deleted once the container works |
| 7 | The judgment agents cost more than the build | Measure cost per agent in the event log, then try cheaper models where a script now does the checking |
| 8 | A cached PASS is not evidence: one PR passed the gate on a cache replay of tests that failed on a fresh run | The gate runs the checks with the build cache off (E3.4) |
| 9 | Reviewers replied without writing their review file in four of 18 jobs | The engine already goes by the file, not the reply. It sends that reviewer back in the same run (E4.5) |
| 10 | One shared line in a hot-spot file cost three rounds of merge conflicts | A merge-main round for open PRs after every merge (E5.4), and one entry per package in shared files |
| 11 | Two of 18 jobs blocked before writing code, because the environment lacked what the spec pinned (wheels, database extensions, runtime versions) | The container is built to match the project's CI (carried over) |
| 12 | The security reviewer's first round missed a temp-table bypass of ledger rules; the second round caught it | A SQL checklist in the project's own rules (carried over) |
| 13 | Every label-routed PR needed its label added by hand, and merge rules had to read the approver's prose | Gone with E3.1: the engine reads the label on the issue and records which rule fired |

## How others do it

The [feature comparison](feature-comparison.md) covers six open-source and seven commercial systems.

- **Every system that runs unattended is central or hosted in CI.** Everything installed per repo is driven by a person. That is why the operating model changed.
- **The control loop belongs in code.** The published orchestrator designs, and the largest public deployment, all keep the model inside a stage.
- **Taken from them:** stall detection and retry with backoff, a checkpoint after every stage, a feedback loop from the PR, a setup script per project, a network allowlist, a readiness check at onboarding, and evidence on the PR.
- **Where this plan is ahead:** risk tiers and path-based routing, specialist reviewers that cannot write, per-stage cost caps, and gate config kept outside the repo. None of the systems documents these.
- **Where this plan is alone:** no system lets agents approve and merge their own work without heavy mechanical checks. The Dev council's merge power is the least-precedented part, which is why it starts in shadow.

## Approach

1. **Engine first, then features.** The engine is everything deterministic: the loop, the state machine, the gate, routing, isolation, caps, the event log, merge, and the file formats agents write.
2. **Engine code does not wait for evidence; autonomy does.** Release exit criteria govern progression. What the factory may do without the operator is earned on measured jobs, or in FullAuto mode set by the operator's policy and adjusted by the factory from its own results.
3. **Backpressure before forward pressure.** Checks, budgets and isolation land before anything that creates more work.
4. **Enforce in scripts and platform settings, not in prompts.**
5. **One real project through R1/R2; the second in R3.**

---

## Engine track — retained work items

The original three-week estimate is historical. R1/R2 govern priority; E1.6 remains the first milestone.

Already done in this repo: the per-worktree checks lock, a re-runnable `job advance`, the gate rejecting new and renamed-in protected files, reviewers with a browser on one shared dev server, the evidence rule for reviews, reviewers added by sensitive path, a waiting job lock, `job merge` waiting for required CI, and project-neutral agents.

| ID | Task | Status |
|---|---|---|
| **E1** | **Factory home, and one job end to end** | |
| E1.1 | Factory home layout: registry, and per project a config folder with `checks.sh`, `setup.sh` and path rules. Every path the engine uses is relative to that home | Done. The registry is the `projects/` folder listing; each project records its repo in its `config.json` |
| E1.2 | `factory onboard <repo>`: clone the repo, create its config folder, check its credentials, and print a readiness checklist (fast checks, tests, CI, branch protection, `AGENTS.md`, `CONTEXT.md`). Replaces the old registry wizard | Done: `factory/bin/factory onboard` |
| E1.3 | `factory run <project>`: the script loop. One headless Claude Code run per stage, agents loaded from the factory and not from the project, all state on disk, safe to stop and restart | Done in code and tested end to end with stand-ins for GitHub and the model (`factory/test_run.py`). Not yet run with a real model |
| E1.4 | The engine does every push and every GitHub call. Agent stages run without the GitHub token, in a clone with no production credentials | Done. Agent stages run with the token removed from their environment; as the same OS user, hard separation waits for the container (E6) |
| E1.5 | The project's `setup.sh` runs once per worktree, with the package manager's cache shared across jobs | Done. The shared cache is the package manager's own store |
| E1.6 | First job on the first real project, from labelled issue to a PR waiting for the operator | Open. Needs the factory home, the project's token, a signed-in Claude Code CLI on the factory machine, and labelled issues |
| **E2** | **Limits, the log, and feedback** | |
| E2.1 | Per stage: wall-clock timeout, turn cap and USD budget, plus a stall kill when a stage has produced no output for some minutes. A breach sends the job to a person | Done: limits in `config.json`, enforced by `factory/bin/run`; `job stop` hands the job over and `job retry` puts it back. The CLI cost cap is passed too, but whether it applies on a subscription login is unverified, so the per-job budget is computed by the engine |
| E2.2 | Retry with backoff when a stage fails for a passing reason, such as a rate limit | Done: up to three more tries, resuming the failed session |
| E2.3 | Event log: one append-only typed row per stage transition, per project, with cost, time and outcome | Done: `events.jsonl` in the project job folder, written by `job` on every stage change. Per-stage cost and time are in each job folder `usage.jsonl` |
| E2.4 | Feedback loop: at the start of each run, a "changes requested" review or a failed CI check on a job's PR starts the next build round with that feedback, inside the three-round cap | Done, with one change: see the note under this table |
| E2.5 | The spec stage can hand a job to a person: the spec writer may answer "needs a split" (or "blocked"), and the job moves to `needs-human` with the reason. Today `spec` can only go to `build`, so a ticket over its own size limit sits in `spec` and holds a slot; on 24 Nov it took a stand-in spec and a blocked build to release it | Done: a `spec.md` whose first line is `STATUS: NEEDS-SPLIT` or `STATUS: BLOCKED` stops the job through `job stop`, with the reason on the issue; `job retry` writes the spec again |
| E2.6 | When CI jobs never start (a billing or quota annotation such as "The job was not started because recent account payments have failed"), the engine reports an infrastructure stop to the operator instead of a failed check, and stops merging or starting merge-dependent work. On 24 Nov every PR showed red checks for this reason | Done: when every failed check is a GitHub Actions job with no steps and no runner, no build round starts. During a merge the job stops in `merging` and the run ends; `job retry` re-runs those jobs and merges. The token needs Actions read and write. Not yet tried with a real fine-grained token |
| **E3** | **Rules in scripts** | |
| E3.1 | Always-stop rules: a `human-merge` label or a change under an always-stop path sends the job to the operator before any model is asked | Done: `job` checks the `human-merge` label and `sensitive_paths` when the reviews pass. A hit skips the approver and goes to the operator, and `job` refuses to merge it. `sensitive_paths` is the always-stop path list; there is no second list |
| E3.2 | Path-based risk floor: the tier is computed from changed paths; intake may raise it, never lower it; no match is MEDIUM | Done: `risk_paths` in `config.json`. Sensitive paths count as high. When the paths raise the tier, the reviewers are re-routed for it |
| E3.3 | A `council` stage in the state machine, in front of the hand-off to the operator. It passes straight through until the Dev council exists | Done: the stage exists and is switched on by a `council` key in `config.json`. Nothing sits in it yet, so `run` passes it through |
| E3.4 | The gate's run of `checks.sh` bypasses the project's build cache (for example `TURBO_FORCE=true`), or the cache is keyed per job | Done: the gate's run sets `FACTORY_GATE=1`, `TURBO_FORCE` and `NX_SKIP_NX_CACHE`, plus any switch in `gate_env` in `config.json`, and lists them in `checks.md`. The builder's own runs keep the cache |
| E3.5 | Flaky checks: the gate re-runs a failed end-to-end step once, records both results, and records instability rather than unconditional PASS; progression requires an approved quarantine policy. A test that flakes twice in a week becomes a follow-up issue. On 24 Nov four gate failures were flakes (a duplicate demo label during loading, axe `document-title` before the title is set, a 5 s test timeout under load from parallel builders), each passing on re-run | Open |
| **E4** | **Reviewers, and what the operator sees** | |
| E4.1 | Reviewer stages get read-only tools, set per stage by the engine | Done in code: `run` gives a reviewer the read tools and writes to its one review file, with no shell; the engine writes the commits and diff to `changes.diff` for it. The UI and UX reviewers keep `node` to drive the browser; `node` can write anywhere, and E4.2 only catches writes to the branch and worktree. Reviewers load no project settings and no MCP servers, so a branch cannot widen these limits. Also open: the CLI lets any reviewer write its memory folder. Tested with stand-ins; the rules have not yet met a real model |
| E4.2 | After review the engine checks the branch and tree are unchanged, and fails the round if not | Done: `run` compares the branch and tree with the commit the gate passed and hands the job to a person if they differ. It also writes `COMMIT:` in each review, and `job` refuses a review written for another commit |
| E4.3 | The engine posts the reviewers' summaries, their evidence and the check log on the PR | Done: after each review round `job` posts each reviewer's summary and evidence, and the last 60 lines of the check log, in one comment on the PR. Tokens and local paths are removed and nobody is @mentioned |
| E4.4 | Non-blocking reviewer notes become follow-up issues. They are not queued automatically | Done: the reviewers' `## Notes` become one issue per job, filed when the job leaves review for good, without the queue label |
| E4.5 | A reviewer that ends without writing its review file is sent back once in the same run, as a review without evidence already is | Done: `run` resumes that reviewer's session once and asks for the file, in the same retry as a review without evidence |
| **E5** | **Throughput** | |
| E5.1 | `concurrency` 2, then 3, starting with jobs on disjoint packages | Open |
| E5.2 | Daily USD budget per project | Done: `daily_budget_usd` in `config.json` (UTC days, 50 in the template). When today's spend across the project's jobs reaches it, `run` ends before the next stage and every job stays where it is for the next run |
| E5.3 | A scheduled run | Open |
| E5.4 | After a merge, the engine re-checks the project's open factory PRs for conflicts and starts a merge-main round for each | Done: at the start of a run and after each merge, a waiting job whose PR conflicts gets a round that merges the base, once per commit and inside the round budget (`job merge-main`). A person's pending PR comment goes first, a job a limit or safety check stopped is left alone, and a job that was waiting for a person is never then merged unattended |
| E5.5 | A review round can be abandoned when the base moves: if the PR becomes conflicting during review, the job goes straight back to `build` for a merge-main round. Today `job` refuses to leave `review` until every reviewer has reported, so stale reviews must finish first. Also note for E5.1: on one machine, parallel builders and gates slow each other enough to time tests out | Done: `run` checks before the reviewers start and again before using their verdicts; a conflicting PR goes back to `build` for the merge-main round |
| **E6** | **The container** | |
| E6.1 | Network allowlist: package registries, GitHub and the model API only | Done in `deploy/`: the factory container has no route out, and a proxy forwards HTTPS to listed hosts only. Verified with the built image on local Docker: `verify.py` passes, git and npm work through it |
| E6.2 | Dockerfile, and the factory deployed as a container on local Docker Desktop. Start from Anthropic's reference dev container and its firewall script | Done: the image builds and `factory/test_run.py` passes inside the container. Not yet run signed in, with a real model or project. The reference firewall script was dropped (it leaves DNS and SSH open) for an internal network and a proxy. Engine and agents are still one user, so E1.4's hard separation is still open |
| E6.3 | Delete the old path: the LLM-driven loop, install-by-copy, and the Windows patches | Open |
| E6.4 | The web console: the container serves the dashboard for every project in the factory home (it reads them since #37), bound to localhost inside a private tunnel such as Tailscale, so the operator can watch runs from another device without opening a port to the internet. Read-only: actions stay on the command line and in PR comments | Open |

**How the feedback loop is triggered (E2.4).** GitHub does not let an account request changes on its own PR, and the factory opens PRs as the operator. So a person asks for another round with a PR comment or review that starts with `/factory`; a changes-requested review works too when the factory runs under a separate account. Only the operator and the logins in `trusted_logins` count. Feedback from a person gets a fresh round budget, as `job feedback` always has. A failed CI check starts a round on its own, but only inside the existing round budget and once per pushed commit.

**Exit:** one command starts the container. A labelled issue on the first real project becomes a PR waiting for the operator with no manual step. A deliberately runaway stage is killed by its cap. Stopping and restarting `factory run` mid-job loses nothing.

---

## Evidence track — earning autonomy

Levels are per project and are earned on real jobs. This is the default mode, `supervised`: until the Dev council has earned merge power, every job stops for the operator. The operator can instead switch a project to FullAuto mode, described in the next section.

| Level | What runs without the operator | Earned by |
|---|---|---|
| **L1** | Issue to approved PR; the operator merges | Ten real jobs, including one seeded gate failure, one CHANGES round and one escalation. For each: cycle time, cost, whether the operator edited the PR, whether it was reverted or hot-fixed within 14 days, and whether it was escalated by a rule or by judgment |
| **L2** | As L1, with reviewers that have been measured | On twenty jobs the operator reviews each PR before reading the reviewers' verdicts. At least ten issues found in total, and the reviewers missed fewer than one in ten |
| **L3** | Merge for the LOW tier, defined by path | Twenty jobs where the Dev council's verdict matched the operator's own decision, then twenty LOW-tier merges with no escape, and one rehearsed rollback |
| **L4** | Signal to deploy for the LOW tier; the operator sets policy | L3 sustained for four weeks, with the Kaizen loop feeding the queue |

Rules that hold at every level:

- Always-stop rules by label and path outrank everything, including the Dev council. This remains true in FullAuto pending explicit reviewed policy change.
- A project may mark paths that never merge without the operator, whatever the level.
- Any escape on an unattended merge drops that project one level until the cause is fixed and recorded.

---

## FullAuto mode

A mode the operator selects, in which no job waits for a person to verify it. The engine decides by rule where a rule exists and asks a model where it does not, inside a policy the operator writes. It then checks its own results and changes what it allows itself.

`supervised` stays the default. FullAuto is an option a person opts into, the way a Claude Code session opts into a mode such as Ultracode: nothing runs in it unless someone selected it. It replaces the operator-agreement evidence of L2 and L3 with the factory's own record (A6, A7). Most of the merge path exists already: with `unattended_merge` on, an APPROVE from the approver merges after the merge gate and CI. What is missing:

| ID | Task | Status |
|---|---|---|
| A1 | Selecting the mode, at three levels. For one job: a `full-auto` label on the issue. For one run: `factory run <project> --full-auto`. As a project's default: `mode` in its `config.json`. The most specific choice wins, and a `supervised` label or `--supervised` turns it off the same way. The label counts only when the operator or a login in `trusted_logins` added it. `factory status`, the dashboard and each event-log row show the mode a job ran in | Open |
| A2 | A `policy` block in the project's `config.json`, replacing `unattended_merge`: the default `mode` (`supervised` or `full_auto`), the highest risk tier that may merge without a person (`ceiling`), what a sensitive path does (`stop` only until explicitly changed by reviewed policy), and a daily cap on merges. A project starts at the LOW tier | Open |
| A3 | A `policy.md` per project in the factory home: the operator's rules in plain language. The approver and the judge read it and name the rule they applied. It is not in the project repo, so a builder cannot change it | Open |
| A4 | A second look in place of a person. Where a job would go to the operator (the approver escalates, a review is blocked, the round limit or a cap is hit), the council slot (E3.3) runs a judge that returns MERGE, REWRITE or DECLINE. REWRITE uses only the remaining authorised round budget; otherwise decline or hand off. DECLINE closes the PR and writes the reason on the issue; nothing waits. One seat to start with, on a different model from the builder. The Dev council (F1) takes the seat when it is built | Open |
| A5 | A watch after the merge. The engine waits for the base branch's CI, and for the deploy health check once F6 exists. A failure merges a revert, logs an escape and sends the job back for one round with the failure as feedback | Open |
| A6 | Grading. Fourteen days after each merge the engine records whether it was reverted or hot-fixed, next to the verdict and the rule that allowed it | Open |
| A7 | The factory changes its own allowance, kept in a state file in the factory home. An escape takes that tier out of unattended merge at once. A run of clean graded merges (`promote_after`, twenty to start with) adds the next tier, never past the `ceiling` | Open |
| A8 | Learnings written by the engine. Each CHANGES round, DECLINE and escape adds a dated entry to the project's learnings file from a fixed template, and a weekly run condenses the file. Both go through the factory as ordinary jobs | Open |

Rules that hold in FullAuto mode:

- Only a person selects the mode. No agent, and not the factory itself, can turn it on.
- Selecting the mode does not lift the policy: the tier ceiling, the sensitive-path rule and the caps still apply.
- The gate, required CI and protected paths are never judged. A branch that fails the checks or touches a protected path does not merge in any mode.
- A `human-merge` label on an issue still sends that job to a person. That is a person asking, not the factory needing one.
- The factory may tighten its own allowance freely and loosen it only up to the `ceiling`. It never edits `config.json` or `policy.md`.
- Every unattended decision is in the event log, with the rule or the verdict that made it.

What the mode cannot do:

- It learns only from failures it can see: a failed check, a failed health check, a revert. A change that passes every check and is still wrong is not caught, so the mode is only as good as the project's checks. Holdout checks (F5), the deploy health check (F6) and monitoring alerts (F8) are what raise that.
- It does not answer an unclear issue. Intake still asks on the issue (NEEDS-INFO) and the job continues when someone answers.

**Order.** R1/R2 assurance precedes activation. A1–A3 may be implemented after E4, A5 recovery rehearsed in R4, A4 shadow-only in R5, A6/A8 measurement begins early; A7 and activation await R6 and existing evidence gates.

---

## Features — retained identifiers

R2: F5; R3: F7; R4: F2/F6; R5: F3/F1 (measurement from R1); R6: F4/F8. Release roadmap governs sequencing.

### F1 — Dev council, in shadow

A council of models that debates a contested job and decides what happens to it.

- **When it is called.** Wherever a job would otherwise come to the operator: the approver escalates, a stage is blocked, the round limit is hit, or a review is needed. It does not replace the gate, the reviewers or the approver.
- **What it returns.** MERGE, REWRITE or ESCALATE. REWRITE is a recommendation within the existing three-round cap; an extra round requires a reviewed policy change. A split escalates.
- **Who sits on it.** Three seats from three different labs (Architect, Risk, Product) and a Chair from a fourth. The seat-to-model mapping is configuration, and a project can override it.
- **How it debates.** Two rounds: independent positions, then one rebuttal where seats see each other. Every answer ends in a structured close: position, confidence, weakest premise, cheapest test.
- **What it sees.** An evidence packet built by the engine: the issue, the spec, the diff, the gate result, the reviews, the project's `CONTEXT.md` and its learnings file. Seats have no tools. They cannot run code, read the repo or push; the engine carries out the verdict.
- **Shadow first.** The council records its verdict, the operator decides independently, and the engine logs whether they agreed. Merge power is granted per risk tier once agreement holds (L3).
- **Grading.** Every verdict is graded later, first against the operator's decision and then against whether the change was reverted or hot-fixed. Accuracy is tracked per seat, so a weak seat or model can be swapped.
- **Limits.** Each session has a hard cost ceiling, starting at $5 and reset after the first five sessions are measured. A malformed answer gets one retry. The run aborts if a configured model does not exist.
- **Runner.** A script in the engine that calls the models directly through one API gateway. Its key lives in the factory's secrets, where no agent can read it. Hermes can later call the same script for product decisions, so there is one set of council rules.

Sending diffs and project context to several model vendors is a data decision for each project, set in its config.

### F2 — Hermes: scheduled runs and notifications

Hermes starts `factory run` on a schedule and tells the operator when a job needs them, a PR is ready, or a cap was hit.

### F3 — Weekly Kaizen, inside view

- A report from the event log: the five DORA measures, plus escalation rate, operator-edit rate, cost per job and council agreement.
- The learnings file: a tracked file in the project's repo, fed by the operator's rejections and by CHANGES rounds, read by the spec-writer and the builder, and curated by the operator each week through a PR.

### F4 — Weekly Kaizen, outside view

- A market watch per project, run by Hermes: competitor changelogs, release notes and blogs, GitHub, Hacker News and Reddit to begin with. Sources that need a login or paid access come later.
- Hermes writes its output to a drop folder in a fixed format. The engine reads it and makes every GitHub call.
- An active competitor list, kept as a tracked file in the project's repo. The factory is registered as one of its own projects; its list is [competitors.md](competitors.md).
- Each week the engine opens one PR with the dated digest and any changes to the list, and files the ideas as proposal issues. A proposal is never queued automatically: the operator decides, and the Dev council may take over triage for a project once it has merge power there.
- External text passes through a summariser with no tools before any agent that can act sees it.

### F5 — Holdout checks

A tester writes tests from the spec's acceptance criteria and public interface, without the diff, and the builder never sees them.

### F6 — Deploy and rollback

A deploy step with a health check afterwards and an automatic rollback to the previous release.

### F7 — A second project

Onboarded with `factory onboard`. Whatever the second project needs that the first did not is where generality gets added.

### F8 — Other external intake

Monitoring alerts and other sources, through the same tool-less summariser as F4.

### Carried over, not yet scheduled

| Task | Where it goes |
|---|---|
| Complexity check, secret scan and dependency audit as examples in the template `checks.sh` | With the first project that lacks them; the readiness checklist reports the gap |
| Verify the prices in `factory/config.json` against the published price list | Before the first cost figures are relied on |
| A rule for narrowed acceptance criteria that a script can check | When the event log shows how often it happens |
| CI parity: the spec-writer checks the environment has what the spec pins, and the builder is told where CI differs (slower, another OS or runtime) | With the container (E6.2), built to match the project's CI; sooner if a real job blocks on it |
| SQL checklist for the security reviewer: schema-qualify every name in triggers and definer functions, pin `search_path` with `pg_temp` last, and test as the app role with shadowing temp tables | With the first project that has them, in that project's own rules; the agents stay project-neutral |
| Copy the route label from the issue to the PR | Only if a project's GitHub merge rule reads PR labels. The engine's own rule reads the issue (E3.1) |
| Remove a merged job's worktree in the background | If it still holds up `factory run` on Linux; it took minutes on Windows |

Three items from the 23 Nov run need no work:

- **Hand merges are detected.** `factory run` asks `job queue` at the start of every run and between jobs, and that moves a job whose PR was merged by hand to `merged`.
- **A machine-readable "label only" line from the approver.** The always-stop rule is now checked by a script, and each event-log row records the rule that fired (E3.1).
- **Porting Binley's later factory changes back.** Checked on 24 Nov: since the harvest, Binley's factory files changed once, for a rule that belongs to that project.

---

## Sources consolidated

- `reference/build-plan.md` v6.4 on main: the engine table and the evidence track. Kept.
- Build plan v6.5 (PR #42): the release sequence and the backlog. Kept, with its status column refreshed to main and R1.7 to R1.9 added.
- `docs/roadmap/deployable-roadmap.md`, `feature-list-by-phase.md` and `agent-roster.md`, and the two Gemini plans: archived under `docs/archive/roadmap-proposals-2026-11-25/`. Their unique content is in the mapping above.
- `docs/roadmap/llm-provider-integration.md`: moved to `reference/` as a spec.
- The two review documents on main: archived with the proposals.

## Non-goals

- Steering a run while it is in progress. Feedback goes in between rounds.
- Other models for the builder or the reviewers. Only council seats use other vendors.
- A merge queue, a webhook server, a mobile app.
- Parallel builders inside one spec, Prometheus metrics, microVM isolation. Each waits for evidence that it is needed.

## Open questions

1. What exactly does Hermes write to the drop folder, and how does it start `factory run` on a schedule? Both need a look at the Hermes setup, which this plan was written without.
2. Does the first real project have a deploy that can be rolled back (F6)?
3. Do the model subscription's terms allow unattended runs? The documentation read for this plan does not say. FullAuto mode depends on the answer.
4. Does the CLI's cost cap apply on a subscription login? Until that is known, the engine keeps its own cap computed from the run's usage.

## What only the operator can do

- Create the private factory home repo.
- Create a fine-grained GitHub token per project (contents, pull requests, issues, and actions read and write to see and re-run CI that never started; no workflow scope, no admin), the model login token for the container, and the key for the council's models.
- Label the first few low-risk issues on the first real project.
