# Factory pilot report: issue #23 (branch finder), job `001-pilot-branch-finder-page`

**Final outcome: `merged`.** PR #24 was merged into `factory-pilot` at 22:24:44 UTC (merge commit `707d6c1`), 55 minutes after the start. The operator approved the merge in the parent session, which re-ran the merge gate from this clone with the fixed gate script (PASS, 298s), merged with `gh pr merge 24 --merge`, and ran `factory/bin/job queue` to record the job as `merged`. So the factory's own `job merge` command never completed a merge in this pilot: the last step was done by hand. I verified the result: the PR is MERGED, `job summary` shows `merged`, the worktree is gone, the `factory:needs-human` label is off, and `src/app/branches/` and `src/lib/branches.ts` are on `origin/factory-pilot`. Issue #23 is still open, because GitHub only closes issues on merges into the default branch.

The rest of this section is the state before that merge, kept for the record.

**Earlier outcome: `needs-human`, not merged.** The job went intake → spec → build → gate → review → approve in one round with every verdict PASS. The final step, `factory/bin/job merge`, was refused for the orchestrator by Claude Code's auto-mode permission classifier. The operator then ran it from PowerShell at 22:15 UTC and the merge gate failed in 0 seconds, so the factory moved the job to `needs-human`. The failure is a Windows fault in the gate script, not in the feature (see "The merge attempt" below). PR #24 is open, marked ready, and unchanged at the commit that passed the round-1 gate.

