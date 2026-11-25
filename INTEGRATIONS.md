# Integration matrix

Build with agents. Verify with evidence.

Status distinguishes code from operational validation. The [build plan](reference/build-plan.md) is authoritative.

| Integration | Role | Status |
|---|---|---|
| Claude Code | Headless intake, spec, builder and reviewer sessions | Current engine; central flow tested with stand-ins |
| GitHub / GitHub CLI | Issues, PRs, CI, branch protection | Implemented; central real-project run open |
| Python / Git / bash | Deterministic control and worktrees | Implemented; Linux/WSL target |
| Docker Desktop | Container deployment and network allowlist | Image and proxy verified locally; signed-in run and hard separation open |
| Local dashboard | Project boards and PR status | Implemented; container web console planned |
| Hermes | Scheduled runs, notifications and market watch | Planned |
| Context7 | Version-specific documentation via MCP | Planned |
| Modern Web Guidance | Build and verification guidance | Planned |
| Crawl4AI | Research intake | Planned |
| Multi-model Dev council | Shadow decisions and measured agreement | Planned; not alternative builder runtimes |
| Prismor | Candidate runtime-security evaluation | Research only; not integrated |

No support for Codex or Gemini as alternate builders is claimed. The council is a separate planned capability. See [reference architecture](reference/software-factory-reference-architecture.md) and [competitor analysis](reference/feature-comparison.md).

## Candidate assessment: Prismor

Evaluate Linux/WSL and container compatibility, Claude Code hook coverage, enforcement bypass resistance, least privilege, egress, secrets, MCP controls, tamper-evident evidence, latency, cost and licensing. Start with an isolated test environment and observe-only evaluation. Do not substitute a third-party hook for factory gates or branch protection. Adoption requires a separate architecture decision and operator approval.

[Upstream Prismor](https://github.com/PrismorSec/prismor)
