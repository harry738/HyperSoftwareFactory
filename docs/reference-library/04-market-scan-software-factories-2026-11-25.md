# 04 Market scan: AI software factories, agentic coding, spec-driven development

Local reference-library notes only. Not pushed. Read-only research on 25 November 2026 (Europe/London). Nothing was posted, liked, replied to, voted on, or logged into on X, Reddit, LinkedIn, Hacker News, or any vendor site.

**Method.** Public reads only. X posts came from the official X search API (`search_posts_all`, three queries, posts from 1 September 2026 onward, 72 results). Hacker News came from the official Algolia API (`hn.algolia.com/api/v1/search`). Reddit's public `.json` endpoints returned HTTP 403, so Reddit items were found via web search of public thread URLs and are cited as those threads. LinkedIn items are public posts/articles found via web search; no LinkedIn login was used. Feature claims were confirmed against official docs, GitHub repository metadata (API snapshot ~20:36 UK time on 25 November 2026), or the author's own published post. Secondary write-ups are labelled as such and are not treated as independent measurement.

**Factory baseline used for the gap analysis:** local `docs/roadmap/deployable-roadmap.md`, `docs/roadmap/feature-list-by-phase.md`, and `docs/roadmap/agent-roster.md`, against `main` @ `72a982c` / plan v6.4 as previously reviewed.

`principles.md` is still deferred until the operator says the reference set is complete.

---

## 1. Main practices the best builders are using

Each practice is tied to a primary or clearly labelled source. These are practices, not a claim that every vendor does all of them well.

### Start from a spec, not a chat prompt

GitHub Spec Kit's official docs describe a core process of **Specify → Plan → Tasks → Implement → Converge**, with each phase producing a Markdown artefact for the next, so the agent works from structured context rather than ad-hoc prompts. Last updated 4 November 2026. ([Spec Kit docs](https://github.github.com/spec-kit/))

