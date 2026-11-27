# 01 Dex Horthy talk

Source: https://www.youtube.com/watch?v=-NFMsM2y0Vk

Mapping vs repo (25 Nov 2026) — extracted from an earlier research note in a separate operator project:

# HyperSoftwareFactory: walkthrough, research/scraping options, and Horthy mapping

**Date:** 25 November 2026  
**Scope:** Read-only review of [harry738/HyperSoftwareFactory](https://github.com/harry738/HyperSoftwareFactory). Nothing was written to the repository, and no pull requests or issues were opened.

**Note:** This is a local research note for HyperSoftwareFactory only. It should not be mixed with the operator's other projects, drives, or inboxes.

Times below are Europe/London. GitHub timestamps ending in Z are UTC; in late November the zone is GMT (UTC+0), so the clock time matches unless British Summer Time is noted.

---

## 1. Repo walkthrough (current main)

**Correct name:** `harry738/HyperSoftwareFactory` ([repository](https://github.com/harry738/HyperSoftwareFactory)). There is no accessible repo named `Hyper-Software-Factory`. The repo is public, MIT at the root, GPLv3 for `factory/`, `.claude/agents/` and `.claude/skills/factory/` ([README licence section](https://github.com/harry738/HyperSoftwareFactory/blob/main/README.md), [LICENSE](https://github.com/harry738/HyperSoftwareFactory/blob/main/LICENSE), [factory/LICENSE](https://github.com/harry738/HyperSoftwareFactory/blob/main/factory/LICENSE)).

**Current tip of main:** [`72a982c`](https://github.com/harry738/HyperSoftwareFactory/commit/72a982c7c9103b5f53a85f22db0c5de6000c6c8f), merge of [#46](https://github.com/harry738/HyperSoftwareFactory/pull/46) on 25 November 2026, 07:37 GMT (Europe/London). The live build plan on main is **v6.4** ([`reference/build-plan.md`](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md)). An earlier review that described main as holding only plan v3, with v6.1 existing only on open PR #6, is out of date: #3, #5 and #6 were merged on 23 November 2026, 23:32 GMT, and many later engine PRs have landed since.

### What the project does

The README describes it as an open-source, agent-driven software factory: labelled GitHub issues become scoped changes and independently reviewed pull requests, across projects, from one central factory. A deterministic script owns orchestration; specialist Claude Code agents write and review; project-defined gates and policy control outcomes. **Supervised by default.** The README is explicit that this is a working pilot, not a production-autonomy claim: the central runner has passed end-to-end tests with GitHub and model stand-ins, but the first run on a real project remains open. ([README](https://github.com/harry738/HyperSoftwareFactory/blob/main/README.md), [CONTEXT.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/CONTEXT.md))

### Top-level layout

From the root listing on main and the README contents table:

| Path | Role |
|---|---|
| `factory/` | Working engine: `bin/factory`, `bin/run`, `bin/job`, `bin/gate`, `bin/route`, templates, tests, dashboard |
| `.claude/agents/`, `.claude/hooks/`, `.claude/skills/` | Stage agents (intake, spec-writer, builder, reviewers, approver), a hook that blocks hand merges, and pinned skills including `factory`, `deslop`, `research`, `prototype`, `to-spec` |
| `reference/` | Build plan, feature comparison, competitor list, architecture, Binley pilot |
| `config/` | Examples only (registry shape, README template, `self.example/`) |
| `scripts/` | Onboarding wizard, multi-project dashboard, `test.sh` (also used by CI) |
| `deploy/` | Container and network allowlist (E6) |
| `docs/` | README images and archived READMEs |
| `AGENTS.md`, `CONTEXT.md` | Rules for changing this repo; product purpose and hard rules |

The public repo must not name a real project, private path or secret. Those live in a private `$FACTORY_HOME`. ([AGENTS.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/AGENTS.md), [CONTEXT.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/CONTEXT.md))

### Roadmap and docs

- **Authoritative status on main:** [build plan v6.4](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md). Engine track E1.1–E1.5 and most of E2–E6 are marked done in code and tested with stand-ins. Still open on that plan: **E1.6** (first real-project job), **E3.5** (flaky-check policy), **E5.1** (concurrency), **E5.3** (scheduled run), **E6.3** and **E6.4**. Features F1–F8 and FullAuto A1–A8 are not built. No autonomy level is earned yet.
- **Open docs PR:** [#42](https://github.com/harry738/HyperSoftwareFactory/pull/42) proposes **v6.5**, with six evidence-gated releases (R1–R6). It was opened on 25 November 2026, 01:20 GMT, against `a88072d`, before #43–#46 merged. Some status rows on that branch are behind current main (for example it still marks E5.4/E5.5 and E6.1/E6.2 as open, which v6.4 on main now marks done). It is documentation only. It has not been merged.
- Other design docs: [reference architecture](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/software-factory-reference-architecture.md), [multi-project architecture](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/factory-multi-project-architecture.md), [feature comparison](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/feature-comparison.md), [competitors.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/competitors.md) (last checked 22 November 2026).

### PRs #2, #3, #5 and #6 (requested)

| PR | State | Notes |
|---|---|---|
| [#2](https://github.com/harry738/HyperSoftwareFactory/pull/2) | Closed, **not merged**, still draft. Head `ce7bf9be`. | Title: harden assurance and document desktop subscription-first operation. Do not revive or merge without a fresh review: an earlier read-only review flagged that the branch still contained a real registry and a private URL. This review did not re-open those files. |
| [#3](https://github.com/harry738/HyperSoftwareFactory/pull/3) | Merged 23 November 2026, 23:32 GMT | Harvest Binley fixes, gate fix, build plan v6. |
| [#5](https://github.com/harry738/HyperSoftwareFactory/pull/5) | Merged at the same time | Central factory home, onboard, script-driven run (E1). |
| [#6](https://github.com/harry738/HyperSoftwareFactory/pull/6) | Merged at the same time. Head `cccd09d3`. | Stage limits, retries, event log, feedback (E2). Its copy of the plan is **v6.1**. That plan already described F4 (market watch) in the same terms as today's v6.4, but most later engine work (E3–E6, E2.5–E2.6, E5.4–E5.5) was still open on that snapshot. |

### Open issues and the one open PR that matter

GitHub listed 19 open items (18 issues + PR #42) when fetched on 25 November 2026.

- **[#26](https://github.com/harry738/HyperSoftwareFactory/issues/26)** (bug): "Treat a missing `unattended_merge` key as off." Still open. The template sets `"unattended_merge": false` in [`factory/config.json`](https://github.com/harry738/HyperSoftwareFactory/blob/main/factory/config.json), but `factory/bin/run` on main after #46 still uses `CONFIG.get("unattended_merge", True)` ([#46 diff on `factory/bin/run`](https://github.com/harry738/HyperSoftwareFactory/pull/46)). A missing key would still fail open. This is the highest-priority safety gap found in this pass.
- Other open bugs: [#27](https://github.com/harry738/HyperSoftwareFactory/issues/27)–[#32](https://github.com/harry738/HyperSoftwareFactory/issues/32) (onboard name validation, CI wait bypassing the stand-in, review-evidence path matching, feedback-file sort, readiness checklist, needs-info resume).
- Docs issues [#15](https://github.com/harry738/HyperSoftwareFactory/issues/15)–[#18](https://github.com/harry738/HyperSoftwareFactory/issues/18) may be partly stale after later README PRs; they should be re-checked before more docs work.
- Test-coverage enhancements [#19](https://github.com/harry738/HyperSoftwareFactory/issues/19)–[#24](https://github.com/harry738/HyperSoftwareFactory/issues/24). [#25](https://github.com/harry738/HyperSoftwareFactory/issues/25) asked for factory-home projects on the dashboard; related work later landed in [#37](https://github.com/harry738/HyperSoftwareFactory/pull/37)/[#39](https://github.com/harry738/HyperSoftwareFactory/pull/39) and should be re-checked before more work.
- **[#42](https://github.com/harry738/HyperSoftwareFactory/pull/42)** is the only open pull request.

### Health and multi-agent readiness

The repo is very active (many engine PRs merged 22–25 November 2026) and the design is unusually explicit: scripted control flow, budgets, always-stop paths, read-only reviewers, and an evidence track before autonomy. Multi-agent *delivery* (intake, spec, build, gate, specialist reviewers, approver) already exists in code. It is **not** ready for unattended multi-agent management on a real project until E1.6 is done, the fail-closed merge default in #26 is fixed, and isolation is proven with a signed-in run (E6 is built but "not yet run signed in", per the build plan). FullAuto is documented and not built. The README's "Now" item is still E1.6, with every job stopping for the operator.

---

## 2. What the social scraping / research component does

**There is no implemented social-scraping or market-watch pipeline in the codebase on main.** A code search on the default branch for scrape, scraping, crawler, crawl, social, twitter, reddit and research as source terms returned no crawl/scrape implementation. Planned intake research is named, not wired.

What exists today:

1. **Plan F4 — Weekly Kaizen, outside view** (same wording on v6.1 in [#6](https://github.com/harry738/HyperSoftwareFactory/blob/cccd09d3/reference/build-plan.md), v6.4 on [main](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md), and v6.5 on [#42](https://github.com/harry738/HyperSoftwareFactory/blob/f53d81fe77edbaf5c0221edecf3542b24777422d/reference/build-plan.md)):
   - A market watch per project, **run by Hermes**, covering "competitor changelogs, release notes and blogs, GitHub, Hacker News and Reddit to begin with. Sources that need a login or paid access come later."
   - Hermes writes a drop folder in a fixed format. The engine reads it and makes every GitHub call, so Hermes holds no GitHub token.
   - An active competitor list is a tracked file in the project repo (the factory's own list is [`reference/competitors.md`](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/competitors.md)).
   - Each week the engine opens one PR with a dated digest and list changes, and files ideas as **proposal issues**. "A proposal is never queued automatically."
   - "External text passes through a summariser with no tools before any agent that can act sees it."
2. **F8** uses the same tool-less summariser for monitoring alerts and other external intake.
3. The operating-model note: **"The market watch stays in Hermes. It is not in the merge path."** Scheduled runs and notifications are F2, also Hermes.
4. The README target architecture mentions "Social links, bug reports, customer feedback, and alerts" entering triage, with untrusted external content summarised by a tool-less model call. Under Planned Integrations it lists **Crawl4AI** for "Intake research" and says **"None of these is wired in yet."** ([README](https://github.com/harry738/HyperSoftwareFactory/blob/main/README.md))
5. A vendored **`research` skill** ([`.claude/skills/research/SKILL.md`](https://github.com/harry738/HyperSoftwareFactory/blob/main/.claude/skills/research/SKILL.md)) investigates a question against primary sources and writes a cited Markdown file via a background agent. That is ad-hoc research, not F4.
6. Open question 1 in the build plan is still unanswered: "What exactly does Hermes write to the drop folder, and how does it start `factory run` on a schedule?"
7. On [#42](https://github.com/harry738/HyperSoftwareFactory/pull/42) / v6.5, F4 and F8 move to **R6** (P2): "Tool-less summarisation of untrusted inputs, provenance, deduplication, approved proposals; no automatic queueing before policy permits."

So the component is **planned, not built**. That is a strength: the plan already keeps research off the merge path, forbids auto-queueing, and requires a tool-less summariser.

---

## 3. Current practice for that component

GitHub repository metadata (licence, last push, star counts) for third-party tools was fetched from the GitHub REST API on 25 November 2026, about 18:50 GMT (Europe/London). Star counts are a snapshot from that request, not a later re-check.

### Official APIs first, scraping only where a site allows it

F4's starting sources already have official or first-party access for most of the list:

| Source | Preferred access | Citation |
|---|---|---|
| GitHub | Official REST/GraphQL APIs (already used by the engine) | [GitHub REST docs](https://docs.github.com/en/rest) |
| Hacker News | Official Firebase API, URIs under `https://hacker-news.firebaseio.com/v0/`. The README says there is currently no rate limit, and clients should ignore unexpected fields. | [HackerNews/API README](https://raw.githubusercontent.com/HackerNews/API/master/README.md) |
| Reddit | Official Data API, subject to the Data API Terms (last revised 20 July 2026 on the page fetched for this review). Access requires compliance with developer documentation and rate limits. User content is owned by users; AI/ML training of user content is restricted. | [Data API Terms](https://redditinc.com/policies/data-api-terms), [Developer Platform help](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data) |
| X / Twitter | Official X API and Developer Policy. The Policy is the contract for API use. X Terms require access through published interfaces; this review cites the official Developer Policy page rather than restating unofficial commentaries. | [X Developer Policy](https://docs.x.com/developer-terms/policy), [X Terms](https://x.com/en/tos) |
| Changelogs, release notes, blogs | Official pages, RSS/Atom, or a licensed search/extract API. Honour `robots.txt`. | [RFC 9309](https://datatracker.ietf.org/doc/html/rfc9309) (Robots Exclusion Protocol) |

**Do not scrape X or Reddit instead of their APIs**, and **do not evade blocks, CAPTCHAs or bot walls**. That would conflict with the operator's rule against evading blocks aimed at the bot, with typical platform terms, and with the factory's own "fail closed / sourced claims" stance. If a source returns 403/429 or a robots disallow, stop, record the failure, and leave it for the operator.

**UK GDPR:** personal data that is publicly available is still personal data. The ICO says you need a lawful basis and, in general, must provide privacy information if you obtain personal data from publicly accessible sources such as social media. ([ICO: obtaining personal data from publicly accessible sources](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/the-right-to-be-informed/what-common-issues-might-come-up-in-practice/)) F4 should prefer product/company artefacts (changelogs, release notes, official blogs, repo releases) over scraping personal profiles, and should minimise or strip personal data in the drop folder.

This is not legal advice; it is a pointer to the published sources.

### Frameworks and libraries (for allowed web pages only)

The README already names Crawl4AI as a *planned* intake-research tool, unwired. These are the named options, verified from their own docs or GitHub metadata:

| Tool | What the official page says | Licence / maintenance (API snapshot) | Fit for F4 |
|---|---|---|---|
| [Crawl4AI](https://docs.crawl4ai.com/) | Open-source crawler that turns pages into LLM-ready Markdown; Playwright-driven; also a hosted API. Docs mention stealth modes and proxies. | Apache-2.0; `unclecode/crawl4ai` last pushed 23 November 2026, 06:00 GMT; 87,879 stars | Reasonable for **public, robots-allowed** changelog/blog pages, self-hosted, with stealth/proxy features left off. Already named in the README, not wired. |
| [Firecrawl](https://docs.firecrawl.dev/capabilities) | Scrape/search/extract API; JS rendering; can be self-hosted (core routes). Cloud-only features include login profiles and "stealth" proxy modes. | AGPL-3.0; `firecrawl/firecrawl` last pushed 25 November 2026, 18:48 GMT; 209,828 stars | Useful as a hosted extractor for public pages. AGPL matters if vendoring. Do not use login-profile or stealth modes to reach disallowed or blocked sites. Monitoring/change detection is a Cloud capability that could later support a weekly watch. |
| [Playwright](https://playwright.dev/) | Browser testing and automation for Chromium, Firefox and WebKit. | Apache-2.0; `microsoft/playwright` last pushed 25 November 2026, 18:25 GMT; 101,059 stars | Already in the factory's orbit (UI reviewers and Binley checks). Use for **app verification**, not social scraping. |
| [Scrapy](https://docs.scrapy.org/en/latest/topics/practices.html) | Mature Python crawling framework with item pipelines. New projects can obey `robots.txt` via `ROBOTSTXT_OBEY`. | BSD-3-Clause; `scrapy/scrapy` last pushed 25 November 2026, 17:15 GMT; 65,610 stars | Heavier than F4 needs. Its "avoiding getting banned" section includes techniques this review does **not** recommend adopting. |
| [Crawlee](https://crawlee.dev/docs/introduction/real-world-project) | Node.js/TypeScript crawling library with HTTP and Playwright crawlers, queues and storage. Its own intro tells you to ask whether the site has an API instead of scraping HTML. | Apache-2.0; `apify/crawlee` last pushed 25 November 2026, 18:05 GMT; 26,577 stars | Good queue/storage patterns, but the factory engine is Python-stdlib-first ([AGENTS.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/AGENTS.md)). Better as a lesson than as a new runtime inside `factory/`. |
| [browser-use](https://github.com/browser-use/browser-use) | "Open-source Python library for AI browser agents, plus Browser Use Cloud: stealth browsers and a hosted agent API" (GitHub description). | MIT; last pushed 24 November 2026, 22:48 GMT; 122,048 stars | Poor fit. An LLM driving a browser, especially with "stealth browsers", is the wrong shape for a weekly, policy-bound market watch and conflicts with "do not evade blocks." |

### Data pipeline patterns (match the plan, then tighten)

F4 already sketches the right skeleton. Worth locking in before any collector is written:

- **Queue and schedule in Hermes, not in the factory container.** E6.1's network allowlist is "package registries, GitHub and the model API only" ([build plan](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md)). Do not punch Reddit, crawl APIs or arbitrary blogs through that allowlist. Hermes (or another process outside the container) collects; the engine only reads a drop folder and talks to GitHub.
- **Fixed drop-folder schema** (still an open question in the plan): source URL, retrieved-at, accessor (API name or HTTP GET), HTTP status, robots decision, raw hash, stripped text, citation, and a personal-data flag. Deduping on URL+content hash.
- **Provenance and citations** on every digest claim, matching the operator's "no made-up claims" rule and the vendored `research` skill.
- **Tool-less summariser** already specified: untrusted text must not be handed to an agent that can write code or open issues until it has been summarised without tools.
- **No automatic queueing** already specified. The operator decides. The Dev council may later triage only after it has earned that power.
- **Storage:** drop folder plus the weekly PR and proposal issues. Do not quietly accumulate social-profile corpora.

### Research automation tools

| Tool | What it is | Licence / maintenance | Fit |
|---|---|---|---|
| [GPT Researcher](https://docs.gptr.dev/docs/gpt-researcher/search-engines) | Autonomous research agent; default retriever is Tavily; Exa and others are supported via `RETRIEVER`. | Apache-2.0; `assafelovic/gpt-researcher` last pushed 23 November 2026, 14:51 GMT; 30,906 stars | Possible later helper for writing the weekly digest **from already-collected, cited sources**. Do not let it browse arbitrary social sites unattended. |
| [STORM](https://github.com/stanford-oval/storm) | LLM system that researches a topic and writes a cited article (pre-writing then writing). | MIT; last pushed 30 September 2025, 19:07 BST; 31,952 stars | Interesting method, slower maintenance. Not a first install. |
| [Open Deep Research](https://github.com/langchain-ai/open_deep_research) | LangGraph research agent; Exa describes it as planning searches and producing a cited report, defaulting to Tavily. | MIT, but the GitHub API reported **`archived: true`** on 25 November 2026, last push 10 August 2026, 19:13 BST; 12,675 stars | Do not adopt an archived repo as a dependency. |
| [Exa](https://exa.ai/docs/search/deep-search) | Hosted search API with a Deep Search mode that iterates, inspects evidence and can return field-level citations. | Commercial API (docs only; not treated as an open-source install) | Good for web evidence with citations, if a later paid source is approved. "Sources that need a login or paid access come later" in F4. |
| [Tavily](https://docs.tavily.com/documentation/api-reference/endpoint/search) | Search and extract API used by several research agents; official docs describe Search, Extract, Crawl, Map and Research. | Commercial API | Same as Exa: a later, approved search layer, not a scrape of social logins. |
| Factory `research` skill | Already in the repo: primary sources, one cited Markdown file. | Vendored, pinned 19–21 November 2026 ([skills README](https://github.com/harry738/HyperSoftwareFactory/blob/main/.claude/skills/README.md)) | Use for one-off questions now. Do not stretch it into an unattended social crawler. |

### Lessons from similar projects

The factory's own [competitors.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/competitors.md) and [feature comparison](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/feature-comparison.md) already cover unattended coding systems (Symphony, OpenHands, Copilot cloud agent, Stripe Minions, and others). The lessons that matter for F4 are the ones the build plan already drew: keep the control loop in code; keep untrusted input out of the merge path; do not auto-queue external ideas; record evidence. Crawlee's own tutorial asks whether the site has an API before you scrape HTML ([Crawlee real-world project](https://crawlee.dev/docs/introduction/real-world-project)). That is the right question for Reddit, HN, GitHub and X.

---

## 4. Fold-in to the earlier PM-bot comparison

The earlier recommendation still holds: do **not** build a single combined dev+PM bot, and do **not** install MetaGPT, ChatDev or an autonomous commit harness. Use a PM seat that writes an approved cut, then the existing PR-only coding path.

For **research-driven roadmap work** (the F4 digest and proposal issues), the ready-made options that help are the *research and spec* tools, not a scraper and not a combined coder:

- **[PM bot](https://x.ai/bot/marketplace/bots/pm-bot)** (Ulysses Ng) is still the best Grok Bot fit for turning a weekly digest into a dated in/out cut and **stopping until the operator approves**. It refuses to start engineering before that. It is not itself a market-watch collector.
- **[Anthropic Product Management plugin](https://github.com/anthropics/knowledge-work-plugins/blob/main/product-management/README.md)** (`/competitive-brief`, `/roadmap-update`, `/synthesize-research`) is the strongest official skill pack for turning sourced notes into roadmap language. Use it on the digest, not as a crawler.
- **[GitHub Spec Kit](https://github.com/github/spec-kit/)** remains the right process layer if a proposal later becomes a factory job: specify, then plan, then implement as a PR.
- **GPT Researcher / Exa / Tavily** can help write a cited briefing from allowed sources. They should feed the drop folder or a draft digest, not open issues or merge.
- Community teaser bots such as [AI PM OS](https://x.ai/bot/9dtfHw4LHmwc5uBC-a9vj) are still a sample of a paid product and are not recommended as the collector.
- **Do not** hand F4 to a general coding bot (SWE, Engineering Lead, Lingxi's Engineer Bot) or to browser-use. Those are the delivery path, and only after the operator approves a proposal.

If a dedicated factory/research bot is created later, it should be a **Hermes-side watcher**: official APIs, drop folder only, no GitHub token, no merge, one business/project list at a time.

---

## 5. Top recommendations for the factory roadmap (proposals only)

Map onto existing plan IDs only. No new RM numbers.

1. **Do not build F4 until the engine track's open safety work is done.** Especially [#26](https://github.com/harry738/HyperSoftwareFactory/issues/26) (fail-closed `unattended_merge`) and E1.6. The build plan already says backpressure before forward pressure. [#42](https://github.com/harry738/HyperSoftwareFactory/pull/42) placing F4/F8 in **R6** is the right sequence, once that PR is rebased onto current main.
2. **Keep the market watch outside the factory container** (already F4/Hermes). Do not widen E6.1's allowlist for crawl or social hosts.
3. **Specify the drop-folder contract first** (answers open question 1): schema, dedupe, provenance, personal-data stripping, weekly PR format. Docs-only, before any collector.
4. **Start F4 with official APIs only:** GitHub, the official HN API, Reddit Data API if access is approved, official changelog/RSS feeds. Leave X until there is an approved API use case. Do not scrape social sites or evade blocks.
5. **If a page fetcher is needed for public blogs,** consider the already-named Crawl4AI (self-hosted, robots honoured, no stealth) or a later approved search API (Tavily/Exa/Firecrawl core scrape). Cite every claim.
6. **Reuse the tool-less summariser and "proposal issues, never auto-queued" rules as written.** The operator remains the only person who can turn a proposal into a factory job or a merge.
7. **Use the existing `research` skill** for one-off sourced questions now; do not treat it as the weekly market watch.

---

## 6. Dex Horthy: "12 Rules for a Software Factory That Doesn't Ship Slop"

### The talk, verified

- **Video title:** "12 Rules for a Software Factory That Doesn't Ship Slop — Dex Horthy, Factory" on the AI Engineer YouTube channel: [https://www.youtube.com/watch?v=-NFMsM2y0Vk](https://www.youtube.com/watch?v=-NFMsM2y0Vk) (page fetched for this review).
- **Conference session page**, with a different official title: "A software factory needs pressure in both directions", AI Engineer CODE 2026, 12 November 2026: [https://ai.engineer/code/2026/talks/dexter-horthy](https://ai.engineer/code/2026/talks/dexter-horthy).
- **Official machine transcript:** [https://ai.engineer/api/code/reading-download/transcripts/dexter-horthy.md](https://ai.engineer/api/code/reading-download/transcripts/dexter-horthy.md). The transcript itself says "Machine-generated transcript; recognition errors remain" and points the source recording at a different YouTube id (`y9JtCCZP2MQ`) than the published cut (`-NFMsM2y0Vk`). The wording below is taken from that official transcript, not from the pasted summary.
- In the talk, Horthy also calls the working title **"12 Factor Factories, which started as a joke title, but then everyone started calling it that."** He says he will "do 12 great practices for software factories" and that it used to be nine, "but we are at 12 now." ([official transcript](https://ai.engineer/api/code/reading-download/transcripts/dexter-horthy.md))
- He points people to the **[No AI Slop manifesto](https://slopmanifesto.com/)** (the transcript mis-hears the URL as "slotmanifesto.com"; the live site is slopmanifesto.com, fetched for this review).
- The factory README already lists "Dexter Horthy's talk on software factories" among its origins. ([README](https://github.com/harry738/HyperSoftwareFactory/blob/main/README.md))

**On listing "the 12 rules":** the official transcript only explicitly numbers one item ("Number two, I will call know your enemy"). It does not publish a clean numbered 1–12 slide list. This review therefore **does not invent a numbered twelve**. It maps the practices Horthy actually states, in talk order, after he announces the twelve, plus the review point he makes after introducing the manifesto.

### Mapping (main `72a982c` vs PR #6 `cccd09d`)

"#6" below means the snapshot at the merged head of [PR #6](https://github.com/harry738/HyperSoftwareFactory/pull/6). That branch is already on main; main has since added E3–E6 work, E2.5–E2.6, E5.4–E5.5 and plan v6.4. "Partial" means the idea is present but not fully enforced or not proven on a real project.

| Practice, as stated in the official transcript | Main (`72a982c`) | PR #6 (`cccd09d`) | Evidence |
|---|---|---|---|
| **Forward and back pressure.** "How do you start work automatically? And how do you make sure that whatever comes out and is touched by a human by the end, all the low-hanging stuff is already fixed." | **Partial.** Forward pressure from a `factory` label through intake → spec → build → PR is built. Incident-to-PR and other external signals (F8) are not. Back pressure (gate, reviewers, CI wait, budgets, always-stop paths) is built and stand-in tested; not yet proven on a real project (E1.6 open). | **Partial, earlier.** E1 run loop and E2 limits/log/feedback exist; always-stop scripts, read-only reviewers and container allowlist were still open on that plan. | [README workflow](https://github.com/harry738/HyperSoftwareFactory/blob/main/README.md), [build plan v6.4](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md), [v6.1 on #6](https://github.com/harry738/HyperSoftwareFactory/blob/cccd09d3/reference/build-plan.md) |
| **Know your enemy.** "Unattended models don't do a great job of maintaining and improving code base quality over time." Keep understanding of the system and the code. | **Partial.** CONTEXT.md and the evidence track exist; no autonomy level is earned; FullAuto is documented and unbuilt. The fail-open merge default (#26) undercuts this. | **Partial.** Same philosophy; fewer mechanical guards landed. | [CONTEXT.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/CONTEXT.md), [build plan evidence track](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md), [#26](https://github.com/harry738/HyperSoftwareFactory/issues/26) |
| **Plan before you build, by expected pain.** Plan more where change will be hard (he gives database schemas as an example, not button colour). | **Partial.** Every job has a spec stage; skills include `to-spec`, `grill-me`, `grill-with-docs` and `domain-modeling`. There is no in-repo `docs/adr/` or `specs/` convention on this public repo, and CONTEXT rule 3 (complexity gate) is "a target and is not built." | **Partial.** Spec stage exists; those later skills and docs were not the focus of #6. | [CONTEXT.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/CONTEXT.md), [skills README](https://github.com/harry738/HyperSoftwareFactory/blob/main/.claude/skills/README.md) |
| **Align visually.** Horthy's "Show Me" skill: HTML mockups, tables, charts instead of walls of text. | **Missing** as a factory requirement. UI/UX reviewers and a shared dev server exist, but there is no mandated visual plan artefact. | **Missing.** | [build plan E4](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md), [README](https://github.com/harry738/HyperSoftwareFactory/blob/main/README.md) |
| **Help agents test their work** with screenshots, browsers, videos, curl, or a real app build in the environment. | **Partial.** Project `checks.sh` is meant to be the back pressure (the Binley example includes a Playwright walkthrough). The **template** `factory/checks.sh` still exits 1 with "has no checks yet." UI reviewers can drive a browser. Holdout tests (F5) are unbuilt. E1.6 not run. | **Partial, weaker.** Gate exists; E4 read-only reviewers and E3.4 cache-off gate were still open. | [factory/checks.sh](https://github.com/harry738/HyperSoftwareFactory/blob/main/factory/checks.sh), [build plan F5](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md) |
| **Fight slop with lint rules.** He points to an "Anti-slop" ruleset, Factory's ESLint plugin, and Slop Code Bench language rules. | **Partial.** A vendored `deslop` skill exists and the skills README says to run `/deslop` before each PR, but it is a skill, not a CI/gate check. CONTEXT rule 3 (complexity +50% blocks for architecture review) is not built. The carried-over backlog still lists "complexity check, secret scan and dependency audit as examples in the template `checks.sh`." | **Missing** as enforcement. | [skills README](https://github.com/harry738/HyperSoftwareFactory/blob/main/.claude/skills/README.md), [CONTEXT.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/CONTEXT.md), [build plan carried-over table](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md) |
| **Slop is a tool in the right place.** Prototypes, side projects, and work behind a feature flag can be rougher; not every line must be perfect. "Slop is bad when it undermines our outcome." | **Partial.** A `prototype` skill is vendored ("throwaway build to answer a design question"). There is no factory rule that keeps prototypes out of production modules, and no feature-flag policy in the engine. | **Missing** as a factory rule. | [skills README](https://github.com/harry738/HyperSoftwareFactory/blob/main/.claude/skills/README.md) |
| **Give models a feature-flagging system** (he mentions PostHog, Statsig or LaunchDarkly) so they can try something and compare. | **Missing** in the factory engine and plan. | **Missing.** | No match in the build plan feature list on main or on #6. |
| **Compound over time: eval everything, learn from past sessions.** | **Partial.** Event log and usage log exist (E2.3). F3 (weekly Kaizen, learnings file) and A8 (engine-written learnings) are planned, not built. A `retro` skill exists for a person-led session retro. | **Partial.** Event log landed in #6; F3/A8 were already planned and still open. | [build plan E2.3, F3, A8](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md) |
| **Unify your forge.** Bring designs and decisions as close as possible to the code, instead of pasting answers through chat. | **Partial.** CONTEXT.md, AGENTS.md, per-project competitor list and learnings file are specified as protected paths in the project repo. Specs today live in job folders, not a durable `docs/adr` or `specs/` tree. | **Partial.** Same operating-model paragraph is already in v6.1. | [build plan operating model](https://github.com/harry738/HyperSoftwareFactory/blob/main/reference/build-plan.md), [CONTEXT.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/CONTEXT.md) |
| **You can't buy everything**, especially verification of *your* code. | **Aligned in intent.** The factory uses Claude Code as the engine but keeps project checks, path rules and policy in the private factory home, outside the builder's worktree. Verification of a real project still depends on that project's `checks.sh`, which the template leaves empty. | **Aligned in intent;** container isolation was still open. | [AGENTS.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/AGENTS.md), [factory/checks.sh](https://github.com/harry738/HyperSoftwareFactory/blob/main/factory/checks.sh) |
| **Human review still matters.** "Agent reviewers, linters, verifiers, they're very useful, but they are not sufficient." Review a subset depending on the stakes; outcomes matter more than PR counts or how many agents run in parallel. ([transcript](https://ai.engineer/api/code/reading-download/transcripts/dexter-horthy.md), [slopmanifesto.com](https://slopmanifesto.com/)) | **Mostly done in policy, with one dangerous hole.** Supervised mode stops every job for the operator; `unattended_merge` is false in the template; always-stop paths outrank the council. The missing-key fallback in `factory/bin/run` still defaults to `True` ([#26](https://github.com/harry738/HyperSoftwareFactory/issues/26)). FullAuto is opt-in and unbuilt. | **Same hole already present in spirit:** v6.1 and #6 put the template at false, while the unsafe fallback was the subject of the earlier review and remains open as #26 on main. | [factory/config.json](https://github.com/harry738/HyperSoftwareFactory/blob/main/factory/config.json), [CONTEXT.md](https://github.com/harry738/HyperSoftwareFactory/blob/main/CONTEXT.md), [#46](https://github.com/harry738/HyperSoftwareFactory/pull/46), [#26](https://github.com/harry738/HyperSoftwareFactory/issues/26) |

### Proposed PR order (nothing opened or pushed)

The operator is the only merger. Each item would be a PR, opened only after he asks for it.

1. **Fail closed on merge** — implement [#26](https://github.com/harry738/HyperSoftwareFactory/issues/26): change `CONFIG.get("unattended_merge", True)` to default `False` in `factory/bin/run` and `factory/bin/job`, with a test that a missing key never merges. Smallest, highest-value change.
2. **Close or retarget stale docs issues**, then rebase [#42](https://github.com/harry738/HyperSoftwareFactory/pull/42) onto current main so v6.5 status rows match v6.4, if he still wants that release framing. Docs only.
3. **AGENTS.md / contributing checklist** — one short section stating: where specs and decisions live; that `/deslop` plus the project's `checks.sh` must pass before a PR is ready for him; which paths (`protected_paths`, `sensitive_paths`, `human-merge`) always need his sign-off. This is Horthy's "suggested next step" and is already half-true in CONTEXT.md.
4. **Template back pressure** — add optional examples to `factory/checks.sh` for lint, types, tests, and a complexity or anti-slop check, fulfilling CONTEXT rule 3 and the carried-over backlog item. Do not enable unattended merge as part of this.
5. **Drop-folder contract for F4** — docs-only PR answering open question 1 (schema, provenance, dedupe, official-API sources, no auto-queue). Implementation of the watcher waits until R6 / after E1.6.

No social-scraping PR should come before items 1 and 5.

---

## 7. What was not done

No commits, branches, pull requests or issues were created. No one was contacted. No bot was imported. This file is a local research note only.