## The merge attempt (added after the first version of this report)
- **What happened.** From PowerShell, `bash` on the PATH is WSL's `C:\Windows\System32\bash.exe`, which cannot read `E:/` paths. The gate ran `checks.sh` with it and got `No such file or directory`, exit 127 in 0s. The factory then did what it should for a failed merge gate: marked PR #24 ready, posted "needs a human" on it, and added `factory:needs-human` to issue #23.
- **Whose fault.** Mine. The PowerShell command in the first version of this report was not tested from PowerShell. The existing `# binley:` patch only picked the right bash when the script was started from Git Bash.
- **Fix.** `factory/bin/gate` now finds Git Bash from git's own install folder instead of the PATH. Tested under both a Git Bash PATH and a PowerShell-like PATH. Committed locally as `fd6951d`, not pushed.
- **What was not affected.** The branch: the sync with `factory-pilot` was a no-op (the base has not moved), so the PR head is still `160d007`, the exact commit that passed the round-1 gate and all three reviews.
- **Ways out of `needs-human`** (I have not taken either; it is the operator's call):
  1. Merge PR #24 by hand on GitHub. The next `factory/bin/job queue` records the job as `merged` and removes the `factory:needs-human` label. This is safe because the head commit already passed the gate.
  2. Give feedback with `factory/bin/job feedback 23`, which starts a new build round and runs the whole pipeline again, including the merge with the fixed gate. About 30 more minutes and a few dollars.

Run date: 21 November 2026, all times UTC. Run from `<factory clone>` on `factory-pilot`. All eight factory agent types and the `factory` skill loaded in this clone.

## Outcome
| | |
|---|---|
| Final job stage | `merged` (via `needs-human`: the first merge gate failed on a Windows fault, then the PR was merged by hand) |
| PR | #24, in a private repo, merged 22:24:44 UTC, base `factory-pilot`, merge commit `707d6c1` |
| Merged into `factory-pilot` | Yes, by hand with `gh pr merge` after a passing merge gate, not by `factory/bin/job merge` |
| Issue #23 | Open (not auto-closed: `factory-pilot` is not the default branch), label `factory`, two intake comments (one is a duplicate, see Problems) |

## Timeline
Start 21:29:26, approver finished 22:07:26: **38 minutes to an approved PR**. Merge not run.

| Stage | Start–end | Time | Notes |
|---|---|---|---|
| Queue, job create, header fix | 21:29:26–21:31:15 | 1m 49s | Includes the cost-matching fix |
| Intake | 21:31:15–21:32:14 | 59s | |
| Route and advance to spec | 21:32:21–21:36:26 | 4m 05s | About 4 minutes lost to a hung Git sign-in prompt |
| Spec | 21:36:30–21:40:24 | 3m 54s | |
| Build round 1 | 21:40:37–21:57:40 | 17m 03s | Includes two failed `checks.sh` runs inside the builder |
| Gate round 1 | 21:58:03–22:03:32 | 5m 29s | `checks.sh` took 327s (it took about 2 minutes when run alone earlier) |
| Reviews (parallel) | 22:03:59–22:05:22 | 1m 23s | code 57s, ux 14s plus a 6s resume, ui 83s |
| Approve | 22:05:38–22:07:20 | 1m 42s | |
| Merge, first try | 22:07:4x | not run | Blocked by the permission classifier |
| Merge, by hand | 22:15:47–22:15:53 | 6s | Gate failed in 0s (WSL bash), job moved to `needs-human` |
| Merge gate re-run and merge | to 22:24:44 | about 5 min | Run by the parent session: gate PASS in 298s, then `gh pr merge 24 --merge` |
| Job recorded as merged | 22:27:43 | | `factory/bin/job queue` |

## Rounds
One build round.

| Round | Gate | code (Haiku) | ux (Sonnet) | ui (Haiku) | Approver |
|---|---|---|---|---|---|
| 1 | PASS (commit `160d007`, 236 tests, no protected path changed) | PASS | PASS | PASS | APPROVE |

No reviewer asked for a change. Their non-blocking notes: the postcode round-trip test only checks the first branch; the disabled button's text is faint at 50% opacity; no demo bar tab is highlighted on `/branches`; the demo bar overflows at 375px (existing code).

Not exercised by this pilot: a gate failure, a CHANGES round, resuming the builder, the security reviewer, an escalation, and the merge.

## Intake
- Decision ACCEPT, risk low, surfaces `ui`, RESCOPED no. Routed reviewers: code (Haiku), ux (Sonnet), ui (Haiku).
- Intake dropped no criterion. It added one reading: postcode search matches with or without the space.
- The spec writer, not intake, narrowed criterion 6. "No horizontal scroll" became "`main` does not overflow", because the existing demo bar is wider than 375px and the issue forbids touching it. The spec also added a "Showing N of 34 branches" status line and one-line edits to `README.md` and `AGENTS.md`. The approver recorded all of this and treated the demo bar as a follow-up.

## Cost
```
job                           issue  stage    round  pr   cost   time
001-pilot-branch-finder-page  #23    approve  1      #24  $4.45  40m
total $4.45 (API-equivalent, factory agents only)
```

Per agent, computed from the job's subagent transcripts with the same formula as `job summary`:

| Agent | Model | Cost | Output tokens |
|---|---|---|---|
| intake | claude-fable-5-2 | $0.47 | 3,909 |
| spec-writer | claude-fable-5-2 | $1.91 | 22,216 |
| builder | claude-opus-5-5 | $1.02 | 20,937 |
| reviewer-code | claude-haiku-5-5 | $0.01 | 10,117 |
| reviewer-ux | claude-sonnet-5-5 | $0.12 | 1,900 |
| reviewer-ui | claude-haiku-5-5 | $0.01 | 7,853 |
| approver | claude-fable-5-2 | $0.90 | 6,270 |

Caveats: the figure uses the prices in `factory/config.json`, which I did not check against a price list. It excludes the orchestrator session (this one), which is not a factory agent. The three Fable agents are 74% of the cost; the spec alone cost more than the build.

## Human minutes
About two minutes: the operator ran the merge command once by hand. Nothing else needed a person up to approval. Three points where a person was or is needed:
1. **Merge (still open).** The permission classifier refused `factory/bin/job merge` for the orchestrator. The operator ran it; it failed on the gate's bash lookup, and the job now waits on the operator in `needs-human`.
2. **Git sign-in.** Git Credential Manager opened a sign-in dialog on the desktop when the factory ran `git fetch`. I worked around it without a person (see Problems), at a cost of about 4 minutes.
3. **Process listing.** The classifier refused a command that lists process command lines while I was diagnosing the hang. I used start times instead.

## Problems
| # | Problem | Windows-specific | Fix or workaround |
|---|---|---|---|
| 1 | Cost came out as $0: `job` matched the job folder with backslashes, but prompts use forward slashes | Yes | One-line fix, `factory/bin/job` line 279, marked `# binley:`. Committed locally as `832d300` on `factory-pilot`, not pushed (worktrees don't need it) |
| 2 | `job advance … spec` hung for 4 minutes: `git fetch` triggered a Git Credential Manager sign-in dialog, invisible to the script | Mostly | Stopped it, killed its 7 leftover processes, and set this clone's git to use the signed-in `gh` CLI (`credential.helper = !gh auth git-credential`, repo-local config, no secret stored). A fresh clone will need the same |
| 3 | Re-running the advance posted the intake comment on issue #23 a second time. `advance` posts the comment before the fetch, so it is not safe to re-run | No | Left as is |
| 4 | Stopping a hung script on Windows leaves its child processes alive and holding the job lock | Yes | Killed by PID after confirming start times |
| 5 | The builder's first two `checks.sh` runs failed with `npm ci` EPERM/ENOTEMPTY: its own run and the Stop hook's gate run installed into the same `node_modules` at once | Yes (file locking) | The builder re-ran once, cleanly. No code change |
| 6 | `agent-browser` is not installed. The builder and UI reviewer fell back to the repo's Playwright. The UX reviewer did not drive the page at all | No | None. The UX "review" was a 14-second read of the diff |
| 7 | The UX reviewer returned PASS without writing `review-ux.md`. The factory kept it as pending, which is the right behaviour | No | Resumed the reviewer once; it wrote the file |
| 8 | The UI reviewer reported its dev server stopped. It was still listening on 5112 | Partly | Killed it after using it for my own checks |
| 9 | Next 16 allows one `next dev` per folder. A second server in the same worktree is refused whatever the port | No | Not hit by the agents this time, only because the UX reviewer never started a server |
| 10 | The Agent tool in this app has no `name` parameter, so the builder can't be named `builder-<id>` as the skill says | No | Would resume by agent id. Not exercised (one round) |
| 11 | The gate took 327s against about 120s standalone | Unclear | None |
| 12 | The gate picked WSL's bash when started from PowerShell, failed in 0s and sent an approved job to `needs-human` | Yes | `factory/bin/gate` now finds Git Bash from git's install folder, marked `# binley:`. Committed locally as `fd6951d`, not pushed. The job itself was not moved back |

**What would break at `concurrency` 3**
- **Job lock (from reading the code, not tested).** On Windows the lock gives up after about 10 seconds instead of waiting. `job merge` holds its job's lock through the whole gate run (5 minutes or more), and `job queue` and `job summary` lock every job. So a queue or summary call during another job's merge would crash.
- **Dev servers.** Ports differ per job, so jobs don't clash with each other. Inside a job, the ux and ui reviewers run in parallel in one worktree and Next refuses the second server (problem 9). A leftover server (problem 8) blocks the next round and, on Windows, blocks removing the worktree.
- **`npm ci` collisions** (problem 5) happen inside one job at any concurrency. Three jobs also mean three `npm ci` and three `next build` runs at once, so the 5.5-minute gate will get slower.
- **Port 3210** is not used by `checks.sh`, so the demo server was not at risk.

## Quality: the 8 acceptance criteria
Checked by me against the PR branch (`160d007`): I read the full diff, re-ran the branch unit tests (9 of 9 pass), and drove `/branches` and `/member` in a browser at 375px.

| # | Criterion | Result | How I checked |
|---|---|---|---|
| 1 | `/branches` under the demo bar with the fictional label | Met | Browser: label visible, demo bar above the page |
| 2 | 34 synthetic branches from a typed fixture, five fields each, test for 34 unique names and postcodes | Met | Browser: 34 cards with name, address, postcode, hours, step-free text. Diff: `Branch` type, 34 entries, all postcodes end `9ZZ`, none is `CV3 9ZZ`. Tests run |
| 3 | Search as you type by town, name or postcode, ignoring case; pure `searchBranches` with the three named tests | Met | Browser: `COV` gives the 3 Coventry branches, `cv219zz` gives Rugby. Tests run |
| 4 | "No branches match" with a link to Ask Binley at `/member` | Met | Browser: `zzzz` gives the message and the link |
| 5 | "Book an appointment" visibly disabled, labelled "Coming soon", not a dead link | Met | Browser: 34 native disabled buttons, "Book an appointment · Coming soon" |
| 6 | Usable at 375px with no horizontal scroll; existing tokens; no new dependency | **Partly** | No element of the new page overflows, only existing tokens are used, and `package.json`, the lockfile and `globals.css` are unchanged. But the document does scroll sideways: I measured it 406px wide at a 375px viewport once the demo bar had loaded. The cause is the existing "Acting colleague" select in the demo bar, which the issue says not to change |
| 7 | One link to `/branches` on `/member` | Met | Browser: exactly one, "Find a branch" |
| 8 | lint, typecheck, test, build pass | Met | Gate log for `160d007`: `checks.sh` exit 0, 236 tests. I did not re-run the full set myself |

Seven met, one partly. The data is synthetic, and the label is on the page.

## Recommendation: go with changes
The pipeline itself worked on Windows: state moved only through the scripts, the gate and the missing-review guard did their jobs, and the result is a clean, small PR for about $4.45 and 38 minutes. I would use it for the wider programme at `concurrency` 1 once items 1 to 4 are done, and raise concurrency only after 5 and 6.

1. **Decide who merges.** Either add a permission rule that allows `factory/bin/job merge`, or accept that every job stops at `approve` for a person to merge. Without one of these the factory cannot finish a job unattended. If a person runs factory scripts by hand, push the gate fix (`fd6951d`) first, or run them from Git Bash.
2. **Fix git sign-in once**, for every clone the factory runs in (`gh auth setup-git`, or the repo-local helper used here).
3. **Give the review agents a browser.** Install `agent-browser` or change the agent definitions to use the repo's Playwright, and make a reviewer that could not open the page say so in its verdict instead of passing.
4. **Stop the builder and its Stop hook running `npm ci` at the same time** (one lock around `checks.sh` per worktree is enough).
5. **Before `concurrency` above 1:** make the Windows job lock wait instead of failing after 10 seconds, and kill child processes when a script is stopped.
6. **One dev server per worktree:** start one for both UI reviewers and stop it by port when the review ends.
7. **Make `job advance` safe to re-run** (post the issue comment last, or skip it when one exists).
8. **Decide the rule for narrowed criteria.** The spec writer weakened criterion 6 and the approver waved it through as a follow-up. Either intake marks that as a rescope or the approver escalates it.
9. **Run two or three more single issues first**, including one that should fail review and one with a security surface, because this pilot only exercised the all-PASS path.
10. **Check the prices** in `factory/config.json` before relying on the cost figures.

Follow-up ticket worth filing: the demo bar's colleague select overflows by 31px at 375px on every page.

## State left behind
- Local `factory-pilot` is two commits ahead of `origin/factory-pilot` (`832d300`, the cost fix, and `fd6951d`, the gate fix), not pushed, and three behind it (the merged feature). It needs a pull, and a push if the fixes are to be kept.
- Job `001-pilot-branch-finder-page` is `merged`. Issue #23 is still open with the `factory` label; close it or remove the label by hand.
- This clone's git config has the repo-local `gh` credential helper.
- Worktree `.worktrees/001-pilot-branch-finder-page` is clean on `factory/001-pilot-branch-finder-page`; no dev server is left on 5110 to 5112.
- Nothing was done to `main`, `spec-5-integration`, any `ticket-*` branch, PRs #20 and #21, or the `BinleyBuildingSociety` folder. No other issue was labelled and no second job was started. `npm run test:e2e` was not run.
