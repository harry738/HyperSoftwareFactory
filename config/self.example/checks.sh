#!/usr/bin/env bash
# The checks for this repo when the factory builds itself. An example: copy it to
# $FACTORY_HOME/projects/<project>/checks.sh, and merge the keys in
# config.overrides.json into the config.json that `factory onboard` wrote there.
#
# The gate runs it with the job's worktree as the working directory, so the tests
# run the branch's engine. Needs PyYAML (requirements.txt), and lsof on Linux.
set -euo pipefail

# Without these the tests would read the live project's config instead of their own.
unset FACTORY_HOME FACTORY_PROJECT

bash scripts/test.sh
