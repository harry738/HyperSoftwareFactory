#!/usr/bin/env bash
# The repo's checks. Exit 0 only when the branch is fit to review.
#
# The gate runs this script from the main checkout with the job's worktree as
# the working directory. Fast, deterministic, non-interactive, rewrites nothing.
#
# Not here yet: gitleaks (not installed on the factory machine).
set -euo pipefail

# The walkthrough's port: 5103 + 10n in job n's worktree (.worktrees/004-x → 5143),
# 5103 anywhere else. Never the demo's 3210, never a job's 5100-5102 + 10n.
n=$(basename "$PWD" | sed -n 's/^\([0-9][0-9][0-9]\)-.*/\1/p')
export PORT=$((5103 + 10 * 10#${n:-0}))

npm ci --prefer-offline --no-audit --no-fund
npm run lint
npm run typecheck
npm test
npm run build
npm run test:e2e
