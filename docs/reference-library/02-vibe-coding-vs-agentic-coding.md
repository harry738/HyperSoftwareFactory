# 02 Grace Ableidinger — Vibe Coding vs. Agentic Coding

Local reference-library notes only. Not pushed to GitHub.

## Source

- **Title:** Vibe Coding vs. Agentic Coding: Which Should You Use?
- **Speaker:** Grace Ableidinger
- **Channel:** IBM Technology ([@IBMTechnology](https://www.youtube.com/@IBMTechnology))
- **Published:** 23 November 2026 (YouTube `upload_date` 20261123, from yt-dlp metadata fetched 25 November 2026)
- **Length:** 8 minutes 36 seconds (516s)
- **URL:** https://www.youtube.com/watch?v=h4tHDFCPmQE (also https://youtu.be/h4tHDFCPmQE)
- **Official chapters** (from the video description and yt-dlp chapter list):
  - 00:00 — Define Vibe Coding vs. Agentic Coding
  - 01:23 — Understand How Vibe Coding Works
  - 01:51 — Use Vibe Coding for Rapid Prototypes
  - 02:12 — Identify Risks in AI-Generated Code
  - 02:41 — Build with Agentic Coding Workflows
  - 03:38 — Compare Vibe and Agentic Coding Side by Side
  - 04:46 — Give AI Coding Agents Focused Context
  - 06:04 — Secure Agentic Coding with Guardrails
  - 07:17 — Choose the Right AI Coding Approach
- **Transcript:** Official English captions exist on the video. A direct timedtext download was rate-limited (HTTP 429) on 25 November 2026. The wording below is taken from the YouTube watch-page transcript fetched the same day from the URL above. The description says "AI was used in the creation of the transcript and metadata for this video." A few caption phrases look like recognition errors (for example "Five coding" for "vibe coding", "mash" for "match"). Quotes are given as fetched; garbled words are noted, not silently rewritten.
- **Added to this library:** 25 November 2026 (Europe/London)

## Summary

Ableidinger distinguishes two AI coding workflows. **Vibe coding** is a prompt–generate–iterate loop that favours speed and is well suited to prototypes, experiments, demos and visualising ideas. The risk is that this code can reach production with little review or understanding, leaving duplicate functions, odd file organisation and convoluted fixes. **Agentic coding** treats the agent as a tool used with a developer: understand the code, plan, execute, test and validate, with more human judgement at the understand and validate steps. Larger work can be split among subagents with scoped permissions (a test-running agent should not have GitHub access). Models have a finite attention budget, so focused context beats dumping everything in. As agents gain reach, the needed controls are testing, human sign-off on irreversible or costly decisions, observability, rollback and guardrails. The question is not which workflow is better, but how much structure and autonomy the task needs. Stay the person who can explain the code.

## Key learnings and principles (mapped to HyperSoftwareFactory)

Repo state used for the mapping, from the 25 November 2026 read-only review: main tip [`72a982c`](https://github.com/harry738/HyperSoftwareFactory/commit/72a982c7c9103b5f53a85f22db0c5de6000c6c8f), build plan **v6.4**, fail-closed merge default still open as [#26](https://github.com/harry738/HyperSoftwareFactory/issues/26), F4 market research planned and not built. This is a local mapping only; nothing was written to the repository.

### 1. Vibe coding is for speed and prototypes, not unreviewed production

> "Vibe coding is generating software primarily through prompting and AI-generated code. The emphasis is on speed." (01:23)

> "Vibe coding is great for rapid prototyping, experimentation, demos and visualizing ideas." (01:51)

> "Because the focus is on speed and ease, there's often little to no reviewing or even understanding the code." … "duplicate functions, oddly organized files, and convoluted fixes to a simple bug." (02:12)

**Factory status: partial.** The factory's default path is already the opposite of unreviewed vibe coding: labelled issues go through intake, a spec, a build, a gate and reviewers, then a PR. A vendored `prototype` skill exists for throwaway builds that answer a design question. There is no feature-flag or sandbox rule that keeps rough spikes out of production modules, and the template `factory/checks.sh` still has no project checks. This lines up with the earlier Horthy finding that prototypes are only partly separated from production.

### 2. Agentic work is understand → plan → execute → test → validate, with humans at both ends

> "Agentic coding is where AI works hand in hand with a developer. This is beyond just generating code. A coding agent should be used as a tool." (02:41)

> "You want to understand the code, then make a plan, execute that plan, test it, and then validate." "Some of these steps could be developer or agent led, but the point is there's more human brainpower involved in agentic coding. Especially here at the understanding step and here at the validation step." (03:38)

**Factory status: partial (design done, not proven on a real project).** This is the factory's intended loop: a script owns orchestration; specialist agents write and review; every supervised job stops for the operator. E1.1–E1.5 and most of E2–E6 are built and stand-in tested. **E1.6** (first real-project job) is still open, so the loop has not yet been proven on a live project. The empty template checks file also weakens the "test" and "validate" steps until a project fills them in.

### 3. Match the workflow to the risk of the task

> "Which is better? That's not really the right question. Different tasks need different levels of structure and autonomy." (07:17)

> For "a quick bug fix", "testing out a new design or renaming variables", vibe coding "might be the right call, but for pushing net new features to production, touching any databases or payment systems, or doing large refactorings, you might want an agentic loop with you behind the wheel." (07:17; caption writes "Five coding" for vibe coding)

**Factory status: partial.** Routing already varies model and reviewers by risk (`low`/`medium`/`high`, `risk_paths`, `protected_paths`, `sensitive_paths`, surface reviewers for UI and security). High-stakes paths can be labelled `human-merge`. What is missing is an explicit written rule that vibe/prototype work stays off schemas, payment and security boundaries, and an AGENTS.md checklist of which files always need the operator's sign-off. That is still a suggested docs PR, not on main.

### 4. Give agents focused context; use scoped subagents

> "model attention is a finite budget. And more of this information doesn't always produce a better answer." "The more context a model receives, the harder it can be for it to pick out what's important." (04:46)

> "Larger tasks can be broken into smaller pieces and delegated to subagents. These are optimized for certain tasks and have scoped permissions. For example, some agent that runs your tests wouldn't have access to your GitHub." (02:41)

> "A subagent can go down a rabbit hole exploring some niche corner of your code base, and then hand back a quick summary. That way, your main agent stays focused on planning and orchestration." (04:46)

**Factory status: mostly done in the engine, with F4 still to follow the same rule.** Specialist stage agents, read-only reviewers, and a hook that blocks hand merges already exist. Agents are not meant to hold GitHub tokens; `factory run` owns GitHub calls. Planned F4 research stays in Hermes, outside the merge-path container, and Hermes is specified to hold no GitHub token. There is no first-class "context budget" rule in AGENTS.md or the build plan telling jobs what *not* to dump into a prompt. Worth adding when the checklist PR is written.

### 5. As agents gain reach, add testing, human sign-off, observability, rollback and guardrails

> "The more powerful your agent, the more control you need." (06:04)

> "This can look like testing, so you know that your changes worked. Governance, so humans signs off on any irreversible or potentially costly decisions. Observability, so you can see exactly what your agent did and why. Rollback, so any mistakes can be undone and guardrails so your agent stays on track and operates according to predefined rules." (06:04)

**Factory status: partial, with one P0 hole.** Guardrails and observability are largely present: budgets, always-stop paths, an event log (E2.3), worktrees and PRs (rollback is "don't merge" or revert), a no-hand-merge hook, and a container/network allowlist (E6, built but not yet run signed-in). Governance is intended to be supervised-by-default: the template sets `unattended_merge` to false. **[#26](https://github.com/harry738/HyperSoftwareFactory/issues/26) is still open:** `factory/bin/run` still uses `CONFIG.get("unattended_merge", True)`, so a missing key fails open. That contradicts this principle and should stay the first proposed PR. Testing is only as strong as each project's `checks.sh`.

### 6. Stay the person who can explain the code

> "If you're worried about vibe coding, don't stop using AI. Just mash the appropriate task to the approach and stay the person who can explain the code." (07:17; caption writes "mash", almost certainly "match")

**Factory status: partial.** Policy already keeps the operator as the only merger, FullAuto unbuilt, and every supervised job stopping for the operator. There is not yet an AGENTS.md / contributing checklist that says which decisions and files he must personally understand before merging, or a learnings file (plan F3) that compounds review lessons. That remains a cheap docs follow-up, after #26.

## Roadmap implications (proposals only; not a principles.md)

Do not add these to the repo until the operator says yes. Suggested order is unchanged: fix [#26](https://github.com/harry738/HyperSoftwareFactory/issues/26) first; then an AGENTS.md checklist (including risk-matched workflows, focused context, and files that need his sign-off); then anti-slop / complexity checks in the template `checks.sh`; then a docs-only F4 drop-folder contract. This video especially supports keeping prototypes out of production paths, scoping subagent permissions (no GitHub token for research or test runners), and treating human sign-off on costly actions as a hard gate.

Collated principles across all library videos will be written later in `principles.md`, once the remaining videos are in.