Public discussion treats this as the alternative to "vibe coding." A LinkedIn post by Ashraf alhnaiti (13 November 2026) describes a Claude Code workflow in which a rule is given an ID in `spec.md`, a planner maps it to a named test, an implementer opens a draft PR, a separate reviewer checks the diff against the spec, and a human reviews only after both CI and the reviewer are green. "The agent that writes the code never grades it." ([post](https://www.linkedin.com/posts/ashraf-alhnaiti-48907720_specdrivendevelopment-claudecode-aiagents-activity-7526882450661298176-WJW3))

Martin Fowler's 16 October 2025 article, still widely cited on HN, compares Kiro, Spec Kit, and Tessl as three takes on spec-driven development. ([article](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html), [HN](https://news.ycombinator.com/item?id=45610996))

### Keep the control loop deterministic; do not throw more agents at every step

Eliseo (Elvis) Saravia wrote on X (15 November 2026): "The best agentic systems I have built and seen other top engineers build involve lots of boring deterministic steps. You can't just throw more LLM agents at every problem and expect reliability to improve." ([post](https://x.com/omarsar0/status/2122035455793188980), 523 likes at fetch)

Peter Scheffer, on LinkedIn, describes a pre-spec gate with **no AI**: schema validity, an operational envelope (retries, timeouts, failure behaviour), and a policy tier (T0–T3, path globs, T3 needs human sign-off). "The agents can be unreliable. The gate is the fixed point." ([post](https://www.linkedin.com/posts/peterscheffer_buildinpublic-softwarefactory-agenticharness-activity-7509009071593676800-Hcjz))

Bassel Haidar (21 May 2026) argues the factory needs a **control plane**: planning, a validation contract written before code, policy gates, and an evidence trail, with worker agents separated from validator agents. Humans keep goals, risk, and final acceptance. ([article](https://www.linkedin.com/pulse/ai-software-factory-needs-control-plane-bassel-haidar-oarue))

This matches Dex Horthy's earlier talk (forward and back pressure; the official transcript does not publish a numbered list of 12) and the IBM vibe-vs-agentic video already in this library.

### Isolate each job, then verify automatically, then leave a human at the merge gate

Firecrawl's 11 September 2026 survey of published accounts (Stripe, Spotify, Shopify, Uber, Ramp, and others — **Firecrawl's retelling, not independently re-measured here**) defines a factory as five stages with a gate at each: intake, isolation, tools, verification, and a merge gate. "Every company that made this work built the gates before the fleet." It quotes Stephen Toub on review becoming the bottleneck, and gives Faire as requiring two human reviews on agent-authored PRs. ([Firecrawl](https://www.firecrawl.dev/blog/ai-software-factory), also on [HN](https://news.ycombinator.com/item?id=49666960), 31 points)

Cursor's official Cloud Agent security docs: each run gets an isolated VM; the agent "pushes its branch and opens a pull request for a human to review before anything merges." "Nothing merges until a person reviews the change." They also document prompt-injection risk for unattended cloud agents, egress allowlists, and signed commits. ([Cursor: security](https://cursor.com/docs/cloud-agent/security), [overview](https://cursor.com/docs/cloud-agent))

On Reddit, several builders describe the same skeleton (issue or board → isolated git worktree or Docker → tests → PR → human, with auto-merge off or tightly gated). Examples: [bunker](https://www.reddit.com/r/ClaudeAI/comments/1xagj87/sandboxed_claude_agents_wrote_159_of_my_188_prs/) (required CI; human wait on CI/config/agent-instruction changes), [Night Watch](https://www.reddit.com/r/ClaudeAI/comments/1rzkef8/i_built_a_cli_that_runs_my_agents_on_a_schedule/) (author recommends leaving auto-merge off), [o8](https://www.reddit.com/r/ClaudeAI/comments/1vdtnhv/ive_been_running_claude_code_as_the_orchestrator/) (worktrees; "nothing merges until I approve it"). These are author reports, not audits.

### Separate the writer from the reviewer, and attach evidence

Cursor agents produce screenshots, videos, and logs and can attach them to the PR. ([capabilities](https://cursor.com/docs/cloud-agent/capabilities))

The LinkedIn SDD workflow above and the IBM talk both insist the implementer does not grade its own work. Firecrawl likewise reports independent verification (for example Spotify's "LLM judge") as a published pattern, again as Firecrawl's citation of those companies.

A personal X workflow from Michelle Mayes (2 September 2026) is typical of careful practitioners: product-management agent → issue → PR → inline review → deslop → tests and CI → QA, then ship. ([post](https://x.com/michellejmayes/status/2095210219626246234))

### Budget tokens, watch the loop, and treat untrusted input as hostile

Cost and review capacity show up repeatedly as the real limits (Firecrawl; several X posts on token burn). Cursor documents egress controls and prompt-injection mitigations for cloud agents. Wely Lau's Apigee article already in this library (entry 03) says to stack cheapest-first guardrails and not treat one demo's catch rate as a transferable benchmark. Firecrawl's factory article also places prompt-injection detection on every web fetch the agent makes (vendor blog; their product interest is declared on the same page).

Mastra's 18 November 2026 Show HN (159 points) describes "Mastra Factory" as the open-source factory they use to build Mastra: a configurable agentic kanban board, @-taggable in Slack, durable agents, a cited markdown wiki, PR-comment signals, a customizable cloud sandbox, and a triage → plan → build → review → shipped workflow. The authors say that in one week Factory opened and merged 238 PRs alongside 630 human-merged PRs, and that they have closed the repo to outside contributors in favour of detailed issue repros. Those figures are the authors' own, from the HN text. ([HN item](https://news.ycombinator.com/item?id=50548660))

---

## 2. Open-source vs paid: short feature comparison

Star counts and push times are from the GitHub API on 25 November 2026, about 20:36 UK time. "Y / P / N / ?" means yes, partial, no, or not verified from official docs in this pass. This is a feature sketch, not a product recommendation or a claim of superiority.

| Tool | Licence / model | Spec intake | Isolation / sandbox | Parallel jobs | Independent review agent | CI / test gate | Default merge stance | Telemetry / evidence |
|---|---|---|---|---|---|---|---|---|
| **GitHub Spec Kit** | OSS, MIT, 151,368 stars, pushed 25 Nov 2026. Process toolkit, not a hosted factory. ([docs](https://github.github.com/spec-kit/), [repo](https://github.com/github/spec-kit)) | Y — Specify → Plan → Tasks → Implement → Converge; also bug-fix and idea-assessment flows | N (uses whatever agent you attach) | N (orchestration is yours) | N (templates only) | P — quality checklists; community "Quality Gates" extension, not core CI | N — you merge | Markdown artefacts between phases |
| **OpenHands** | OSS, MIT, 94,329 stars, pushed 25 Nov 2026. ([repo](https://github.com/All-Hands-AI/OpenHands), [SDK docs](https://docs.openhands.dev/sdk)) | P — task/prompt; not a Spec Kit clone | Y — docs describe Docker/Kubernetes agent server | P — multi-agent tasks are a stated SDK use | ? not confirmed as a built-in independent reviewer in this pass | P — agents can run commands/tests in the environment | ? | SDK/server; cloud product exists alongside OSS |
| **Aider** | OSS, Apache-2.0, 50,255 stars; last push **22 May 2026** (slower than the others in this snapshot). Terminal pair-programmer. ([repo](https://github.com/Aider-AI/aider)) | P — chat + repo map, not a factory queue | N (local repo) | N | N | P — can run tests you ask for | N — human commits | Local session |
| **Cline** | OSS, Apache-2.0, 71,894 stars, pushed 25 Nov 2026. "Autonomous coding agent as an SDK, IDE extension, or CLI." ([repo](https://github.com/cline/cline)) | P | P — local/IDE; SDK possible | ? | ? | P | N | IDE/SDK |
| **Goose (Block)** | OSS, Apache-2.0, 56,990 stars, pushed 25 Nov 2026. Extensible agent; "install, execute, edit, and test with any LLM." ([repo](https://github.com/block/goose) as resolved by API) | P | P | ? | N as a factory | P — can execute and test | N | Local/extensible |
| **BMAD-METHOD** | OSS, licence SPDX not asserted in the API (`NOASSERTION`), 55,740 stars, pushed 25 Nov 2026. Role-based agile method (PM, architect, dev), not a hosted runner. ([repo](https://github.com/bmad-code-org/BMAD-METHOD)) | Y — structured roles and planning | N | N | P — method separates roles | N | N | Process / docs |
| **Mastra Factory** | Authors say it is fully open source (`npm create factory`) in a 18 Nov 2026 Show HN. Repo URL was not verified in this pass (a guess at `mastra-ai/factory` 404'd). | P — triage / plan stages in their workflow | Y — "customizable cloud sandbox" (author claim) | Y — authors describe senior engineers kicking off parallel sessions | P — review is a named stage | P — bug/vuln scanners mentioned by authors | Authors say Factory opened **and merged** 238 PRs in a week — that is their report, and it is a different merge stance from the operator's rule | PR-comment signals, cited wiki |
| **Cursor Cloud Agents** | Paid (Cursor). Official docs. ([overview](https://cursor.com/docs/cloud-agent), [security](https://cursor.com/docs/cloud-agent/security)) | P — task from issue, Slack, Teams, Jira, Linear, GitHub, or prompt | Y — isolated Firecracker microVMs; egress allowlists | Y — "as many agents as you want in parallel" | P — hooks, Bugbot / Security Review mentioned; not the same as HSF's staged read-only reviewers | Y — agents test in the VM; push after testing | **Human reviews the PR; nothing merges until a person reviews** | Screenshots/videos/logs; signed commits; admin session logs |
| **GitHub Copilot coding / cloud agent** | Paid Copilot. Official docs describe cloud sandboxes or Actions-based environments, issue/PR workflows, Copilot review, and (for third-party agents, public preview) automatic security validation with CodeQL, secret scanning, and advisory checks. ([Copilot on github.com](https://docs.github.com/en/copilot/concepts/agents/coding-agent); [third-party agents](https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-third-party-coding-agents)) | P — issues, prompts, Spaces | Y — cloud sandbox or Actions | P — multiple sessions / agents tab | P — Copilot can review PRs | Y — security scans on generated code (third-party agent path) | Agent "request[s] a review from you" (third-party docs) | Usage metrics for Enterprise; session context |
| **Claude Code / Codex** | Paid model/CLI subscriptions; often used as the *engine* inside a factory (including HyperSoftwareFactory, bunker, Night Watch). Not themselves a multi-project control plane. | P | P — local or whatever harness wraps them | P — if the harness adds it | N unless the harness adds a second session | P | N unless the harness adds merge | Usage in the harness |
| **HyperSoftwareFactory** (for contrast) | OSS, MIT root / GPLv3 engine. Plan v6.4. | P — intake + spec stage; durable `docs/specs` / ADR templates still a proposal | Y — worktrees + container/allowlist (not yet run signed-in); checks live outside the worktree | Planned (E5.1 open) | Y — read-only specialist reviewers (stand-in tested) | P — gate exists; template `checks.sh` is empty; E1.6 not run | Supervised: the operator merges; **but a missing `unattended_merge` key still defaults to on (#26)** | Event log + usage log; dashboard tiles still a proposal |

**How the market splits.** Open-source strength is process kits (Spec Kit, BMAD) and self-hosted engines (OpenHands, Cline, Goose, Aider). Paid cloud agents sell isolation, parallelism, artefacts, identity, and org policy (Cursor, Copilot). Almost every serious write-up still leaves a **human at the merge gate**. Factories that advertise auto-merge (some Show HN / Reddit tools; Mastra's own merge counts) are the exception, not the consensus of the official Cursor/Copilot docs or of Firecrawl's "Faire" example. The operator's "PRs only, I merge" rule is aligned with that consensus, not behind it.

---

## 3. Gap analysis vs the local deployable plan

The operator's bar: **direct match / incorporate first**, then partial components, then inspiration. Scores are impact (H/M/L) × effort (L/M/H) against `docs/roadmap/deployable-roadmap.md`, `docs/roadmap/feature-list-by-phase.md`, and `docs/roadmap/agent-roster.md`. These are proposals, not official IDs.

### Where HyperSoftwareFactory already leads or is at least level

- **A scripted orchestrator, not a model choosing the next stage** — direct match to Saravia, Scheffer, Haidar, and v6.4. The roster already says only `factory run` holds the GitHub token.
- **Path- and label-based risk routing, always-stop rules, and specialist read-only reviewers** — the repo's own 22 November feature comparison already called this a lead. Still true against this scan. Matches "writer never grades itself."
- **Isolation of checks from the builder worktree**, plus a container and network allowlist (E6 built, not signed-in) — same idea as Cursor egress allowlists and Reddit worktree/Docker patterns, implemented on the operator's machine rather than a vendor VM.
- **Supervised merge as policy** — aligned with Cursor and with Night Watch / o8 / Faire-as-reported-by-Firecrawl. The **implementation hole** is issue #26.
- **Budgets, stall kills, retries, and an event log** — closer to a control plane than most OSS harnesses.

### Where it lags (clearest opportunities, ranked)

| Rank | Opportunity | Impact × effort | Phase | Bar | Why the market says it matters |
|---|---|---|---|---|---|
| 1 | **Fail closed on `unattended_merge` (#26)** | H × L | 0 | Direct match | Official Cursor docs and the common practitioner advice put a human at the merge gate. A missing key that defaults to merge undercuts that. |
| 2 | **Durable specs, ADRs, Always/Ask-First/Never checklist, 3-part questionnaire, plan-approval gate** | H × M | 1 | Direct match (Spec Kit / SDD / Gemini already proposed) | Spec Kit and the LinkedIn SDD write-ups make this the default serious practice. The factory has a spec *stage* but not the in-repo templates or a hard plan gate. Optionally **incorporate Spec Kit** as the artefact format; do not replace `factory run`. |
| 3 | **Fill `checks.sh` (lint, tests, secret scan, anti-slop) and run E1.6** | H × M | 2 | Direct match | Firecrawl: review is the bottleneck; gates must exist before the fleet. The gate script today has no checks, and the first real job is still open. |
| 4 | **Cheapest-first static + policy filters on untrusted intake (issue text, F4/F8 drop folder); fail closed if a check cannot run** | H × M | 4 (sharpens 0) | Direct match to entry 03; also Cursor prompt-injection + Firecrawl "detect on every fetch" | Already on the feature list from the Apigee article. This scan reinforces it. Not a proposal to install Apigee or Model Armor. |
| 5 | **PR evidence pack (spec/ADR links, check logs, screenshots or browser notes) plus dashboard tiles from the existing event log** | M × L | 3–4 | Partial incorporate (Cursor artefacts; Mastra/Firecrawl review-tax) | Cheap, uses machinery already there, and attacks the review bottleneck without auto-merge. |
| 6 | **Holdout tests (F5) and independent QA evidence** | M × M | 4 | Already planned; market confirms | Alhnaiti / Haidar / IBM: the writer does not grade the work. |
| 7 | **Concurrency (E5.1) and scheduled runs (E5.3 / F2)** | M × M | 2 / 4 | Already planned | Cursor and Mastra emphasise parallelism and Slack/@-tag kickoff. Schedule is also Night Watch's pitch. Keep it after E1.6. |
| 8 | **Signed, attributed agent commits** | L–M × M | 3 | Inspiration (Cursor) | Useful if branch protection later requires verified commits. Not P0. |
| 9 | **Vendor-style microVMs, Slack-first kanban, issue "actionability" scoring** | L–M × H | later | Inspiration only | Cursor Firecracker VMs and Sentry-style intake scoring (via Firecrawl) are real, but E6 plus a labelled issue queue already cover the need for an operator-owned factory. Do not take Mastra's "factory merges" counts as a goal. |

**Do not incorporate:** auto-merge as a default, a TypeScript-only factory toolchain, a global 90% coverage blocker, or near-term multi-tenant onboarding for outside teams (already deferred in the deployable plan).

### Mapping onto the five phases

- **Phase 0** stays first and is now even more clearly a market-aligned P0.
- **Phase 1** should explicitly allow GitHub Spec Kit (or its artefact shapes) as an optional process layer on top of intake/spec, still enforced by the scripted orchestrator.
- **Phase 2** is where HSF either proves itself (E1.6 + real checks) or stays a promising pilot.
- **Phase 3** should pick up artefact-rich PRs, not new autonomy.
- **Phase 4** keeps F3 learnings, telemetry tiles, F4/F8 with cheapest-first guardrails, F5, F6, F2, F1 in shadow, F7. Slack/@-tag intake can wait until F2.

---

## Limits of this scan

- X coverage is three relevancy searches since 1 September 2026, not a complete census of every vendor account. Handles were not assumed in advance; posts were taken as they appeared in the result set.
- Reddit `.json` was blocked (403); only search-indexed public threads were used.
- LinkedIn was search-only; post dates and wording are from the public pages returned by search.
- Vendor internals cited by Firecrawl were not re-verified with those companies.
- Star counts change; they are a snapshot from the GitHub API at the time above.
- No one was contacted, and no repo or social account was written to.
