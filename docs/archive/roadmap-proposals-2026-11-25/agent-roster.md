> **Archived 25 Nov 2026.** Historical proposal, superseded by [reference/build-plan.md](../../../reference/build-plan.md) (one roadmap). Its status claims and links are not maintained.

# Agent roster (proposal)

Proposal only. Roles are for a multi-agent split of the deployable roadmap. They map onto agents and scripts that already exist in HyperSoftwareFactory where those exist. The operator remains the only merger and the only person who can approve Tier 3 plans, FullAuto, or going live. Auto-merge and auto-deploy are not adopted.

Least privilege is already a factory rule: the script owns GitHub; agent stages run without the GitHub token; reviewers are read-only; Hermes, when built, holds no GitHub token. A test or research helper must not gain merge or production credentials.

**Hard rules, in addition to that.** **Never-self-merge:** the factory never merges its own work ([Gumloop, entry 13](../reference-library/13-gumloop-software-factory.md)); the author of a change does not approve it ([Itamar Friedman, entry 11](../reference-library/11-itamar-friedman-software-factory-engineer.md)). **Autonomy stays at L2 (workflow-orchestrated)** ([Agent Baseline, entry 14](../reference-library/14-agent-baseline-secure-software-factory.md)): the orchestrator script chooses the next step; agents never grant themselves access; L3 and L4 are out of scope. Every role sits inside four security boundaries (entry 14): **sandbox**, **network**, **supply chain**, and **identity/access**.

## Orchestrator (script, not a model)

| | |
|---|---|
| **Maps to** | `factory run`, `factory/bin/job`, `factory/bin/gate`, `factory/bin/route` |
| **Owns** | Control flow for every job: which stage runs next, budgets, retries, always-stop rules, event log, starting and stopping agents. Also the LLM provider router in `docs/roadmap/llm-provider-integration.md` (role bindings, fallback, rate limits, usage rows). The orchestrator itself has **no model** |
| **Inputs** | Labelled issues, `config.json`, job state, gate results, reviewer files, CI status |
| **Outputs** | Stage transitions, `events.jsonl`, PRs opened through the engine, stops for a person |
| **Tools / access** | GitHub token (contents, PRs, issues, actions read/write as in v6.4). No workflow-admin scope. This is the **only** role that should hold that token |
| **The operator's approval** | Cannot merge unless `unattended_merge` is on **and** #26 has been fixed to fail closed — and this plan keeps unattended merge off, so the orchestrator always stops for the operator at merge |

This is Gemini's "platform" and IBM's "main agent stays on planning and orchestration," implemented as a script so a model does not choose the next step (v6.4).

## Discovery / Spec agent

| | |
|---|---|
| **Maps to** | Existing **intake** and **spec-writer** stage agents; vendored skills `triage`, `to-spec`, `grill-me`, `grill-with-docs`, `research` (ad-hoc, not F4) |
| **Owns** | Phase 1 work on a job: 3-part questionnaire, risk tier suggestion, living spec, ADR draft for Tier 2/3 |
| **Inputs** | GitHub issue, `CONTEXT.md`, `AGENTS.md`, learnings file, questionnaire template |
| **Outputs** | `docs/specs/<issue-id>.md` (or the job spec file), optional ADR draft, a recommended Tier 1/2/3, a request for missing answers (`factory:needs-info`) |
| **Tools / access** | Read the worktree and issue text. **No** GitHub token, **no** production secrets, **no** merge. May not start the builder |
| **The operator's approval** | Tier 3 (and, until he says otherwise, Tier 2) plans wait for him. Intake may reject a job; it may not override an always-stop path |

## Planner

| | |
|---|---|
| **Maps to** | Part of the **spec-writer** today; could stay the same agent with a stricter plan artefact. Skills: `wayfinder`, `to-tickets`, `implement-spec` (planning half) |
| **Owns** | Implementation plan: target files, vertical slices, test mapping, rollback note for Tier 3 |
| **Inputs** | Approved or draft spec, ADR, path rules, project's `checks.sh` capabilities |
| **Outputs** | A verified implementation plan the gate can check for completeness |
| **Tools / access** | Read-only on the repo clone. No GitHub token. No code edits in production paths until the plan is approved |
| **The operator's approval** | Required before build on Tier 3; required on Tier 2 under this proposal; Tier 1 may proceed on an automated checklist |

## Builder

