# Deployable roadmap (proposal)

Proposal only. Not an official revision of `reference/build-plan.md`. No new official E/F numbers are allocated. The operator remains the only merger. FullAuto is out of scope for this plan. Auto-merge and auto-deploy are not adopted.

Built from the Gemini 12-week docs (local copies under `docs/roadmap/gemini/`), build plan **v6.4**, issue #26, the original reference-library set (entries 01–04), the LLM provider spec (`docs/roadmap/llm-provider-integration.md`), and the 25 November 2026 ingestion batch (entries 05–15). This revision folds five high-impact additions from that batch onto `main` @ `351b660` (the squash of pull request #47).

The factory engine is already mostly built and stand-in tested. These phases start from that fact. They are **slices with entry/exit criteria**, not a promise that each slice lasts three calendar weeks.

## Standing gates (every phase)

- A missing `unattended_merge` key must fail **closed** (issue #26). Until that lands, treat unattended merge as unsafe.
- **Never-self-merge (hard rule).** The factory never merges its own work ([Gumloop, entry 13](../reference-library/13-gumloop-software-factory.md)). The author of a change does not approve it ([Itamar Friedman, entry 11](../reference-library/11-itamar-friedman-software-factory-engineer.md)). The operator merges every PR. Agents open PRs only. The existing approver may recommend; it cannot merge.
- Always-stop paths and `human-merge` outrank any agent verdict.
- **Autonomy cap: L2 (workflow-orchestrated)** ([Agent Baseline, entry 14](../reference-library/14-agent-baseline-secure-software-factory.md)). A recorded script (`factory run`) chooses the next step and the tools; agents work inside that path. **L3 and L4 are out of scope.** Agents never grant themselves access (identity/access boundary).
- Four security boundaries must stay explicit (entry 14): **sandbox** (what the process can touch), **network** (where data may go; `data_leaving_lan` defaults to deny), **supply chain** (what may be installed or pulled), and **identity/access** (who the agent is, and that it does not hold the GitHub token).
- No push to the public repo, and no Drive change, without the operator's yes.
- Rollback for factory work is: do not merge, or revert the PR on `main`. Project deploy rollback is F6 and is not assumed until the first real project has a reversible deploy (open question 2 in v6.4).

## Phase 0 — Safety

**Goal.** Close the fail-open merge hole so later autonomy talk cannot accidentally merge.

**Entry.** Current `main` (`72a982c` or later) with #26 still open.

**Work.** Change `CONFIG.get("unattended_merge", True)` to default `False` in `factory/bin/run` and `factory/bin/job`, with a test that a missing key never merges. Optionally clear the small open engine bugs (#27–#32) if they are still valid.

**Depends on.** Nothing.

**Exit.** A missing config key cannot merge; template and code agree that unattended merge is off; tests cover it; the operator has merged the PR.

**Human gate.** The operator reviews and merges this PR. No other factory change should land first.

**Rollback.** Revert that PR (the previous default was fail-open, so reverting is worse — only revert if the fix itself is wrong, and keep unattended merge off by config).

## Phase 1 — Steering and discovery

**Goal.** Forward pressure that is structured, and design intent that lives in the repo (Gemini Phase 1; Horthy "unify the forge" and "plan by expected pain"; IBM "match the workflow to the risk").

**Entry.** Phase 0 exit.

**Work.**

- An `AGENTS.md` (and, if useful, CONTRIBUTING) checklist: Always / Ask First / Never; where specs and ADRs live; which checks must pass before a PR is ready; which paths need the operator's sign-off; focused context; prototypes stay out of production modules.
- Templates for living specs (`docs/specs/<issue-id>.md` or the project's existing job-spec convention) and ADRs (`docs/adr/`).
- The Gemini 3-part discovery questionnaire (scope, risk/blast radius, acceptance) as the intake/spec template.
- Publish a Tier 1 / 2 / 3 protocol that **maps onto** existing `low` / `medium` / `high`, path rules and `human-merge`, rather than a second router. Tier 3 (schema, auth/security, breaking APIs) always needs an ADR, a rollback note, and the operator's plan approval before build.
- A plan-approval gate: Tier 2 and Tier 3 do not start the builder until the implementation plan is approved (Tier 1 may use a short automated checklist). The gate has two steps, after [Ben Holmes / Warp, entry 06](../reference-library/06-ben-holmes-software-factory-as-code.md): a **spec gate** (the living spec and, for Tier 2/3, the ADR are complete enough to build against) and a **triage gate** (tier, blast radius, and whether the plan is approved). Nothing in production paths is edited until both pass.
- A written prototype / feature-flag rule for vibe-coded spikes (IBM + Horthy).
- Provider-integration *schema* only (see `docs/roadmap/llm-provider-integration.md`): `providers`, `role_bindings`, and `data_leaving_lan` defaulting to **deny**. Bindings still point at the Claude Code harness and today's short model names, so behaviour does not change. A missing residency key fails closed, in the same spirit as #26.

**Depends on.** Phase 0. Can be docs-and-template PRs; no need to wait for E1.6.

**Exit.** A labelled test issue produces a structured spec (and, for Tier 2/3, a verified plan) before any production path is edited. Templates exist in-repo. The operator has signed off the Tier 3 rule. The provider config schema parses; a missing `data_leaving_lan` key is treated as deny; no live new vendor is enabled.

**Human gate.** The operator approves the checklist and the Tier 3 protocol, approves Tier 3 plans, and merges the docs PRs.

**Rollback.** Revert the docs PRs; the engine loop still works as today.

## Phase 2 — Inner-loop quality and first real job

**Goal.** Back pressure before a human looks (Gemini Phase 2; Horthy anti-slop and "help agents test"; IBM test-and-validate). Prove it on one real project (E1.6).

**Entry.** Phase 1 templates exist; Phase 0 is done; a real project, token, and signed-in factory machine are ready (E1.6 prerequisites in v6.4).

**Work.**

- Fill the template `factory/checks.sh` with **examples** (lint, types, tests, secret scan, complexity / anti-slop, dependency audit). The toolchain is the **project's**, not a factory-wide `pnpm` / `tsc` / `Vitest` stack. The factory engine stays Python.
- Keep the existing retry loop; add project rules that forbid skipping the gate (the Gemini `--no-verify` / `@ts-ignore` / `any` ban, translated to that stack).
- Map each acceptance criterion to a test (pairs with later F5). An optional project policy may set a coverage floor for new domain logic; **do not** make 90% a global factory CI blocker.
- Run the factory container signed-in (E6). Finish engine items that block a real job (E3.5 flaky checks, E6.3–E6.4, E5.1 / E5.3 if they start to matter).
- **E1.6:** first labelled issue on a real project through to a PR that waits for the operator.
- Implement the LLM provider layer in `docs/roadmap/llm-provider-integration.md`: the factory Protocol, FakeProvider tests, and local / LAN adapters (Ollama native or OpenAI-compatible). Add the E6 private-endpoint path (`NO_PROXY` / a distinct allowlist; HTTP only to private addresses) if the operator wants a local or LAN model on the signed-in container. The builder stays on Claude Code unless he relaxes the v6.4 non-goal. An OpenRouter adapter may be coded against the fake; a real key, `openrouter.ai` on the public allowlist, and any paid spend wait for his yes.

**Depends on.** Phases 0–1, and the first project's `checks.sh` / `setup.sh` in the private factory home.

**Exit.** The first real job has produced a PR that passed the project's checks without skipped gates, and is waiting for the operator. The container has been run signed-in at least once. Template examples exist for the next project. Provider stand-in tests are green; an optional local or LAN path may be demonstrated on a non-production job if the operator wants it. USD budgets still stop the job.

**Human gate.** The operator labels the first real issues, reviews the PR, and merges or rejects it. He remains able to explain the change (IBM).

**Rollback.** Leave the PR unmerged; fix in a new round. Do not enable unattended merge to "get through" a red gate.

## Phase 3 — Fresh-context review and merge governance

**Goal.** A human only reviews work that has already been checked against the spec, security baseline and architecture (Gemini Phase 3; most of E4 is already built).

**Entry.** Phase 2 exit, or at least E1.6 in progress with reviewers running on real diffs.

**Work.**

- Keep the existing clean-context, read-only reviewers. Tighten what the PR must attach: spec, ADR (when Tier 2/3), check output, coverage or test map if the project uses one, rollback note, and **evidence that a failing test was written (or observed) and then passed** ([Gumloop, entry 13](../reference-library/13-gumloop-software-factory.md)).
- The review pack uses five merge-risk headings, after [Ben Holmes / Warp, entry 06](../reference-library/06-ben-holmes-software-factory-as-code.md): **Alignment** (does the diff match the approved spec?), **Impact** (what can break?), **Verification** (what was actually run, including the failing-then-passing evidence), **Rollback cost** (how hard is a revert?), and **Error detection** (how will we know if this is wrong in production?).
- Make sure required CI and the gate block merge of non-compliant work. Tier 3 always stops for the operator, even if a later policy ever turns unattended merge on for Tier 1.
- No autonomous merge. Never-self-merge is a standing hard rule. The approver may recommend; it cannot merge. The builder (or any other authoring role) cannot approve its own work.
- Enforce fail-closed provider bindings for the fresh-context and security reviewers: no silent downgrade to a weaker model; if the bound model is unavailable, the job stops for the operator. Event / PR evidence records which provider and model actually ran (`docs/roadmap/llm-provider-integration.md`).

**Depends on.** Phases 0–2 (artefacts from Phase 1, checks from Phase 2).

**Exit.** A non-compliant PR cannot be merged by the factory. Every Tier 3 job shows the ADR, rollback note, and a stop for the operator. Reviewers still cannot write the branch. A security or fresh-context review cannot complete on a weaker substitute; a missing reviewer model stops for the operator.

**Human gate.** The operator merges or rejects. For Tier 3 he has also approved the plan in Phase 1's protocol.

**Rollback.** Unmerged PRs; or revert after merge.

## Phase 4 — Operator-scale features (not a multi-tenant product)

**Goal.** Sharpen the factory for the operator's own projects: lessons, telemetry, research, holdout tests, deploy/rollback, a council in shadow, a second project. This is Gemini Phase 4 **without** external self-service.

**Entry.** Phase 3 exit, or a stable E1.6 flow with the operator still merging.

**Work, in a sensible order (not all at once).**

- F3 weekly inside-view Kaizen and a curated learnings file (Horthy: compound lessons), plus Harrison Chase's **knowledge loop** ([entry 05](../reference-library/05-harrison-chase-knowledge-factory.md)): any role may **flag** a gap in skills, `AGENTS.md`, or domain knowledge; a separate **Curator** role (see the agent roster) opens PRs that update those artefacts and never merges them.
- Dashboard tiles from the existing event log: **cost per accepted change as the headline metric** ([Itamar Friedman, entry 11](../reference-library/11-itamar-friedman-software-factory-engineer.md)), plus first-pass green rate, retry counts; later spec-drift and tier mix. No Prometheus stack (v6.4 non-goal).
- Optional Context7 / live-docs hook and security rule packs, inside the E6 allowlist, after E1.6.
- Docs-only F4 drop-folder contract, then F4/F8 research on official APIs, outside the factory container, proposals never auto-queued.
- F5 holdout checks; F6 deploy and rollback if the first project can actually roll back; F2 Hermes schedule and notifications; F1 Dev council **in shadow only**; F7 a second **operator** project.
- **Propose-but-don't-execute** for incident and performance agents ([OpenAI via The Pragmatic Engineer, entry 07](../reference-library/07-pragmatic-engineer-openai-software-factory.md); F6-related): they may open a PR or a proposal issue; they never deploy, roll back, restart, or change production themselves. The operator approves and the Release / Ops script runs only after that yes. Auto-deploy is not adopted.
- Optional **Prismor observe-mode trial** only ([entry 15](../reference-library/15-prismor.md)): if the operator says yes, run it around the Claude Code harness in observe mode on a disposable machine, compare observations to the existing allowlist and checks, and do **not** enable enforce mode. Nothing is installed in this pass.
- Provider follow-through from `docs/roadmap/llm-provider-integration.md`: dashboard tiles by provider and connection; F1 council calls models through the completion path (the "one API gateway" already in v6.4); F4 summariser prefers local or LAN. OpenRouter in production, and any other paid model API, only after the operator approves the spend and the E6 host entry. `data_leaving_lan` stays **deny** unless he changes it.

**Explicitly deferred:** self-service onboarding for external teams, reusable domain packs sold or offered to outsiders, and any "run autonomously to merge" exit criterion from the Gemini docs.

**Depends on.** A working supervised loop (Phases 0–3). F6 depends on a reversible deploy existing. F4 depends on the drop-folder schema and official API access. F1 merge power is **not** in this phase.

**Exit.** The operator can see loop quality on the dashboard, a weekly learnings PR exists or is defined, and at least one of F3, telemetry, or the F4 contract has landed. External multi-tenant has not been started.

**Human gate.** The operator chooses which of F2–F8 to start, approves any paid API, merges every PR, and is the only person who can later consider FullAuto or council merge power (those stay outside this plan).

**Rollback.** Revert individual feature PRs. Research watchers are outside the merge path, so they can be stopped without rolling back the engine.

## Dependency sketch

```
Phase 0 (#26; never-self-merge and L2 cap already standing)
    └─ Phase 1 (checklist, specs/ADRs, questionnaire, Tier 1–3,
         Holmes spec + triage plan gate, provider schema, data_leaving_lan=deny)
         └─ Phase 2 (project checks, anti-slop, signed-in E6, E1.6,
              provider layer, local/LAN adapters, failing-then-passing test evidence)
              └─ Phase 3 (PR artefacts + five merge-risk headings, Tier 3 always stops,
                   fail-closed reviewer/security model bindings, never-self-merge)
                   └─ Phase 4 (F3 + Curator knowledge loop, cost-per-accepted-change tiles,
                        optional Context7, F4 contract, then F5/F6/F2/F8/F1-shadow/F7;
                        propose-but-don't-execute on incident/performance agents;
                        optional Prismor observe trial; OpenRouter only after the operator's yes)
```

Open PR #42 (v6.5 docs) may be rebased onto current main if the operator still wants that release framing; it is not a substitute for Phase 0.
