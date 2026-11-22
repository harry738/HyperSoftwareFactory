#!/usr/bin/env bash
# The project's checks. Exit 0 only when the branch is fit to review.
#
# The gate runs this script from the main checkout with the job's worktree as
# the working directory. Keep it fast, deterministic and non-interactive, and
# never let it rewrite files (no auto-fix, no formatter in write mode).
#
# Replace the block below with this project's checks. A worked example for a
# Next.js app (lint, typecheck, unit tests, build, Playwright walkthrough) is in
# reference/binley/checks.sh.
set -euo pipefail

# A port per job, for anything that starts a server: 5103 + 10n in job n's
# worktree (.worktrees/004-x -> 5143), 5103 anywhere else. Clear of the reviewers'
# dev servers on 5100-5102 + 10n. Follows config.json ports; change both together.
n=$(basename "$PWD" | sed -n 's/^\([0-9][0-9][0-9]\)-.*/\1/p')
export PORT=$((5103 + 10 * 10#${n:-0}))

# ponytail: fails until set up, so a new project can't merge through an empty gate.
echo "factory/checks.sh has no checks yet. Edit it for this project." >&2
exit 1

# Example for a Node project:
# npm ci --prefer-offline --no-audit --no-fund
# npm run lint
# npm run typecheck
# npm test
# npm run build
