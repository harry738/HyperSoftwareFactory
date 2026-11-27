"""PreToolUse hook: no agent merges a pull request by hand.

PRs merge only through `factory/bin/job merge` (which runs gh itself, outside
the agent's shell) or a person on GitHub. The deny rule in settings.json
missed `gh pr merge` chained after another command, so this checks the whole
command text. Exit 2 blocks the call and shows the reason to the agent.

ponytail: text matching. Catches `gh pr merge` in any form with gh, pr and
merge as separate words, and the REST merge endpoint. Code that builds the
words at run time gets past it; branch protection on GitHub is the real wall.
"""

import json
import re
import sys

HAND_MERGE = re.compile(r"\bgh(?:\.exe)?\b\W{1,6}pr\W{1,6}merge\b|/pulls/[^/\s]+/merge\b|\bmergePullRequest\b", re.I)


def main():
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    if HAND_MERGE.search(command):
        print("Merging a pull request by hand is blocked in this repo. Factory jobs merge with "
              "`factory/bin/job merge <job>`; anything else is merged by a person on GitHub.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
