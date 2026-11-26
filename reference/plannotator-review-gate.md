# Plannotator — Plan & Code Review Gate for AI Agents

**Source:** plannotator.ai · backnotprop/plannotator
**Status:** ADOPT — install and wire into Software Factory
**License:** MIT / Apache 2.0 (dual) | **Stars:** 15.1K | **Version:** v0.29.4 (Nov 2026)
**Language:** TypeScript (92%) | **Commits:** 12,897 | **Contributors:** 234

---

## What it is

An open-source, locally-running plan and code review tool for AI coding agents. Intercepts the agent's proposed plan before execution, presents it in a proper review UI, collects inline annotations, and sends structured feedback back to the agent.

Supports Claude Code, Codex, OpenCode, Copilot CLI, Gemini CLI, Amp, Droid, Kiro CLI, and Pi. Integrates with VS Code, Zed, Obsidian, Bear, and Octarine.

---

## Relevance to HyperSoftwareFactory

### Maps directly to our pipeline

| Factory Stage | Plannotator Feature |
|---|---|
| Gate 2 — Architecture Review | Plan review — annotate agent's proposed plan before any code is written |
| Gate 3 — Verification | Code review — full diff viewer with inline annotations |
| Build feedback loop | Structured feedback sent directly back to agent (no copy-paste) |
| Human-in-the-loop | Approval gates and automation hooks |
| Documentation | Obsidian vault integration — plans saved with frontmatter and tags |
| Audit trail | Version history with diffs between revisions |
| Security | Runs locally — data never leaves the machine |

### What it replaces

We described a "review UI" in our reference architecture but hadn't built one. Plannotator provides:

- Annoation surface for plans (before code)
- Annotation surface for code diffs (after build)
- Structured feedback → agent revises based on exact annotations
- Version history across plan and code reviews

### Pipeline integration

```
Agent proposes plan
    ↓
Plannotator intercepts (plan mode hook)
    ↓
Council/human reviews with inline annotations
    ↓
APPROVE → Agent starts coding
  or
DENY + FEEDBACK → Agent revises and resubmits
    ↓
Agent writes code → PR created
    ↓
Plannotator code review — full diff annotations
    ↓
Council/human reviews
    ↓
APPROVE → Merge → Deploy
  or
DENY + FEEDBACK → Agent fixes
```

---

## Key Data

| Metric | Value |
|---|---|
| GitHub Stars | 15,100 |
| Releases | 235 (v0.29.4 latest) |
| Contributors | 234 |
| Commits | 12,897 |
| License | MIT OR Apache-2.0 |
| Primary Language | TypeScript (92%) |
| Release cadence | Multiple per week (very active) |
| Supported agents | Claude Code, Codex, OpenCode, Copilot CLI, Gemini, Pi, Amp, Droid, Kiro |
| Supported editors | VS Code, Zed, Obsidian, Bear, Octarine |

---

## Installation

```bash
curl -fsSL https://plannotator.ai/install.sh | bash
```

Then install the Claude Code marketplace plugin:
```bash
claude plugin marketplace update plannotator
plannotator --version
```

---

## Decision

| Vote | Rationale |
|---|---|
| **ADOPT** ✅ | Directly fills our "review UI" gap in Gates 2 and 3. Mature project (235 releases), active development. Runs locally, MIT license. Integrates with Obsidian (our vault system). Sends structured feedback back to agents — no manual re-entry. |