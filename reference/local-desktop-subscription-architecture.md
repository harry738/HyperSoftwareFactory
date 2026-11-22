# Local-first desktop and subscription architecture

**Decision:** The first factory runtime is **Claude Code in Claude Desktop (Code tab)** on the operator's PC. Use the user's Claude Ultra subscription for Claude Code, and a separate signed-in OpenAI Codex installation for ChatGPT-plan-backed coding work. This is the preferred *initial* workflow, not a proposed cloud-hosted multi-tenant service.

**Current capability vs target:**
- **Working:** the existing `/factory run` skill orchestrates Claude Code subagents and local Python/git/GitHub CLI scripts. It runs inside a target project into which `factory/` and `.claude/` have been copied. Runtime state is held in that project's gitignored `factory/jobs/` folder.
- **Not yet wired:** Codex execution by the factory; model selection across Claude/Codex, subscription quota reporting, automatic failover, and a factory-wide multi-project scheduler.
- **Not required:** Anthropic/OpenAI API keys, rented servers, Kubernetes, databases, or usage-based cloud infrastructure for the initial supervised workflow.

## Operator workflow on Windows

1. Install Claude Desktop, open its **Code** tab, and sign in with Claude Ultra. Alternatively, open the target project's checkout in the supported Claude Code CLI/IDE. Ensure `/factory` and its agents are installed in that project.
2. Authenticate Claude Code using the **Claude subscription** login. Check `/status` and confirm the active login/plan. Avoid `ANTHROPIC_API_KEY` in the process environment: Claude Code prefers that API key and can incur *separate API charges*.
3. Install Python, Git and GitHub CLI. Sign in to `gh` and configure Git's credential helper locally. Run the project-specific `factory/checks.sh` until its deterministic tests pass; the template deliberately fails until configured.
4. Run `python scripts/factory-doctor.py --subscription-only` as a non-networked preflight. This flags environment API keys and missing tools; it cannot verify a plan or quota. Open Claude Code from the project and invoke `/factory run <issue-number>`. Start with `concurrency: 1`, then inspect the proposed PR and its evidence. The default `allow_unattended: false` sends approved work to a human for GitHub merge.
5. Install official Codex locally and run `codex` once to log in with your ChatGPT subscription. Use it as a **manual second-opinion reviewer** initially. A future provider adapter may automate supported Codex CLI/SDK/app-server interactions after an integration and security review.
6. If the operator uses WSL, keep each project, runtime, Git credential store and executable path consistent on that side of the Windows/WSL boundary. The existing Windows `factory/bin/proc.py` fixes require platform-specific regression testing.

## Identity, billing and plan limits

| Engine | Supported sign-in path | Initial function | Charging/usage boundary |
|---|---|---|---|
| Claude Code | Claude Desktop Code tab or Claude Code signed in directly to Claude Ultra | Main orchestrator, agent implementation and review | Subject to Claude plan allocation, weekly/session limits and provider policy |
| OpenAI Codex | Official Codex CLI/app signed in with ChatGPT | Additional interactive implementation/review | Uses eligible ChatGPT Codex allowance subject to rate, plan and credit rules |
| Claude/API and OpenAI/API | Explicit separate API credentials, only if the operator opts in | Future optional headless service runners | Separately metered/charged; never selected silently |

**Do not copy, parse, export or proxy** another application's session, OAuth token or credential. Subscription credentials are not general-purpose API keys. Use only the official sign-in and integration interfaces provided for the runtime. Claude Ultra's consumer subscription is designed for ordinary use of native Claude products, including Claude Code. Do not assume it authorises a third-party proxy, shared account, or unlimited unattended agent farm.

The official OpenAI Codex CLI accepts ChatGPT sign-in. OpenAI also documents **Sign in with ChatGPT** for eligible open-source and local apps; if the factory ever becomes its own app, that supported integration can be evaluated separately, subject to availability, scopes, limits and preview constraints. It is **not implemented** in this repository.

Plan allowance is not a fixed dollar budget. `factory/bin/job` calculates an **API-equivalent cost estimate** using local Claude Code transcripts and manually configured prices. That number is a benchmark only; it is **not** money charged to the subscription, a receipt, a balance, or a measure of remaining quota.

When plan quota is reached, the agent should stop after a safe checkpoint and signal `needs-human` or wait for an explicit operator resume. Do not automatically purchase credits, silently switch to API credentials or log in using another person's account. Account-level plan-usage APIs may not be available for all providers; use local job counts, wall-clock limits and the official provider's usage indicator as initial controls.

## Local-first architecture

```text
Claude Desktop (Code tab) or Claude Code CLI   [Claude Ultra sign-in]
                |
        /factory interactive skill
                |
       Local factory/bin/job state machine
                |
    GitHub issues -> spec -> local worktrees -> checks
                |                         |
           Claude subagents      Optional human-invoked Codex
                |                 [ChatGPT sign-in, distinct CLI]
         Commit-bound reviewers
                |
        Policy gate -> evidence -> PR
                |
      HUMAN MERGE (initial default)
```

The control flow, workspace, logs, Git state and local quality checks run on the operator's PC. Model inference normally uses provider-hosted services; *local-first does not mean offline or private inference*. The factory is a tool invoked by the operator, not a background cloud platform.

## Future provider adapter contract (planned, not implemented)

Define a shared, versioned `AgentTask` and `AgentResult` envelope with:
- task ID, project, role, workspace, base/head SHA, requirement snapshots, expected output format and allowed file permissions;
- selected engine (`claude-code` or `codex`), operator-approved sign-in mode and capability discovery;
- execution ID, timestamps, exit code, model/tool identity if supplied, usage when available, evidence references, structured errors and whether human interaction is required.

Keep the provider-specific adapter at the *invocation boundary*; Python state machine, test runner, risk policy and PR merging remain shared. Preserve permission prompts and product quota limits. Never use subscription sign-in to create a private API proxy.

**Initial routing:** Claude Code remains the complete engine because it is the existing working pipeline. Codex can be invoked by the operator for independent reviews. Do not change `factory/config.json` to claim an automated Codex adapter is active before it is built and verified.

## Acceptance criteria for subscription-first MVP

1. On a Windows machine, sign in to Claude Desktop Code with a Claude subscription and complete one project issue to a human-reviewable PR without an Anthropic API key.
2. Independently sign in to Codex with a ChatGPT account, run a review interactively, and attach its finding to the PR. No OpenAI API key is required for that official Codex usage.
3. Verify that setting `ANTHROPIC_API_KEY` does **not** pass the documented subscription-only preflight; require user confirmation of a paid-API mode before proceeding.
4. A provider usage-limit error pauses safely and never incurs fallback paid API costs without explicit opt-in.
5. One project can be used without starting cloud infrastructure, databases, background schedulers or a separate factory server.
6. The repo's integration tests prove that stale reviews, protected workflow additions and non-low-risk changes cannot self-merge.
7. Actual provider usage and rate-limit exhaustion are never inferred from API-equivalent dollar estimates alone.

## Official sources

- [Claude Code with Pro, Max or Ultra](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-max-or-ultra-plan)
- [Start Claude Code from Claude Desktop](https://support.claude.com/en/articles/14552382-your-first-day-in-claude-code)
- [Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- [Codex as an embeddable platform](https://developers.openai.com/blog/codex-as-a-platform)
- [Sign in with ChatGPT for open-source apps](https://developers.openai.com/cookbook/articles/sign-in-with-chatgpt)
