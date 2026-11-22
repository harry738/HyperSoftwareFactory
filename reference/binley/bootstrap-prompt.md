# Factory bootstrap prompt (plan P1-07 and P1-08)

Paste everything under the line into a new chat opened on the main project folder (`E:\Documents\Claude\Projects\BinleyBuildingSociety`). This is the one hands-on session. After it, work flows through the factory (plan §6A, "Autopilot").

---

Install the software factory on `main` so it can build this repo's tickets without me prompting each one. This is plan features P1-07 and P1-08, route H: I am in the session, and you stop for my review before the PR is merged.

## Read first
- `docs/plans/2026-11-21-ai-first-programme.md`: section 6 (factory operating model) and section 6A (build model, "Pilot result", "Autopilot").
- `CLAUDE.md` and `GLOSSARY.md`.
- The pilot report: `E:\Documents\Claude\Projects\Binley-factory\PILOT-REPORT.md`.
- The factory's own skill: `E:\Documents\Claude\Projects\Binley-factory\.claude\skills\factory\SKILL.md`.

## What exists
- A working pilot install is in the clone `E:\Documents\Claude\Projects\Binley-factory`, on branch `factory-pilot`. Its working tree has every Windows patch, each marked `# binley:`, including two local commits that were never pushed (the cost-matching fix and the gate's Git Bash fix). Copy from that working tree, not from `origin/factory-pilot`.
- The pilot took issue #23 to an approved PR in one round (38 minutes, about $4.45). The factory could not merge by itself.
- This machine is Windows 11 with Git Bash. `python3` does not exist here; `python` does. A bare `bash` from Python or PowerShell is WSL's, which cannot read `E:/` paths.
- Labels `factory`, `factory:needs-info`, `factory:needs-human` and `human-merge` already exist on GitHub.

## Do this, on a branch `factory-bootstrap` cut from `main`

1. **Copy the factory in.** From the clone's working tree: `.claude/agents/*.md` (8 files), `.claude/skills/factory/SKILL.md`, `factory/bin/job`, `factory/bin/gate`, `factory/bin/route`, `factory/checks.sh`, `factory/config.json`, `factory/dashboard.html`, `factory/LICENSE`. Also bring over the `.gitattributes` lines (LF for `factory/**`, `*.sh`, `.claude/agents/*.md`), the two `.gitignore` lines (`/factory/jobs/`, `/.worktrees/`), the `.worktrees` ignores in `eslint.config.mjs` and `tsconfig.json`, and the "Working in this repo" and "Software factory" sections of `AGENTS.md`. Do not copy the branch finder feature (`src/app/branches`, `src/lib/branches*`, `src/components/BranchFinder.tsx`): it was pilot data, not canon.

2. **Configure it for `main`.** In `factory/config.json`: `base_branch` is `main`, `concurrency` is 1, `merge_method` is `merge`. `protected_paths`: `factory/checks.sh`, `factory/config.json`, `factory/bin/*`, `e2e/walkthrough.e2e.ts`, `CLAUDE.md`, `docs/project-brief.md`, `GLOSSARY.md`, `.github/workflows/*`. Keep `intake`, `spec-writer` and `approver` on Fable and `builder` on Opus. The Fable 5.2 price in the price map is a copy of 5.1 and is unverified: leave it and say so in your report.

3. **Make the checks complete.** `factory/checks.sh` runs `npm ci`, lint, typecheck, unit tests and build today. Add the Monday walkthrough (`npm run test:e2e`) once its port is configurable: make `playwright.config.ts` and the `demo` script read a `PORT` environment variable (default 3210), and have `checks.sh` pass a port that cannot clash with a running demo or another job. Add `gitleaks detect --no-banner` only if `gitleaks` is installed; if it is not, tell me and do not install it yourself.

4. **Apply the pilot's nine fixes.** Each one needs a way to show it works.
   1. **The factory can merge.** Add permission rules to `.claude/settings.json` so `factory/bin/job merge <job>` runs without a prompt. Keep the existing deny on an agent typing `gh pr merge` directly.
   2. **Git never asks for a sign-in.** Git calls made by the scripts must fail fast instead of opening a dialog (`GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never`). Document the repo-local credential helper (`!gh auth git-credential`) in `AGENTS.md` for every clone the factory runs in.
   3. **Reviewers have a browser.** `reviewer-ux` and `reviewer-ui` open the page with the repo's Playwright on the job's port. A reviewer that could not open the page must not return PASS: it says why, and the job goes to `needs-human` when the cause is tooling.
   4. **No `npm ci` clash.** One lock per worktree around `checks.sh`, so the builder's own run and its Stop hook's run never install at the same time.
   5. **The Windows job lock waits.** It gives up after about 10 seconds today. Make it wait as the Linux lock does.
   6. **Stopping a script kills its children.** A stopped script must not leave processes holding the job lock.
   7. **One dev server per job.** Next allows one `next dev` per folder. Start one server for both UI reviewers and stop it by port when the review ends.
   8. **`job advance` can be re-run.** It must not post the intake comment on the issue twice.
   9. **A narrowed criterion escalates.** If the spec drops or weakens an acceptance criterion from the issue, the approver must ESCALATE. Add this to `approver.md`, beside the existing `human-merge` rule and path list. Update that path list for `main`'s files.

5. **Frontier labeller (P1-08).** Add `factory/bin/frontier`: for every open issue labeled `ready-for-agent` and not yet `factory`, read its blockers from GitHub's issue dependencies API (`gh api repos/harry738/Binley/issues/<n>/dependencies/blocked_by`). If none is open, add the `factory` label. It prints what it released. Add one line to the factory skill so every `/factory run` starts with it.

6. **Verify, and show me the output.**
   - `bash factory/checks.sh` exits 0 on the branch.
   - `factory/bin/job queue` and `factory/bin/frontier` run without error from Git Bash and from PowerShell.
   - `python -m json.tool factory/config.json` succeeds.
   - Each file in `.claude/agents/` has only the frontmatter keys `name`, `description`, `tools`, `model`, and `hooks` on the builder.
   - `git check-ignore factory/jobs/x .worktrees/x` prints both paths.
   - A unit test or a scripted check for fixes 5, 6 and 8.

7. **Draft three trial tickets (P1-18) and show them to me before filing.** Use the issue template in plan §6. Do not label them `factory`.
   - One ordinary route F ticket: small, with a screen, no money or rules.
   - One that the factory should refuse or escalate: a request that breaks a project rule in `CLAUDE.md`. It passes the trial only if it is not merged.
   - One route G ticket with a security surface (for example a change in `src/lib/redaction.ts`), labeled `human-merge`. It passes only if the security reviewer runs and the PR is handed to me.

8. **Open a PR to `main` and stop.** Run `/deslop` first. Write the PR body with what changed, how each of the nine fixes was verified, and anything you could not verify. Do not merge it.

## Limits
- Do not run `/factory run` in this session and do not label any issue `factory`. A session in an app worktree cannot load the factory's agents; the factory runs from the clone.
- Do not touch the `factory-pilot` branch or the clone's files, apart from reading them.
- Do not install software on this machine. If something is missing, tell me.
- Synthetic data only. The "Fictional organisation – demo only" label stays on every screen.

## After I merge the PR
Tell me these next steps; do not do them:
1. In the clone: `git fetch`, switch to `main`, pull. Open a new chat on the clone folder and confirm `intake` shows as an agent type and `factory` as a skill.
2. From that chat, run the three trial tickets one at a time (label one `ready-for-agent`, run `/factory run`, check the result by hand).
3. If the trials pass: the monorepo move (P1-03), then the planner session for Phase 1 and the scheduled `/factory run` (P1-19).

## Done means
The PR is open, every check in step 6 has output in your report, the three trial tickets are drafted and shown to me, and you have listed what you could not verify.
