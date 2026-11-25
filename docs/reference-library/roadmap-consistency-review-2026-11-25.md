# Roadmap consistency review (25 November 2026, Europe/London)

Local only. Not pushed. This is a review of the proposal set under `this working tree` after the LLM provider spec and its `docs/roadmap/deployable-roadmap.md` entry were written. It is not an official revision of `reference/build-plan.md`. The operator remains the only merger.

**Read:** `docs/roadmap/deployable-roadmap.md`, `docs/roadmap/feature-list-by-phase.md`, `docs/roadmap/agent-roster.md`, `docs/roadmap/llm-provider-integration.md`, `docs/reference-library/gemini-roadmap-integration-2026-11-25.md`. Glanced at `docs/reference-library/04-market-scan-software-factories-2026-11-25.md` (scored opportunities).

Policy defaults were checked against one another: `unattended_merge` fail-closed / stays off; `data_leaving_lan` defaults to deny; no factory-wide `pnpm`/`tsc`/`Vitest` stack; no global 90% coverage blocker; FullAuto, external multi-tenant, and selling domain packs to outsiders stay out of this plan.

## Fixes made (trivial and unambiguous only)

1. `docs/roadmap/llm-provider-integration.md`: two backtick paths `03-layered-llm-guardrails.md` now read `docs/reference-library/03-layered-llm-guardrails.md`, which is where that file actually sits.
2. `docs/roadmap/deployable-roadmap.md`: the "Built from" sentence now also cites the market scan and `docs/roadmap/llm-provider-integration.md`.
3. `docs/reference-library/gemini-roadmap-integration-2026-11-25.md`: the companion-files line now points at the later same-evening files (provider spec, market scan, this review) and states that the analysis predates them and is not the live feature list.

Nothing else was edited in this pass.

## What is solid

The five phases, standing gates, and "the operator merges / agents open PRs only" rule are consistent across the roadmap, feature list, roster, and the earlier Gemini integration analysis. v6.4 remains the spine; no new official E/F numbers are invented.

The engine facts in the provider spec match `main` @ `72a982c`: scripted `factory run`, Claude Code as the stage harness, short model names (`fable` / `sonnet` / `opus` / `haiku`), budgets and `usage.jsonl` / `events.jsonl`, reviewers read-only, agents without the GitHub token, E6 HTTPS allowlist and `NO_PROXY` limited to localhost.

Provider integration now appears in all four live plan files, with the same split: Phase 1 schema and `data_leaving_lan=deny`; Phase 2 Protocol, FakeProvider tests, and local/LAN adapters (OpenRouter coded against the fake only); Phase 3 fail-closed reviewer and security bindings; Phase 4 dashboard-by-provider, council via the completion path, OpenRouter in production only after the operator's yes. That matches the role-binding table in the roster and the adopt-vs-build recommendation (LiteLLM or any-llm as transport; keep the Claude Code harness; do not stand up a required proxy).

Coverage and toolchain stance is consistent: rejected as a global factory default, allowed only as a project's `checks.sh` or optional policy. Market-scan "do not incorporate" items (auto-merge as default, TypeScript-only factory stack, global 90% gate, near-term multi-tenant) are already deferred or rejected in the feature list.

## Conflicts and gaps (flagged, not edited)

### 1. Delivery order vs phased plan (highest practical confusion)

`docs/roadmap/feature-list-by-phase.md` item 7 puts "LLM provider integration" after the Phase 4 F4 contract (item 6), which reads as if the whole capability waits until the end. The item text itself says "schema first, then local/LAN, then fail-closed bindings," which matches the roadmap (schema in Phase 1, adapters in Phase 2, bindings in Phase 3, OpenRouter in Phase 4). The numbered list and the phases disagree. Suggest splitting item 7 across the existing Phase 1–4 steps, or moving the schema bullet under item 2.

### 2. Market-scan rows landed in the feature list but not in the roadmap

These are on the feature list, and in the scan's scored opportunities, but have no work or exit line in `docs/roadmap/deployable-roadmap.md` and no named owner in the roster's "who owns which phase" table:

- Optional GitHub Spec Kit (or Specify → Plan → Tasks shapes) as a Phase 1 process layer (scan opportunity 2).
- PR screenshots / browser notes on UI changes (scan opportunity 5; roadmap Phase 3 lists spec, ADR, check output, rollback note, but not screenshots).
- Layered cheapest-first guardrails on untrusted input (scan opportunity 4; delivery-order item 6 mentions them, the Phase 4 work bullets do not).
- Crawl4AI (planned in v6.4 and the feature list; not in the Phase 4 work list).

### 3. Who implements the provider layer?

