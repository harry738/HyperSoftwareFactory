# Gemini 12-week plan × HyperSoftwareFactory v6.4 — integration analysis

Local proposal only. Nothing was pushed or committed to GitHub. The two planning documents were copied out as Markdown; the source originals were left in place and were not modified or deleted.

**Date:** 25 November 2026 (Europe/London)  
**Repo tip used:** [harry738/HyperSoftwareFactory](https://github.com/harry738/HyperSoftwareFactory) `main` at [`72a982c`](https://github.com/harry738/HyperSoftwareFactory/commit/72a982c7c9103b5f53a85f22db0c5de6000c6c8f) (merge of #46, 25 November 2026, 07:37 GMT). Live plan: [reference/build-plan.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md) **v6.4**.  
**Local working copy:** this working tree is **not** a git checkout. Repo files were read with the GitHub API. No clone was made, so there is no local HEAD.

## Sources

| Source | Path or URL |
|---|---|
| Gemini, shorter plan | exported from the operator's planning docs · local [docs/roadmap/gemini/ai-software-factory-product-and-engineering-roadmap.md](../roadmap/gemini/ai-software-factory-product-and-engineering-roadmap.md) |
| Gemini, detailed plan + questionnaire | exported from the operator's planning docs · local [docs/roadmap/gemini/ai-software-factory-discovery-questionnaire-and-product-roadmap.md](../roadmap/gemini/ai-software-factory-discovery-questionnaire-and-product-roadmap.md) |
| Factory build plan v6.4, feature comparison, CONTEXT/AGENTS, issue #26, open PR #42 | GitHub `main` @ `72a982c` |
| Video learnings | [01-dex-horthy.md](01-dex-horthy.md), [02-vibe-coding-vs-agentic-coding.md](02-vibe-coding-vs-agentic-coding.md) |

Companion local files (also proposals, not pushed): [deployable-roadmap.md](../roadmap/deployable-roadmap.md), [agent-roster.md](../roadmap/agent-roster.md), [feature-list-by-phase.md](../roadmap/feature-list-by-phase.md), and later the same evening [llm-provider-integration.md](../roadmap/llm-provider-integration.md), [04-market-scan-software-factories-2026-11-25.md](04-market-scan-software-factories-2026-11-25.md), and [roadmap-consistency-review-2026-11-25.md](roadmap-consistency-review-2026-11-25.md). This analysis predates those later files and is not the live feature list.

`principles.md` is still deferred until the operator says the video set is complete.

## How the 12-week plan maps onto v6.4

The Gemini docs describe a **greenfield** four-phase, 12-week build of a spec-driven factory. HyperSoftwareFactory already has most of that **engine** on main: labelled issues go through intake → spec → build → gate → read-only reviewers → approver → a PR, with budgets, retries, an event log, worktrees, and a container/network allowlist (E6 built, not yet run signed-in). The factory's own three-week engine timebox is largely complete in code and stand-in tests. **E1.6** (first real-project job) is still open. Treating Gemini week 1 as "start the factory from scratch" would ignore what is already shipped.

The two Gemini docs also **disagree with each other** on where multi-tenant onboarding sits: the shorter plan puts "Multi-Tenant Platform & User Workspace" in Phase 3 (weeks 7–9); the longer plan puts it in Phase 4 (weeks 10–12). This analysis follows the longer, more detailed document for phasing, and flags the clash.

| Gemini item | Closest v6.4 / repo counterpart | Fit |
|---|---|---|
| Root / nested `AGENTS.md`, Always / Ask First / Never, Context Pyramid, Task Router | `AGENTS.md` and `CONTEXT.md` exist and are protected paths. There is no Always / Ask First / Never checklist, and no mandated `docs/specs/` or `docs/adr/` tree | Partial. High-value docs gap |
| 3-part discovery questionnaire (scope, risk, acceptance) on new issues | Intake and a spec stage already exist; `to-spec` / `grill-me` skills are vendored. No fixed 3-section issue template | Partial. Adopt as an intake enhancement |
| Risk tiers 1 / 2 / 3 with ADR + rollback + human approval on Tier 3 | Plan already claims a lead on "risk tiers and path-based routing" (`low` / `medium` / `high`, `risk_paths`, `protected_paths`, `sensitive_paths`, `human-merge`, always-stop rules). Not the same published 3-tier matrix or formal ADR protocol | Partial. Align the names; do not build a second router |
| Implementation plan gate before any code | Spec stage exists; not a hard "no `src/**` until the plan is approved" gate for every risk tier | Partial |
| Isolated sandbox, frozen package manager, secret scanning | E6 container + allowlist, per-project `setup.sh` / `checks.sh` outside the builder worktree, worktrees. Factory CI is Python + `scripts/test.sh`, not `pnpm` / `tsc` / `Vitest` | Partial. Keep checks **per project**, not a TypeScript-only harness |
| Self-correcting retry until green; no `--no-verify` / `@ts-ignore` / `any` | E2 retries and caps are done. Template `factory/checks.sh` still exits 1 with no checks. Language-specific bypass bans belong in project checks | Partial |
| Every acceptance criterion maps to a test; ≥90% branch coverage on new domain logic | F5 (holdout checks) is planned. Factory CI has **no** coverage threshold. 90% as a global factory rule would not fit a Python engine or every target project | Conflict if applied globally; useful as an optional project policy |
| Fresh-context reviewer vs spec, security, architecture | E4 read-only reviewers are done and stand-in tested (code, UI/UX, security). They already run without write access | Overlap — largely done |
| Auto-assembled PR with spec, ADR, coverage report, rollback plan | PRs and evidence on the PR exist; living `docs/specs` / ADR links and a rollback-plan artefact are missing | Partial |
| CI blocks non-compliant merges; Tier 3 human checkpoints | Intended: `unattended_merge: false` in the template; always-stop paths; `job merge` waits for required CI. **[#26](https://github.com/harry738/HyperSoftwareFactory/issues/26)** still defaults a missing key to **on**. FullAuto is documented and unbuilt | Conflict until #26 is fixed; keep the operator as the only merger |
| Multi-tenant self-service for **external** teams' repos; "execute … autonomously" | Operating model: "Own projects only. Generality is added when a second project forces it" (F7). "A web app for onboarding is a later feature." Dashboard and `factory onboard` already serve the **operator** | Conflict if treated as near-term. Defer |
| Context7 and OWASP / framework rule packs | A Context7 note already lives at `reference/context7-docs-mcp.md` (planned, not wired). Crawl4AI is named in the README planned integrations, also unwired. OWASP packs are new | Partial / new |
| Telemetry: first-pass green rate, retry counts, spec-drift, tier mix | Event log + `usage.jsonl` (E2.3) and a dashboard exist. Those exact metrics are not specified. Prometheus is a **non-goal** in v6.4 | Partial. Extend the existing dashboard from the event log; do not add a new metrics stack |
| F1 Dev council, F2 Hermes schedule, F3 learnings, F4/F8 research, F5 holdout, F6 deploy/rollback, F7 second project | Gemini barely covers these. They stay on the factory feature track, after the engine's open items | Keep, do not replace |

Video learnings that should shape the integration (not a full `principles.md`):

- **Horthy:** pair forward pressure (structured intake) with back pressure (checks before a human looks); plan more where change is expensive; fight slop with lint/complexity rules; keep prototypes out of production; compound lessons; keep decisions next to the code; humans still sign off. The official transcript does not publish a numbered list of 12.
- **Ableidinger (IBM):** match vibe vs agentic work to risk; understand → plan → execute → test → validate; focused context; scoped subagents (a test runner should not hold a GitHub token — the factory already removes tokens from agent stages); testing, governance, observability, rollback and guardrails; stay the person who can explain the code.

## Overlaps (already on the repo path)

- Scripted control flow, not a model choosing the next stage.
- Spec-then-build, read-only reviewers, an approver, a PR waiting for a person (supervised default).
- Risk- and path-based routing, specialist security review, budgets and retries, an event log, container isolation and a network allowlist.
- Agents without GitHub tokens; Hermes (when built) also holds no GitHub token for F4.
- A dashboard and onboarding CLI for the operator.
- A reference note for Context7; planned (unwired) Crawl4AI for intake research.

## Conflicts and cautions

1. **Fail-open merge vs Tier 3 human gate.** Gemini requires mandatory human approval for high-stakes work. The template sets `unattended_merge` false, but `factory/bin/run` still uses `CONFIG.get("unattended_merge", True)` ([#26](https://github.com/harry738/HyperSoftwareFactory/issues/26)). Fix this before any other Gemini-inspired work.
2. **Autonomy language vs the operator's rule and v6.4.** The longer Gemini exit criterion, "external users can … execute an end-to-end spec-to-PR workflow autonomously," and the shorter vision of an "autonomous" factory, sit badly with "the operator merges," with supervised-by-default, and with FullAuto being opt-in and unbuilt. The deployable plan keeps every merge with the operator.
3. **Multi-tenant / external self-service vs "own projects only."** v6.4 adds generality when a **second of the operator's projects** (F7) forces it, not when outside teams self-serve. Do not put external multi-tenant in the next 12 weeks.
4. **The two Gemini docs disagree** on whether multi-tenant is Phase 3 or Phase 4.
5. **Stack assumptions.** Gemini Phase 2 names `pnpm --frozen-lockfile`, `tsc`, ESLint and Vitest, and bans `@ts-ignore` / `any`. The factory engine is Python 3 (only `PyYAML` in `requirements.txt`) with CI in `.github/workflows/tests.yml` running `bash scripts/test.sh` on Ubuntu and Windows. Target projects may be TypeScript (the Binley example is Next.js-shaped). Quality gates must stay in each project's `checks.sh`, not be hardcoded as a Node toolchain in the engine.
6. **90% branch coverage** is not in factory CI and should not become a global merge blocker for the engine or for every project. Propose it as an optional project policy for new domain logic, alongside F5 holdout tests.
7. **12-week greenfield calendar vs an engine that is already mostly built.** Do not restart the clock at week 1. Use Gemini's *themes* as the next slices on top of v6.4, and finish E1.6 plus #26 first.
8. **v6.5 on open PR [#42](https://github.com/harry738/HyperSoftwareFactory/pull/42)** proposes evidence-gated releases R1–R6, but was opened against an earlier SHA and may be stale versus #43–#46. It is docs only. Rebase or close it; do not treat it as the live plan.

## New items worth adding (proposals only — no official IDs allocated)

1. Fail-closed `unattended_merge` (already issue #26).
2. An `AGENTS.md` / contributing checklist: where specs and ADRs live; Always / Ask First / Never; which checks must pass before a PR; which paths need the operator's sign-off; focused-context and prototype-vs-production rules (Horthy + IBM).
3. `docs/specs/` and `docs/adr/` templates (or the equivalent project convention), so design intent lives in the repo.
4. The 3-part discovery questionnaire as the intake/spec template, writing a risk tier that maps onto existing path/label rules.
5. A hard plan-approval gate before build for Tier 2 and Tier 3 (Tier 1 may use a shorter checklist).
6. Template `checks.sh` examples: lint, types, tests, secret scan, complexity / anti-slop (CONTEXT rule 3 and the carried-over backlog). Language-specific, not Vitest-only.
7. Spec-to-test traceability (pairs with planned F5). Optional per-project coverage policy — not a factory-wide 90% rule.
8. Richer PR assembly: links to the spec, ADR, check output, and a rollback note.
9. Dashboard metrics from the existing event log: first-pass green rate, retry counts, later spec-drift and tier mix. No new Prometheus stack.
10. Optional Context7 / live-docs hook and OWASP or language security packs, after E1.6, still inside the E6 allowlist rules.
11. Feature-flag or sandbox rule for vibe/prototype work (Horthy + IBM). Missing today.
12. F4 drop-folder contract (docs first; official APIs; Hermes outside the container). Do not start this before #26 and E1.6.

## Recommended updated roadmap (proposal)

Keep **v6.4 as the spine**. Do not replace E/F/A IDs. Overlay five deployable phases (detail in `docs/roadmap/deployable-roadmap.md`):

0. **Safety (now).** Land #26. Unattended merge stays off. The operator is the only merger.
1. **Steering and discovery.** Checklist, spec/ADR templates, questionnaire, aligned 3-tier protocol, plan gate, prototype policy.
2. **Inner-loop quality.** Project-appropriate `checks.sh` examples, anti-slop/secret scan, signed-in container (E6), **E1.6** first real job, finish remaining engine opens as they block (E3.5, E5.1, E5.3, E6.3–E6.4).
3. **Review and merge governance.** Tighten fresh-context review and PR artefacts; CI/gate already block bad work; Tier 3 always stops for the operator.
4. **Operator-scale features, not a multi-tenant product.** F3 learnings, dashboard metrics, optional Context7; then F5, F6 if the first project can roll back, F2/F4/F8, F1 council in shadow, F7 second project. External self-service stays deferred.

Suggested first PRs, unchanged in spirit: **#26**, then the AGENTS.md checklist and spec/ADR templates, then template checks / anti-slop, then a docs-only F4 contract. Open PR #42 only if the operator still wants a rebased v6.5 framing.

## Recommended feature list (compact)

**Keep (existing or already planned):** engine loop E1–E6; risk/path routing; read-only reviewers; event log and dashboard; `factory onboard`; F1–F8 and FullAuto as documented; Context7 as a reference note; Crawl4AI as a planned, unwired research tool.

**Add (new proposals):** fail-closed default; Always / Ask First / Never checklist; `docs/specs` + `docs/adr`; discovery questionnaire; named Tier 1–3 protocol; plan-before-build gate; anti-slop / complexity examples in `checks.sh`; optional coverage policy; PR artefact pack; event-log telemetry tiles; prototype / feature-flag rule; F4 drop-folder schema.

**Defer:** external multi-tenant onboarding, domain packs for outside teams, autonomous merge, a TypeScript-only factory toolchain, a global 90% coverage gate, Prometheus.

The operator remains the only person who can approve a plan for Tier 3 work, merge a PR, enable FullAuto, or add any of this to the public repo.