| | |
|---|---|
| **Maps to** | Existing **builder** stage agent; skills `implement`, `tdd`, `prototype` (spikes only) |
| **Owns** | Phase 2 execution in the job worktree: implement the plan, run the project's checks, self-correct on lint/type/test failures inside the retry budget |
| **Inputs** | Approved plan, spec, ADR, `setup.sh` environment, focused context (not the whole monorepo dumped at once) |
| **Outputs** | Commits on the job branch, `build.md`, a branch ready for the gate |
| **Tools / access** | Write in the worktree only. **No** GitHub token, **no** production credentials, **no** ability to change `checks.sh` or factory config (those live outside the worktree). Prototype work must stay in a spike branch or behind a flag |
| **The operator's approval** | Does not merge. Stops when an always-stop rule fires, a cap is hit, or the plan is exceeded |

## Test / QA

| | |
|---|---|
| **Maps to** | The **gate** (script running `checks.sh`) today; planned **F5** holdout tester (writes tests from the spec without seeing the diff) |
| **Owns** | Back pressure: project checks, secret scan, complexity / anti-slop examples, later holdout tests, optional coverage policy |
| **Inputs** | Worktree after build, spec acceptance criteria, project's `checks.sh` |
| **Outputs** | Pass/fail, logs the PR can link to, holdout tests the builder never saw (F5, Phase 4) |
| **Tools / access** | Run tests and scanners in the worktree or a copy. **No** GitHub token (the factory already uses this pattern: a test-running helper must not have GitHub access — IBM). Must not rewrite source as a formatter-in-write-mode (gate rule today) |
| **The operator's approval** | Cannot waive a failed gate. Only the operator can merge a PR that still needs a policy exception, and this plan recommends he does not |

## Fresh-context reviewer

| | |
|---|---|
| **Maps to** | Existing read-only **reviewer** agents (code, and UI/UX where routed) |
| **Owns** | Phase 3 audit of the diff against the spec, `AGENTS.md`, architecture, and obvious regressions, in a clean context |
| **Inputs** | Pinned commit, spec, ADR, gate result. Not the builder's session |
| **Outputs** | A review file: approve, changes, or blocked, with evidence |
| **Tools / access** | Read-only. May use the shared review dev server / browser. Cannot push, merge, or edit the branch (engine already treats a dirty tree as a failed review) |
| **The operator's approval** | A clean review does not merge the PR. The operator still does. Fresh-context review is fail-closed on its bound model: no silent downgrade (`docs/roadmap/llm-provider-integration.md`) |

## Security reviewer

| | |
|---|---|
| **Maps to** | Existing **security** surface reviewer (opus in the template for security paths) |
| **Owns** | Auth, secrets, schema, ingress/egress, OWASP-style checks when those packs exist |
| **Inputs** | Diff, project's security rules, later optional rule packs |
| **Outputs** | Security verdict with evidence; follow-up issues for out-of-scope findings (already in the plan) |
| **Tools / access** | Read-only, same as other reviewers. No production credentials |
| **The operator's approval** | Any touch of auth, secrets, or schema is Tier 3 and already needs his plan approval and merge. The bound security model may not be silently replaced by a weaker one; if it is unavailable, the job stops (see `docs/roadmap/llm-provider-integration.md`) |

## Release / Ops

| | |
|---|---|
| **Maps to** | **Not built.** Closest: `job merge` (today waits for required CI, and should still stop for the operator), planned **F6** deploy and rollback, dashboard / E6.4 web console |
| **Owns** | After the operator merges: deploy, health check, rollback (F6); later dashboard telemetry tiles |
| **Inputs** | Merged SHA, project deploy config, health endpoint |
| **Outputs** | Deploy result, rollback, event-log rows |
| **Tools / access** | Deploy credentials live in the private factory home / secrets, **never** in an agent worktree or in the public repo. This role should be a script plus the operator, not an unsupervised model |
| **The operator's approval** | **Always**, for production promote and for enabling any auto-rollback policy. He also merges the code being deployed |

## Research / F4 watcher

| | |
|---|---|
| **Maps to** | Planned **Hermes** market watch (F4) and F8 intake; **not** the vendored `research` skill (that is one-off, primary-source notes) |
| **Owns** | Phase 4 research workstream: official-API / robots-allowed watches, drop folder, weekly digest; no scraping behind blocks |
| **Inputs** | Competitor list, approved source list (GitHub, HN API, Reddit Data API if approved, changelogs/RSS) |
| **Outputs** | Drop-folder files with provenance; the **engine** opens the weekly PR and proposal issues |
| **Tools / access** | Runs **outside** the factory container (E6.1 allowlist is package registries, GitHub, model API only). **No** GitHub token. **No** login-scraping or stealth/evasion |
| **The operator's approval** | Proposals are never auto-queued. He decides what becomes a factory job. Paid APIs wait for his yes. Prefer a local or LAN model for summarising untrusted sources; do not send drop-folder text to OpenRouter while `data_leaving_lan` is deny |

