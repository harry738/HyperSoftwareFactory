# 15 Prismor — self-hosted runtime control plane for agent tool calls

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Repository:** https://github.com/PrismorSec/prismor
- **Homepage / docs:** https://prismor.dev
- **GitHub API snapshot, 25 November 2026:** Apache-2.0, language **Python**, **675** stars, **72** forks, created 20 February 2026, last push 25 November 2026, 16:22 UTC (16:22 UK). Topics include `agent-control-plane`, `prompt-injection`, `supply-chain`, `claude-code`, `owasp`.
- **Description (API):** a self-hosted runtime control plane: observe, HITL-approve, or block rogue tool calls (secret leaks, prompt injection, supply chain) in a local dashboard; agent-agnostic.
- **Formerly** Immunity Agent. The CLI alias `immunity` is deprecated.
- **Files read (read-only GitHub / raw; nothing was starred, forked, cloned for install, or `pip install`'d):** README, `pyproject.toml`, `prismor/__init__.py` version notes, and `AGENT_INTEGRATIONS.md` (updated 22 October 2026).
- **Added:** 25 November 2026.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** Security reviewer; E6 (sandbox, egress, supply-chain install checks); F4 untrusted intake (prompt injection, secret leak, MCP tools); LLM spec (optional LiteLLM extra; Claude Code is a listed integration; Factory Droid is marked roadmap). Observe-mode first, if ever evaluated. **Do not install in this pass.**

**Scores:** Relevance H (closest off-the-shelf enforcement hook for tool-call policy). Actionability M (useful later; not a now-install). Novelty H relative to the current empty `checks.sh` and planned E6 allowlist.

**Dedupe:** Complements entry 03 (layered, cheapest-first guardrails) and entry 14 (Agent Baseline: policy authorizes, infrastructure enforces). Prismor is a concrete hook/proxy/dashboard, not a competing factory runner. Overlaps Sandcastle/E6 on Seatbelt. Optional `litellm` extra overlaps the LLM-spec transport choice but is only used here for a semantic-injection detector, not as the factory's model router.

## What the project is

Prismor is a **self-hosted runtime control plane** that sits in front of an agent’s **tool calls**. Before a call runs, Prismor can **observe**, require **human approval**, or **block** it, according to YAML policy. The pitch is to catch secret leaks, prompt injection, and supply-chain-risky installs without sending telemetry to a vendor SaaS (the dashboard and session store are local). It is **agent-agnostic**: it plugs in via hooks, an SDK, or an LLM/MCP proxy, rather than replacing the coding harness.

The README quick start is `pip install prismor` then `prismor setup`. **That was not run.**

## Main features (from README and docs; not installed or exercised)

- **Policy engine** on YAML rules: allow, warn, or block. Docs claim on the order of **81** built-in rules; that figure was not re-counted here.
- **Observe vs enforce.** Observe is the documented default — log what would have been blocked, without breaking the agent. Enforce actually blocks. This matters: any later trial should start in observe mode.
- **Supply-chain checks** at install time (packages the agent tries to add).
- **Network isolation / egress** controls.
- **Optional macOS Seatbelt sandbox.**
- **Skill and MCP scanners**, plus an **MCP gateway** with per-tool human-in-the-loop approval.
- **Prompt guardrails** (including an optional semantic-injection path).
- **LLM proxy** for agents that cannot be hooked directly.
- **Secret sweep / cloak and leak guards.**
- **Local dashboard** (web and terminal) over a session store.
- **Integrations** listed for many coding agents, including **Claude Code**, Codex, Cursor, OpenHands, and Goose. **Factory Droid** is marked yellow / roadmap in `AGENT_INTEGRATIONS.md` (22 October 2026). Support claims were not verified by running the hooks.

## How it is built

**Language and packaging.** Python, **requires Python >= 3.8**. Built with **hatchling**. The PyPI package name is `prismor`; version **1.64.0** was printed in packaging metadata at the time of this read. A `package.json` in the repo is for skill/metadata packaging, **not** the runtime.

**Core dependencies** (from `pyproject.toml`):

- `pyyaml>=6.0`
- `cryptography>=41`
- `tomli` on Python 3.10 and older

**Optional extras** include:

- `litellm` — semantic prompt-injection detection
- Presidio / spaCy — PII
- A long list of framework extras for the supported coding agents and MCP stacks

**Architecture** (from the README mermaid / capabilities section):

1. **Entry** — hooks, adapters, or the proxy intercept a tool call before execution.
2. **Policy** — detect + evaluate YAML policy, optionally against a signed advisory feed; result is allow, warn, or block (or HITL approve).
3. **Evidence** — session store in **SQLite + JSONL**; web and terminal dashboards; a **tamper-evident hash chain** with **Ed25519** signatures; optional learning from those traces.
4. **Optional org plane** — a self-hosted control plane for signed remote policy, telemetry, and an org dashboard.

No Prismor process was started, and no hook was installed, in this review.

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Conceptual match to entry 03, E6 isolation/allowlist, F4 untrusted-intake checks, and the security reviewer. Claude Code is already the default harness, and Prismor lists a Claude Code integration. |
| **Incorporate (proposal only)** | The operator may later **evaluate Prismor in observe mode** around Claude Code, on a disposable machine, and compare blocks to the existing allowlist and checks. Do not turn on enforce until that trial is reviewed. MCP-tool HITL is relevant if MCP is enabled. Skill/MCP scanners could later inform F4. |
| **Inspiration** | Tamper-evident session logs as a complement to the event log. Signed advisory feeds. Seatbelt as one more sandbox option (also in Sandcastle). |
| **Do not incorporate now** | `pip install prismor` or `prismor setup` on the factory machine. Making Prismor a required dependency of `factory run`. Enabling enforce mode, org-plane telemetry, or paid extras without the operator's yes. Treating Factory Droid support as shipped. |