The roster describes *runtime* roles. Phase 2 leads are Builder and Test/QA, who are job-stage agents, not the authors of factory-engine PRs. The provider layer, E6 private-endpoint path, and schema work belong to the scripted orchestrator (as Phase 0 already treats "Orchestrator" for the #26 code change), but the Phase 1–2 ownership table does not say so. Release/Ops and Orchestrator also both touch dashboard tiles in Phase 4.

### 4. The existing approver stage has no roster role

The engine still has an `approver` agent. The roadmap says it may recommend and cannot merge. The roster has no Approver row; merge power sits with the operator, and the orchestrator runs `job merge`. Worth a one-line mapping so the stage is not mistaken for a missing owner.

### 5. Exit criteria that are compound or soft

- Phase 2 exit mixes a hard requirement (E1.6 PR waiting; stand-in provider tests green) with an optional "local or LAN path may be demonstrated if the operator wants it." A phase can pass without that demo; say so explicitly.
- Phase 2 work mentions "E5.1 / E5.3 if they start to matter," but the feature list places scheduled `factory run` (E5.3 / F2) in Phase 4. Concurrency (E5.1) is Phase 2 and planned, which is fine if E5.3 is dropped from the Phase 2 bullet.
- Phase 4 exit ("at least one of F3, telemetry, or the F4 contract") is measurable but weak, and does not mention provider follow-through, which is intentional if Phase 4 stays pick-and-choose.
- Phase 3 "a non-compliant PR cannot be merged by the factory" is the right bar but needs a stated test or required-CI check, not only a policy sentence.

### 6. Stale integration analysis, and a softer deferral

`gemini-roadmap-integration-2026-11-25.md` recommended roadmap and compact feature list predate the provider spec and the market-scan rows. The new cross-reference states that; the body was not rewritten. Feature list says reusable domain packs are "deferred until after F7, and only for the operator's projects at first"; the roadmap lists packs sold or offered to outsiders as explicitly deferred. Close enough, but the F7 wording is softer.

### 7. Feature-list legend and library index

The legend still says new proposals come from "Gemini, the videos, or the integration analysis," and does not mention the market scan or the operator's 25 November provider request. `docs/reference-library/index.md` lists entries 1–4 only; it does not list the Gemini integration note, the ingestion log, or this review.

### 8. Public-repo scan (held a push, then redacted)

A secrets / personal-info / cross-business scan was run on every Markdown file before any commit. **No API keys, tokens, passwords, or email addresses were found.** Flags that held the first push, under the public-repo rule (CONTEXT.md: the repo is public; nothing in it should name a real project, a private repo, or a local path) and the rule not to mix the operator's other work, were:

- References to a separate operator project, and a local path in that project's research folder, in `01-dex-horthy.md` and `ingestion-log.md`.
- A local machine path for this working tree in `gemini-roadmap-integration-2026-11-25.md`.
- Personal planning-doc URLs and "planning docs" wording in the ingestion log, the exported Gemini doc headers, and the integration analysis.
- The operator's first name throughout the proposal docs (about a hundred mentions). The public repo usually says "the operator."

Those have been redacted in this working tree (unredacted originals kept in a local backup, not for the public repo). Re-scan before any push.

## Prioritized fix list (for the operator)

1. **Confirm the redaction scan is clean** before any GitHub push (other-project names, local machine paths, personal planning-doc URLs, and the operator's first name).
2. **Reconcile delivery-order item 7** with the Phase 1–4 provider split so the schema is not read as a Phase 4-only task.
3. **Fold the market-scan feature-list rows into the roadmap** (Spec Kit optional in Phase 1, screenshots in the Phase 3 artefact pack, cheapest-first guardrails in the F4 contract bullet) or mark them explicitly as feature-list-only until he picks them.
4. **Name an owner for factory-engine work** on the provider layer and E6 private-endpoint path (Orchestrator / a factory-docs PR, not the job Builder), and add a one-line Approver-stage mapping.
5. **Tighten Phase 2 exit** (stand-in tests required; live local/LAN demo optional and not a phase gate) and drop E5.3 from the Phase 2 "if they start to matter" list so it stays Phase 4.

Lower priority: update the feature-list legend and the library index; decide whether the Gemini integration body's recommended list should be marked historical only (the header now says so).

## Push status (25 November 2026, 20:45 UK request)

The operator asked in chat to push once review and collation were complete. The review is written. The provider spec and roadmap entry are in place. A first pre-push scan was not clean; a redaction pass was then applied in this working tree. **No branch, commit, or pull request was created in this pass.** Nothing was force-pushed or merged. A further go-ahead is still required before any push.
