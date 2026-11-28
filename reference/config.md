# Project config.json

Each project has a `config.json` in `$FACTORY_HOME/projects/<name>/`. `factory onboard` writes it from the template, `factory/config.json`: it adds `repo` and sets `base_branch` to the clone's default branch. This page lists every key of the template, plus `repo` and `council`, which the template does not have.

"Default" is the value in the template. Where `factory/bin/run` has its own fallback for a missing key, the entry says so. `factory/test_config_doc.py` fails when a template key has no entry here.

## Path patterns

`protected_paths`, `sensitive_paths` and `risk_paths` hold `fnmatch` patterns, matched against the repo-relative path of each changed file. In `fnmatch`, `*` also matches `/`: `docs/*` matches `docs/a/b.md` as well as `docs/a.md`.

## Keys

### `concurrency`

How many jobs can be running at once. `factory/bin/job` refuses to start a job past it and holds the rest in the frontier. Default: `1`. Read by `factory/bin/job`.

### `max_rounds`

How many build rounds a job gets. A new job's `round_limit` is set from it, and a job sent back from needs-human with feedback gets this many more rounds. Default: `3`. Read by `factory/bin/job`.

### `base_branch`

The branch jobs start from, diff against and merge into. `onboard` sets it to the clone's default branch (from `origin/HEAD`), keeping the template value when that cannot be read. Default: `"main"`. Read by `factory/bin/job`, `factory/bin/gate`, `factory/bin/run` and `factory/bin/factory` (onboard, and the readiness check of the branch's protection).

### `merge_method`

How the factory merges a PR: passed to `gh pr merge` as `--<method>`, so `merge`, `squash` or `rebase`. Default: `"merge"`. Read by `factory/bin/job`.

### `unattended_merge`

Whether an approved job may merge without a person. It allows that only when it is the JSON boolean `true`; a missing key or any other value (including `"true"` or `1`) means a person merges. Default: `false`. Read by `factory/bin/job` and `factory/bin/run`.

### `job_budget_usd`

The cost cap in USD across all of a job's stages. A new job's `budget_usd` is set from it, and `job retry` on a job a limit stopped tops its budget up by this much over what it has spent; `factory/bin/run` stops the job when it reaches its budget. Default: `15`. Read by `factory/bin/job`.

### `daily_budget_usd`

The project's cost cap in USD per UTC day, across all its jobs. Once today's spend reaches it, the run ends before the next stage and every job stays where it is. A missing key means no daily cap. Default: `50`. Read by `factory/bin/run`.

### `stage_budget_usd`

The cost cap in USD for one stage. Default: `5` (also `run`'s fallback). Read by `factory/bin/run`.

### `stage_max_turns`

The turn cap for one stage. Default: `300` (also `run`'s fallback). Read by `factory/bin/run`.

### `stage_timeout_minutes`

The wall-clock limit for one stage, in minutes. Default: `60` (also `run`'s fallback). Read by `factory/bin/run`.

### `stage_stall_minutes`

How long a stage may produce no output before it is stopped, in minutes. Default: `20` (also `run`'s fallback). Read by `factory/bin/run`.

### `retry_waits_seconds`

The waits, in seconds, before each retry of a stage that failed for a passing reason such as a rate limit. Its length is the number of retries. Default: `[30, 120, 480]` (also `run`'s fallback). Read by `factory/bin/run`.

### `trusted_logins`

GitHub logins, besides the operator's, whose `/factory` comments and changes-requested reviews on a waiting job's PR start its next round. Default: `[]`. Read by `factory/bin/job`.

### `labels`

The issue label names the factory uses. An object with the keys `queue` (issues the factory works on), `needs_info`, `needs_human`, `ready` and `human_merge` (an always-stop: a person merges), each mapping to a label name. Read by `factory/bin/job` and `factory/bin/frontier`.

### `routing`

The reviewers for each risk tier. An object from risk tier (`low`, `medium`, `high`) to an object from reviewer role to model. Read by `factory/bin/route` and `factory/bin/job` (when the changed paths raise a job's risk).

### `surface_reviewers`

Extra reviewers for a surface that intake names. An object from surface (such as `ui` or `security`) to an object from reviewer role to model. Read by `factory/bin/route`.

### `protected_paths`

Paths a branch must not touch. `factory/bin/gate` fails a branch that adds, modifies, deletes or renames a matching file. A list of [path patterns](#path-patterns). Default: the template's checks, config, `factory/bin/*`, `CLAUDE.md`, `AGENTS.md`, `.github/workflows/*` and `.claude/*`. Read by `factory/bin/gate`.

### `sensitive_paths`

Paths whose change makes a job high risk, adds `sensitive_reviewers` and sends the job to a person whatever the reviews say. A list of [path patterns](#path-patterns). Default: package manifests, lockfiles and `*.env*`. Read by `factory/bin/job`.

### `sensitive_reviewers`

Reviewers added when a job changes a sensitive path. An object from reviewer role to model. Read by `factory/bin/job`.

### `risk_paths`

The changed paths that set a job's lowest risk tier. An object with the keys `low` and `high`, each a list of [path patterns](#path-patterns). Any `high` or sensitive file makes the job high; it is low only when every changed file matches `low`; otherwise it is medium. Read by `factory/bin/job`.

### `ports`

The ports a job's servers use. An object with the keys `base` and `step`: job `n`'s port is `base + step × n + offset`, with offset 0 for the builder and 1 for the reviewers' dev server. Read by `factory/bin/job` and `factory/bin/run`. `factory/checks.sh` does not read `ports`: it hard-codes its own port, so the two have to be changed together by hand.

### `dev_server`

The command that starts the reviewers' dev server, as an argv list, run in the worktree with `{port}` filled in. It is started only when a `ux` or `ui` reviewer runs. It can be left out when a project has no pages. Default: a Next.js dev server. Read by `factory/bin/job`.

### `prices_usd_per_mtok`

Model prices for working out a job's cost from its transcripts. An object from model id to an object of USD prices per million tokens, with the keys `input`, `output`, `cache_write_5m`, `cache_write_1h` and `cache_read`. It is used only when a job has no `usage.jsonl`. Read by `factory/bin/job`.

### `repo`

The source the project was onboarded from: a GitHub `owner/name` or a git URL or path. The template has no such key: `onboard` writes it. No script under `factory/bin/` reads it; `scripts/factory-dashboard.py` reads it to list the project's PRs.

### `council`

The template has no such key. When it is present, `factory/bin/job` sends a job bound for needs-human through the `council` stage first. `factory/bin/run` currently passes that stage straight through to needs-human.
