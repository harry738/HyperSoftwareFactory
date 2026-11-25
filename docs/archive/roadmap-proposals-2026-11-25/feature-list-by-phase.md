> **Archived 25 Nov 2026.** Historical proposal, superseded by [reference/build-plan.md](../../../reference/build-plan.md) (one roadmap). Its status claims and links are not maintained.

# Feature list by phase (proposal)

Proposal only. No official new IDs are allocated. Status is against `main` @ `351b660` (plan v6.4 plus the pull request #47 docs) on 25 November 2026. Auto-merge and auto-deploy are not adopted.

Legend: **existing** = on main in some working form (including stand-in tested); **planned** = already in v6.4 / the backlog and not built; **new proposal** = comes from Gemini, the videos, the integration analysis, or reference-library entries 05–15, and is not an official repo item yet.

| Feature | Phase | Source | Status |
|---|---|---|---|
| Fail-closed `unattended_merge` (missing key = off) | 0 | Repo issue #26; Horthy / IBM governance | Planned (bug open; template is already false, code fallback is true) |
| Supervised default; **never-self-merge** as a hard rule: the factory never merges its own work, and the author does not approve their own change; the operator merges | 0 (standing) | Repo v6.4; the operator's rule; IBM; [Gumloop, entry 13](../reference-library/13-gumloop-software-factory.md); [Itamar Friedman, entry 11](../reference-library/11-itamar-friedman-software-factory-engineer.md) | Existing (policy), now stated as a hard rule. Undercut until #26 lands. Auto-merge is not adopted |
| Always-stop rules by label and path | 0 (standing) | Repo E3.1 | Existing |
| Scripted `factory run` loop (intake → spec → build → gate → reviewers → approver → PR) | 0–3 | Repo E1–E4 | Existing (stand-in tested; E1.6 open) |
| Agents have no GitHub token; engine does GitHub calls | 0–4 | Repo E1.4; IBM scoped subagents | Existing |
| Autonomy cap at **L2 (workflow-orchestrated)**; agents never grant themselves access; L3/L4 out of scope | 0 (standing) | [Agent Baseline, entry 14](../reference-library/14-agent-baseline-secure-software-factory.md) | New proposal (matches how `factory run` already works) |
| Four security boundaries documented and enforced: sandbox, network, supply chain, identity/access | 0–1 (standing) | [Agent Baseline, entry 14](../reference-library/14-agent-baseline-secure-software-factory.md); repo E6; `docs/roadmap/llm-provider-integration.md`; `docs/roadmap/agent-roster.md` | New proposal (documents existing intent) |
| Event log and per-stage cost/time | 0, 4 | Repo E2.3 | Existing |
| Budgets, stall kill, retries | 2 | Repo E2.1–E2.2 | Existing |
| Container and network allowlist | 2 | Repo E6.1–E6.2 | Existing (not yet run signed-in) |
| Merge-main when the base moves | 2–3 | Repo E5.4–E5.5 | Existing |
| Daily budget | 2 | Repo E5.2 | Existing |
| Concurrency > 1 | 2 | Repo E5.1 | Planned |
| Scheduled `factory run` | 4 | Repo E5.3, F2 | Planned |
| Flaky-check policy | 2 | Repo E3.5 | Planned |
| E6.3–E6.4 (remaining container / console work) | 2–4 | Repo E6 | Planned |
| First real-project job (issue → PR for the operator) | 2 | Repo E1.6 | Planned (open) |
| `factory onboard` and readiness checklist | 1–2 | Repo E1.2 | Existing |
| Operator dashboard | 4 | Repo (dashboard / later E6.4) | Existing (basic); telemetry tiles below are new |
| Risk routing (`low` / `medium` / `high`, path rules, `human-merge`) | 1 | Repo; feature comparison "ahead" | Existing |
| Named Tier 1 / 2 / 3 protocol (checklist / full plan / ADR + rollback + the operator) | 1 | Gemini risk matrix; maps onto existing routing | New proposal |
| `AGENTS.md` Always / Ask First / Never checklist | 1 | Gemini; Horthy suggested next step | New proposal (file exists, checklist does not) |
| Living spec templates (`docs/specs/` or equivalent) | 1 | Gemini; Horthy "unify the forge" | New proposal (job specs exist; durable folder convention does not) |
| ADR templates (`docs/adr/`) | 1 | Gemini; Horthy expected pain; `grill-with-docs` skill | New proposal (skill mentions ADRs; no repo layout) |
| 3-part discovery questionnaire on intake | 1 | Gemini | New proposal |
| Plan-approval gate before build (Tier 2/3), with Holmes **spec gate** then **triage gate** | 1 | Gemini Phase 1 exit; IBM plan-before-execute; [Ben Holmes / Warp, entry 06](../reference-library/06-ben-holmes-software-factory-as-code.md) | New proposal (spec stage exists, hard gate does not) |
| Optional GitHub Spec Kit (or the same Specify → Plan → Tasks artefact shapes) as a Phase 1 process layer, still orchestrated by `factory run` | 1 | Market scan (Spec Kit official docs; LinkedIn SDD write-ups) | New proposal |
| Prototype / feature-flag rule (vibe work stays out of production) | 1 | Horthy; IBM; vendored `prototype` skill | New proposal (skill exists; no factory rule) |
| Focused-context rule in the checklist | 1 | IBM | New proposal |
| Template `checks.sh` examples (lint, types, tests) | 2 | Repo carried-over backlog; Gemini Phase 2; Horthy back pressure | Planned (template currently has no checks) |
| Secret scan and dependency audit examples | 2 | Repo carried-over backlog; Gemini | Planned |
| Complexity / anti-slop check in the template | 2 | Repo CONTEXT rule 3; Horthy; carried-over backlog | Planned (not built; `deslop` is a skill, not a gate) |
| Language-specific "no skipped gates" rules | 2 | Gemini (`--no-verify`, `@ts-ignore`, `any`) | New proposal — **per project stack**, not a factory TypeScript toolchain |
| Spec-to-test traceability | 2–4 | Gemini; pairs with F5 | New proposal + planned F5 |
| Optional coverage floor for new domain logic | 2 | Gemini ≥90% branch coverage | New proposal as **optional project policy**; not a global factory CI rule (conflict if applied globally) |
| Read-only fresh-context reviewers | 3 | Repo E4; Gemini Phase 3; IBM validate step | Existing |
| Security reviewer on sensitive paths | 3 | Repo surface reviewers; Gemini / later OWASP packs | Existing; packs are new |
| PR artefact pack (spec, ADR, checks, rollback note, and evidence of a **failing test that then passes**) plus five merge-risk headings: Alignment, Impact, Verification, Rollback cost, Error detection | 3 | Gemini 3.2; [Gumloop, entry 13](../reference-library/13-gumloop-software-factory.md); [Ben Holmes / Warp, entry 06](../reference-library/06-ben-holmes-software-factory-as-code.md) | New proposal (evidence on PR is partial today) |
| PR screenshots / browser notes on UI changes, attached with check logs | 3 | Market scan (Cursor artefacts; Firecrawl) | New proposal |
| CI / gate block non-compliant merge | 3 | Repo gate + required CI; Gemini 3.3; #26 | Partial until #26 and project checks exist |
| Tier 3 always stops for the operator | 3 | Gemini; the operator's rule | New proposal as an explicit protocol (always-stop / `human-merge` already can express it) |
| F3 weekly Kaizen and learnings file, plus a **knowledge loop**: agents flag gaps; a separate **Curator** role opens PRs that update skills / `AGENTS.md` / domain knowledge and never merges | 4 | Repo F3; Horthy compound lessons; `retro` skill; [Harrison Chase, entry 05](../reference-library/05-harrison-chase-knowledge-factory.md) | Planned (F3) + new proposal (Curator) |
| Dashboard: **cost per accepted change** as the headline metric, plus first-pass green rate, retry counts, later tier mix | 4 | Gemini 4.2; uses existing event log; [Itamar Friedman, entry 11](../reference-library/11-itamar-friedman-software-factory-engineer.md) | New proposal (do not add Prometheus — v6.4 non-goal) |
| Context7 / live-docs hook | 4 | Gemini 4.1; repo `reference/context7-docs-mcp.md` | Planned (note only, not wired) |
| OWASP or language security rule packs | 4 | Gemini 4.1 | New proposal |
| F4 drop-folder contract (docs) | 4 | Repo open question 1 | New proposal (docs first) |
| F4 / F8 market watch and other external intake | 4 | Repo F4, F8; official APIs only | Planned (not built) |
| Layered cheapest-first guardrails on untrusted agent inputs (static checks, then the tool-less summariser, then no auto-queue); fail closed if a check cannot run; optional OWASP LLM-style cases in the F4 contract | 4 (also sharpens Phase 0) | Article: Wely Lau, Layered LLM guardrails on Apigee (demo, not an official Google product); repo F4/F8 tool-less summariser; issue #26 | New proposal |
| F5 holdout checks | 4 | Repo F5; Gemini test mapping | Planned |
| F6 deploy and rollback; incident and performance agents **propose but do not execute** (no auto-deploy) | 4 | Repo F6; IBM rollback; v6.4 open question 2; [OpenAI / Pragmatic Engineer, entry 07](../reference-library/07-pragmatic-engineer-openai-software-factory.md) | Planned + new proposal (propose-but-don't-execute) |
| F2 Hermes schedule and notifications | 4 | Repo F2, E5.3 | Planned |
| F1 Dev council in shadow | 4 | Repo F1, A4 | Planned (no merge power in this plan) |
| F7 second operator project | 4 | Repo F7 | Planned |
| Crawl4AI for allowed public pages | 4 | Repo README planned integrations | Planned (not wired; no stealth / block evasion) |
| Optional Prismor **observe-mode** trial around the Claude Code harness (no enforce; operator yes required; not installed in this pass) | 4 | [Prismor, entry 15](../reference-library/15-prismor.md) | New proposal (optional trial only) |
| FullAuto / unattended merge for any tier | — | Repo A1–A8; auto-merge also promoted in entries 09, 10, and 12 and **not adopted** | Planned and **out of this deployable plan** |
| External multi-tenant self-service onboarding | — (deferred) | Gemini Phase 3 or 4 (the two docs disagree); conflicts with "own projects only" | Deferred — not a near-term feature |
| Reusable domain packs for outside teams | — (deferred) | Gemini Phase 4 | Deferred until after F7, and only for the operator's projects at first |
| Factory-wide `pnpm` / `tsc` / `Vitest` harness | — (rejected as engine default) | Gemini Phase 2 | Rejected as a global factory stack; allowed only as a **project** `checks.sh` |
| Global 90% coverage merge blocker | — (rejected as engine default) | Gemini Phases 2–3 | Rejected as global; optional per project |
| v6.5 release framing (R1–R6) | docs only | Open PR #42 | Planned docs; rebase or close; not the live plan |
| LLM provider abstraction (Claude Code harness plus completion APIs) with three uniform connection types: local (Ollama native or OpenAI-compatible on the same machine), LAN (same APIs at a private host:port, with TLS/auth, health checks, and a separate E6 private-endpoint allowlist), and OpenRouter as an aggregator | 1–4 | The operator, 25 Nov 2026 voice; `docs/roadmap/llm-provider-integration.md`; would relax the v6.4 "other models for builder/reviewers" non-goal only if he agrees | New proposal (default stays Claude Code) |
| Per-role model binding and fallback chains; `data_leaving_lan` defaults to deny; security and fresh-context reviewers fail closed (no silent downgrade to a weaker model) | 1, 3 | `docs/roadmap/llm-provider-integration.md`; issue #26 fail-closed principle | New proposal |
| Provider usage in `usage.jsonl` / `events.jsonl`: local and LAN record tokens, latency, and $0 API cost (optional electricity/amortised estimate); OpenRouter uses reported `usage.cost`; USD budget caps still stop the job | 2, 4 | `docs/roadmap/llm-provider-integration.md`; extends repo E2.3 | New proposal |
| E6 private-endpoint path for local sidecars and LAN model hosts (`NO_PROXY` / distinct allowlist; HTTP only to private addresses) | 2 | Repo E6.1; `docs/roadmap/llm-provider-integration.md` | New proposal |

## Suggested delivery order (PRs, the operator merges)

1. #26 fail-closed merge default.  
2. `AGENTS.md` checklist + spec/ADR templates + questionnaire + Tier 1–3 write-up.  
3. Template `checks.sh` examples, including anti-slop / secret scan.  
4. E1.6 first real job (operational, plus any blocking engine fixes).  
5. PR artefact pack (including failing-then-passing evidence and the five merge-risk headings) and explicit Tier 3 stop.  
6. Docs-only F4 drop-folder contract, including cheapest-first guardrails on the drop folder; then only the Phase 4 slices the operator picks.
7. LLM provider integration, as in `docs/roadmap/llm-provider-integration.md`: config schema first, then local/LAN adapters, then fail-closed reviewer bindings; OpenRouter and any paid spend only after the operator's yes.

Nothing in this list is on GitHub until he says yes.