## Curator (knowledge loop)

| | |
|---|---|
| **Maps to** | **Not built.** Closest: planned **F3** learnings file and the operator's existing habit of merging docs PRs. Inspired by [Harrison Chase, entry 05](../reference-library/05-harrison-chase-knowledge-factory.md) |
| **Owns** | The knowledge loop tied to F3: collect flags from other roles (gaps in skills, `AGENTS.md`, ADRs, or domain notes), open PRs that update those artefacts, and keep skill files from rotting or bloating. Does not implement product features |
| **Inputs** | Gap flags from any role, the learnings file, current `AGENTS.md` / skill docs, review notes that mention missing context |
| **Outputs** | PRs that update skills, `AGENTS.md`, or domain knowledge. Never a merge |
| **Tools / access** | Least privilege: write only in documentation / skill paths in a job worktree. **No** GitHub token (the orchestrator opens the PR). **No** production credentials, **no** ability to change factory config or `checks.sh` |
| **The operator's approval** | Required to merge every curator PR. The Curator must not approve its own work (never-self-merge). Other agents may flag gaps; only this role (or the operator) turns a flag into a knowledge PR |

## PM / product steer

| | |
|---|---|
| **Maps to** | **The operator**, with optional later use of the official PM bot (see the earlier PM-agent note). Not a factory stage today. F1 Dev council, when built, is a later **shadow** debate, not a product manager and not a merger |
| **Owns** | What is in or out of a cut, which Phase 4 features start, whether a proposal issue is labelled for the factory |
| **Inputs** | Digests, learnings, dashboard, open issues |
| **Outputs** | An approved cut or a labelled issue. Stops until the operator agrees |
| **Tools / access** | No merge token, no production deploy, no unattended engineering |
| **The operator's approval** | Required for every cut. An agent's "looks good" does not count |

## Who owns which phase

| Phase | Lead role | Supporting roles |
|---|---|---|
| 0 Safety | Orchestrator (code change + test) | The operator reviews and merges |
| 1 Steering and discovery | Discovery / Spec, Planner | PM steer (the operator), Orchestrator enforces the plan gate |
| 2 Inner-loop and E1.6 | Builder, Test / QA | Orchestrator (retries, container), the operator on the first real PR |
| 3 Review and governance | Fresh-context reviewer, Security | Test / QA, Orchestrator, the operator merges |
| 4 Operator-scale | PM steer (the operator chooses the slice), Research / F4 watcher, Release / Ops (F6), Test / QA (F5), Orchestrator (telemetry, F2) | Dev council only in shadow; never as merger |

No role in this roster is allowed to force-push, use admin override, push directly to `main`, or merge without the operator.


## Model / provider bindings

Proposal only; see `docs/roadmap/llm-provider-integration.md`. Default for every model-using stage remains the Claude Code CLI harness and the short names already in `config.json` (`fable`, `sonnet`, `opus`, `haiku`) until the operator changes a binding. Local, LAN, and OpenRouter are first-class connections on the completion path (council, later optional roles). `data_leaving_lan` defaults to deny. Reviewer and security roles fail closed rather than falling over to a weaker model. Provider choice does not change the L2 autonomy cap or the four security boundaries.

| Role | Model? | Default (today) | Notes |
|---|---|---|---|
| Orchestrator | No | — | Script; owns the router and budgets |
| Discovery / Spec | Yes | Claude Code `fable` | Eligible later for local/LAN |
| Planner | Yes | Same spec-writer path | Eligible later for local/LAN |
| Builder | Yes | Claude Code `opus` | Changing this relaxes a v6.4 non-goal and needs the operator's yes |
| Test / QA | No today | Scripted `checks.sh` | F5 may need a model; prefer local/LAN; fail closed if it is missing |
| Fresh-context reviewer | Yes | `routing` / surfaces | Fail closed; no silent downgrade |
| Security reviewer | Yes | Claude Code `opus` | Fail closed; no silent downgrade |
| Release / Ops | No | Script + the operator | |
| Research / F4 watcher | Optional | Not built | Prefer local/LAN for untrusted text |
| PM / product steer | No | The operator | |

Paid OpenRouter spend, and any new E6 allowlist host, wait for the operator.
