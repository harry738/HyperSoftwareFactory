# Greptile + CodeRabbit — Replication Plan

**Status:** DESIGN — add to Software Factory verification layer
**Date:** 2026-11-26

---

## What they do

### Greptile
- **Graph-based codebase indexing** — builds a semantic graph of every function, class, file, and dependency across the entire repo
- **Context-aware PR reviews** — understands how changes affect distant parts of the system
- **Natural language codebase queries** — "How does auth work?" returns file/function references
- **Confidence scores** (0-5) on every review comment
- **Self-updating knowledge base** — auto-generated, real-time, editable docs of the codebase, accessible via MCP
- **TREX runtime validation** (beta) — runs PR branch in a sandbox to catch runtime bugs
- **Learning from team feedback** — reads 👍/👎 reactions and replies to learn coding standards
- **Custom rules** in plain English, `.greptile/rules`
- **Sequence diagrams** + PR summaries
- **Fix in your coding agent** — one-click send of issue context to Claude Code, Cursor, Codex
- **Swarm of review agents** — parallel agents review changes
- **Self-hosted** deployment with your own LLM

### CodeRabbit
- AI PR review with inline comments and suggested fixes
- PR summary generation
- Monorepo-aware
- Learns from reviewer feedback
- Integration with GitHub, GitLab, Bitbucket

---

## What we already have vs what's missing

| Capability | We have | Gap |
|---|---|---|
| Code review agent | ✅ Matt Pocock /code-review, code-review skill | — |
| PR summary generation | 🔶 Partial (from council verdicts) | No structured auto-summary |
| Custom rules / lint | ✅ Anti-slop lint, Semgrep, TypeScript rules | — |
| Security scanning | ✅ TruffleHog, Trail of Bits, SkillSpector | — |
| Runtime validation | ✅ TestSprite (web), Mobile Agent Testers | — |
| Agent feedback loop | ✅ Plannotator (plan + code review annotation) | — |
| **Code graph indexing** | ❌ None | **Build** — core gap |
| **Self-updating knowledge base** | ❌ None | **Build** — core gap |
| **Cross-file impact analysis** | ❌ None | **Build** — core gap |
| **Confidence scoring** | ❌ None | **Build** — core gap |
| **Learning from PR feedback** | ❌ None | **Build** — core gap |
| **Codebase Q&A (NL)** | ❌ None | **Build** — core gap |
| **Sequence diagram generation** | ❌ None | **Build** — nice-to-have |
| **Swarm parallel reviewers** | 🔶 Planned (5-verifier pool) | Needs orchestration |

---

## Replication approach

### Phase 1 — Code graph indexing (highest ROI)

Greptile's core is the code graph. We need one that works locally in our factory's container.

**Options:**

| Approach | Effort | What it gives |
|---|---|---|
| **Ast-grep + tree-sitter** | 2 days | Syntax-aware AST indexing, function call graph, dependency resolution. Fast (Rust), local, no API costs. | 
| **Understand (SciTools)** | Drop-in | Commercial-grade code graph. Can query via CLI. ~$1K/license. |
| **OpenGrok** | 1 day | Open-source code search + cross-reference engine. Java, heavier. |
| **Custom with ts-morph (TypeScript)** | 3 days | Full TypeScript AST + import resolution. Only works for TS repos. |

**Recommended:** `ast-grep` (sg) + tree-sitter. Rust-native, MIT license, works with TypeScript, Python, Rust, Go. Build a factory job that:
1. On PR, runs `sg` over the whole repo to produce a dependency graph
2. Feeds the graph into the review agent as context
3. The reviewer can answer: "What calls this function? What imports this module?"

### Phase 2 — Self-updating knowledge base

After every merge, auto-generate a codebase summary.

**Implementation:**
1. On merge, run a Claude Code agent that reads the full repo and writes `docs/knowledge-base/` 
2. Documents: architecture overview, module responsibilities, key functions
3. Each doc has frontmatter with tags and last-updated date
4. Review agents load relevant docs via MCP for context

### Phase 3 — Confidence scoring

Assign 0-5 scores to each review verdict:

| Score | Meaning |
|---|---|
| 5 | Verified at runtime (TestSprite/Mobile Agent Testers pass) |
| 4 | Evidence trail complete (tests written + pass, lint clean, security scan clear) |
| 3 | All static checks pass (lint, types, tests exist) |
| 2 | Review completed but missing evidence |
| 1 | Review incomplete — verifier pool not fully exercised |
| 0 | Not reviewed |

### Phase 4 — Learning from PR feedback

Track 👍/👎 reactions on review comments (Plannotator supports this). After N reviews:
1. Analyse which review comments were accepted vs rejected
2. Update custom rules to encode approved patterns
3. Flag patterns that were consistently rejected

### Phase 5 — Codebase Q&A

Expose the code graph + knowledge base via a simple MCP server. Factory agents can ask:
- "Find all functions that call `getPrice()`"
- "What's the authentication flow?"
- "Which files in the trading module import from analytics?"

---

## Build vs buy

| Tool | Build | Buy | Verdict |
|---|---|---|---|
| Code graph indexing | ast-grep + tree-sitter (MIT, free) | Greptile ($15/dev/mo) | **Build** — ast-grep is mature, our need is simple |
| Code review | Already built (Matt Pocock + custom) | Greptile / CodeRabbit | **Already have** |
| Knowledge base | Auto-generated via Claude Code | Greptile Knowledge Base | **Build** — custom to our factory |
| PR summaries | Claude Code + prompt | — | **Build** — trivial |
| Runtime validation | TestSprite + Mobile Agent Testers | — | **Already have** |
| Feedback learning | Track reactions → update rules | Greptile Learning | **Build** — medium effort |

**Bottom line:** We already have 70% of CodeRabbit's capability. Greptile's **code graph** is the one piece worth building.

---

## Priority for HyperSoftwareFactory

| Item | Effort | Why |
|---|---|---|
| ast-grep code graph indexing | 2 days | Unlocks cross-file impact analysis + codebase Q&A |
| Self-updating knowledge base | 1 day | Gives reviewers full repo context without re-scanning |
| Confidence scoring | 4h | Standardises verification quality reporting |
| Feedback learning | 3 days | Makes review agents smarter over time |
| Codebase Q&A via MCP | 1 day | Lets agents query the codebase in natural language |