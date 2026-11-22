# Skills in this repo

27 skills. `factory` comes with the software factory (see AGENTS.md). 25 are copied from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, see `LICENSE-mattpocock-skills`).

- **Pinned commit:** `abeeaf95660ba9e8b7c753eb38f441ca707a8823` (plugin v1.3.2), copied 19 Nov 2026.
- **`triage` added 20 Nov 2026** from the same pinned commit, so `/setup-matt-pocock-skills` creates the issue labels that `to-spec` and `to-tickets` use.
- **`grill-me` and `grilling` added 20 Nov 2026** from the same pinned commit, for the small-feature process in `docs/engineering-guidance.md`. `grill-me` delegates to `grilling`.
- **11 more added 21 Nov 2026** from the same pinned commit (upstream `main` was still at it): `grill-with-docs`, `domain-modeling`, `wayfinder`, `research`, `pr`, `retro`, `ask-matt`, `to-questionnaire`, `writing-for-agents`, and two from upstream's `in-progress/` folder, `software-factory` and `setup-ts-deep-modules`. Vetted: Markdown only plus one dependency-cruiser config, no scripts. Left out on purpose: prose-writing, exercise and Husky skills, and `git-guardrails-claude-code` (it would block the software factory's pushes).
- **Changes from upstream:** none to the skill text. The `agents/openai.yaml` files were left out because they are not used by Claude Code.
- **`deslop` added 20 Nov 2026** from [cursor/plugins](https://github.com/cursor/plugins) `cursor-team-kit/skills/deslop` at commit `0b46ec399d55f2829e88822998f53b84944837d3` (MIT, (c) Cursor, see `LICENSE-cursor-team-kit`). Unchanged. One Markdown file, no scripts.
- **Not installed as a plugin** so the version stays fixed. To update, re-vet the newer commit, then replace the folders.

| Skill | Invoked by | Purpose |
|---|---|---|
| `setup-matt-pocock-skills` | You | One-time setup of issue tracker, labels and doc layout |
| `triage` | You | Move issues through triage states and write agent-ready briefs |
| `grill-me` | You | Interview you to settle a plan's open decisions |
| `grilling` | Claude | The interview loop behind `grill-me` |
| `handoff` | You | Condense a conversation for another session |
| `to-spec` | You | Turn a conversation into a spec in the issue tracker |
| `to-tickets` | You | Split a spec into tickets with blocking links |
| `implement` | You | Build one ticket with TDD and a review |
| `implement-spec` | You | Build a whole spec with parallel subagents |
| `tdd` | Claude | Red-green-refactor, one slice at a time |
| `code-review` | Claude | Review the diff against standards and the spec |
| `codebase-design` | Claude | Module design guidance, called by `tdd` |
| `prototype` | Claude | Throwaway build to answer a design question |
| `diagnosing-bugs` | Claude | Structured loop for hard bugs |
| `deslop` | You or Claude | Strip AI padding from the branch diff before review |
| `factory` | You | Run the software factory on `factory` issues (from the factory clone; GPLv3, see `factory/LICENSE`) |
| `grill-with-docs` | You | Grill a plan and write the glossary and ADRs as decisions settle |
| `domain-modeling` | Claude | Keep `GLOSSARY.md` and ADRs sharp, called by `grill-with-docs` |
| `wayfinder` | You | Plan work too big for one session as decision tickets on the tracker |
| `research` | You | Research a question from primary sources into a Markdown file |
| `pr` | Claude | Write a pull request body |
| `retro` | You | Retrospective on a coding session |
| `ask-matt` | You | Which skill or flow fits this situation |
| `to-questionnaire` | You | Turn an open decision into a questionnaire for someone else |
| `writing-for-agents` | Claude | Rules for writing skills, CLAUDE.md and agent docs |
| `software-factory` | You | Shared language for designing a software factory (upstream marks it in progress) |
| `setup-ts-deep-modules` | You | dependency-cruiser rules so each package is a deep module (in progress upstream) |

Build chain: `/handoff` → `/to-spec` → `/to-tickets` → `/implement` (one ticket first) → `/implement-spec`. Run `/deslop` before each pull request.

Some skill text mentions upstream skills that are not copied here. Those mentions are optional paths, not required steps.

To remove: delete this folder, and remove the "Agent skills" block from `CLAUDE.md` and the `docs/agents/` files (written by hand on 20 Nov 2026, following `/setup-matt-pocock-skills`; that skill does not need running again unless the issue tracker changes).
