# Plannotator — Plan & Code Review Gate

**Status:** ADOPT — install and wire into Software Factory
**Source:** plannotator.ai · backnotprop/plannotator (15.1K⭐, MIT/Apache 2.0)

## What it provides

- **Plan review gate** — intercepts agent plans before execution. Human reviews with inline annotations. Structured feedback back to agent.
- **Code review gate** — full diff viewer with inline annotations for agent-written code. Feedback flows back to agent with one click.
- **10 agent integrations** — Claude Code, Codex, OpenCode, Copilot CLI, Gemini CLI, Pi, Amp, Droid, Kiro
- **Editor integrations** — VS Code, Zed, Obsidian, Bear, Octarine

## Factory integration

| Gate | Before | After |
|---|---|---|
| Gate 2 — Architecture Review | Manual spec review in terminal | Plannotator plan review — inline annotations, structured feedback to agent |
| Gate 3 — Verification | Manual code review of diff | Plannotator code review — diff annotations, feedback back to agent |
| Gate 4 — Feedback | Manual log review | Version history with diffs between revisions |

## Data

- 235 releases (v0.29.4 latest)
- 12,897 commits, 234 contributors
- Runs locally — data never leaves machine
- Obsidian integration — plans saved with frontmatter and tags
- Approval gates and automation hooks available