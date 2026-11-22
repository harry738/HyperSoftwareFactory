# Upstream open-source capability assessment

**Date:** 2026-11-22  
**Target:** HyperSoftwareFactory at `main` + the pending assurance-hardening PR  
**Operating constraint:** local Claude Desktop / Claude Code with the operator's Claude Ultra subscription; optional local Codex signed in through an eligible ChatGPT subscription. No implicit API billing, credential extraction, hosted control plane or unattended agent farm.

## Executive recommendation

Keep the local `factory/bin/job` state machine, worktree management, and verified PR lifecycle. **Do not swap orchestration platforms because of framework popularity.** Add independently useful engineering capabilities first. Each new upstream dependency must improve a measured outcome, pass a supply-chain/licence review and be pinned to a tested version.

The current repository already contains `/factory`, intake/spec/builder/review agents, `to-spec`, `to-tickets`, TDD and code-review skills, a deterministic gate, a dashboard and a pilot. It has no automated Codex adapter, no container isolation, and no enforced scanner suite yet. The current PR is adding fail-closed review and merge controls; it is *not* a full security sandbox.

## Assessment matrix

| Upstream | Documented capability | Existing overlap | Decision | Specific next step |
|---|---|---|---|---|
| [Agent Skills](https://github.com/agentskills/agentskills) | Open `SKILL.md` convention, parser/specification and reference validator | ~27 copied/curated Claude skills | **Adopt early** | Validate every included skill using pinned `skills-ref`; record source SHA, licence, permissions and compatibility; define canonical vendor-neutral skill catalogue |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Local Git/working-directory secret detection with pre-commit/CI integrations | No deterministic committed-secret detector | **Adopt early** | Pin CLI; scan new commits and checked-out files; block leaked dummy credentials in an adversarial fixture |
| [Trivy](https://github.com/aquasecurity/trivy) | Local filesystem, repository and container vulnerability/configuration/secret scans, SBOM | No dependency or configuration vulnerability scan | **Adopt early** | Pin CLI and database policy; use `trivy fs --scanners vuln,misconfig --exit-code 1` with configured severities; separate scanner errors from findings |
| [Semgrep CE](https://github.com/semgrep/semgrep) | Static analysis and source-pattern rules across many languages; local CLI/CI | LLM code reviewer only, limited static policy | **Adopt early** | Pin CE CLI and vetted local rules; run on changed code and test seeded anti-patterns. CE does not provide full cross-file security analysis |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | Spec-driven flows, structured planning, task breakdown, bug workflows, agent integrations, templates/presets/catalogs | Existing `to-spec`, `to-tickets`, spec-writer and factory stages | **Pilot** | Compare one isolated issue using Spec Kit vs existing spec workflow; score criterion retention and test traceability. Adopt templates selectively; avoid competing specs/sources of truth |
| [Conftest](https://github.com/open-policy-agent/conftest) | Declarative Rego policy tests against JSON/YAML and other configuration | Python merge/risk checks and `protected_paths` | **Pilot** | Express merge risk floor, evidence contract and protected-file rules as read-only policy inputs; compare against Python gate on adversarial fixtures. Python remains enforcement until parity established |
| [Agent Client Protocol](https://github.com/agentclientprotocol/agent-client-protocol) | Editor/client ↔ coding-agent protocol with session lifecycle, permissions and JSON-RPC; stable v1 as reviewed | Claude Code native agent tool; no Codex/Cursor adapter | **Pilot** | Prototype an ACP adapter only if supported official binaries and account sign-in permit it. Preserve permission prompts and cancellation. ACP is not an execution sandbox, subscription proxy or complete job orchestration layer |
| [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) | Python/TypeScript/REST SDK, tools, workspaces and conversations; agent server | Existing Python orchestration and native subscription-backed Claude Code | **Defer** | Study tool/workspace design as reference; evaluate runtime replacement only if native provider adapters or isolation are demonstrably inadequate. SDK examples use an LLM API key: subscription compatibility must not be assumed |
| [Temporal](https://github.com/temporalio/temporal) | Durable, retryable workflow execution and local development server | GitHub/filesystem-backed job state machine | **Defer** | Revisit after measured multi-host resume/retry failures or unattended long-running jobs; avoid server/database overhead in the first desktop build |
| [Renovate](https://github.com/renovatebot/renovate) | Automated dependency-update pull requests; cloud GitHub app or self-hosted runner | No automated dependency maintenance | **Defer for factory runtime** | When dependency-heavy projects are onboarded, pilot the GitHub app or scheduled CLI on one repo with lockfile-only PRs and mandatory checks. No reason to self-host immediately |

### Why these choices

**Adopt early** means local deterministic tooling that can run under an ordinary shell and CI without using any Claude or OpenAI model quota. Pin versions, make scanning opt-in per-project at first, and fail closed once false positives and installation behaviour are understood. Gitleaks and Trivy overlap on secrets: use Gitleaks for repo history/commit coverage and Trivy primarily for vulnerabilities/misconfigurations. Do not double-count their findings.

**Pilot** means the value may be high, but it overlaps existing implementation or introduces an extra process. Spec Kit is strongest for clarifying requirements and preserving traceability; it should enhance the existing spec contract, not replace `/factory`. Conftest scales when a growing policy catalogue makes Python checks hard to manage. ACP is potentially useful for multiple coding engines, but it is primarily *client-to-agent* interoperability; a stable job-result schema, isolated CLI process and official vendor auth remain necessary.

**Defer** means unnecessary operational complexity in the initial desktop mode. OpenHands uses its own agent tooling and LLM integration rather than serving as a transparent bridge to an existing Claude Desktop subscription. Temporal needs a service/worker model. Renovate is useful maintenance automation, but it does not solve the immediate factory's assurance gaps.

## Recommended sequencing and proof

**A. Harden independent quality, without more AI model calls.**
1. Pin Gitleaks and Trivy locally. Use severity thresholds, exit codes and an offline/DB-refresh strategy appropriate to the project.
2. Add a pinned Semgrep CE rule set for the repo's Python/TypeScript stack, with a clear policy for findings vs tool errors.
3. Run all three in `checks.sh` and in GitHub Actions, with mandatory seeded tests (secret, vulnerable lockfile, unsafe code).
4. Validate the existing skills registry against Agent Skills specification; keep upstream SHA and licence provenance.

*Exit:* all seeded bad fixtures fail and normal code remains green on Windows and Linux; no API key is needed to perform scanning.

**B. Improve requirement quality before scaling autonomy.**
1. Pilot Spec Kit's specify/plan/tasks and its consistency checks on one existing issue without altering the existing factory pipeline.
2. Compare original issue criteria with `spec.md` and the generated tests. Human-approval rules remain independent of model claims.
3. Pilot Conftest against structured policy input: risk-tier, changed paths, checks, reviewer evidence and approval.
4. Keep GitHub branch rulesets and a human merge as the ultimate release authority.

*Exit:* original criteria cannot silently disappear; policy denies a high-risk or stale-verdict fixture with a machine-checkable reason.

**C. Add multiple model engines only after a provider-neutral contract.**
1. Define `AgentTask`/`AgentResult` with role, worktree, SHA, evidence, timeout, status and auth mode.
2. Implement a local Codex CLI adapter using only official supported ChatGPT sign-in, with no credentials copied into the factory. Start with independent review.
3. Investigate ACP v1 support/adapter licensing and capabilities as an experiment rather than a hard dependency.
4. Compare Claude vs Codex on the same benchmark tasks and review outcomes, not self-reported success.

*Exit:* the same task can run in two supported engines with reproducible evidence and no surprise API billing.

## Security and licensing acceptance criteria

- No tool is fetched/executed at an unpinned `latest` inside privileged CI or a sensitive development workspace without a reviewed versioning policy.
- Review licence obligations for binary distribution, vendored source, modified skills and mixed MIT/GPLv3 factory components.
- Only approved skills and scanner rule bundles are allowed to run. A new skill cannot grant broader filesystem/network permissions by instruction alone.
- Treat a scanner's failure to run as `INCONCLUSIVE` or a gate failure, never a pass.
- The locally running factory must not access browser session cookies or repackage consumer subscriptions as an API; use supported Claude Code/Codex sign-in only.
- Preserve a software bill of materials and provenance record when publishing releases.

## Useful upstream entry points

- Spec Kit [README](https://github.com/github/spec-kit) and [integration guides](https://github.github.com/spec-kit/integrations/index.html)
- Agent Skills [specification](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx) and [reference validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- OpenHands [SDK README](https://github.com/OpenHands/software-agent-sdk)
- ACP [README](https://github.com/agentclientprotocol/agent-client-protocol) and [protocol overview](https://agentclientprotocol.com)
- Temporal [README](https://github.com/temporalio/temporal)
- Conftest [docs](https://github.com/open-policy-agent/conftest/blob/master/docs/index.md)
- Semgrep [Community Edition](https://github.com/semgrep/semgrep)
- Trivy [filesystem target](https://trivy.dev/docs/latest/target/filesystem/)
- Gitleaks [README](https://github.com/gitleaks/gitleaks)
- Renovate [README](https://github.com/renovatebot/renovate)

This assessment does **not** install any third-party tools or enable unattended merges. Update the decision log after the pilots, not by assumption.
