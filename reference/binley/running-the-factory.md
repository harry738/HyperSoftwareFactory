## Software factory

`/factory run` builds every open GitHub issue labeled `factory` through
intake → spec → build → gate → review → approve, one PR per issue.
`factory/bin/frontier` adds the `factory` label to `ready-for-agent` issues
whose blockers are closed; every run starts with it. State is in
`factory/jobs/` (gitignored); `factory/bin/job` is its only writer. Checks:
`factory/checks.sh`. Dashboard: `cd factory && python -m http.server`, then
open http://localhost:8000/dashboard.html.

Each job works in its own git worktree, a full checkout of the repo at
`.worktrees/<job-id>` (gitignored). A tool run from the repo root that doesn't
read `.gitignore` sees those copies too; exclude `.worktrees/` in its config.

Run the factory from its own clone (`<factory clone>`),
not from an app worktree: a worktree session can't load the factory's agents.
Every clone the factory runs in needs git to sign in through the `gh` CLI,
because the scripts make git fail instead of opening a sign-in dialog. Once
per clone (the empty value first clears Git Credential Manager, which Git for
Windows sets system-wide and which would otherwise run first):

```bash
git config --local credential.helper ""
git config --local --add credential.helper '!gh auth git-credential'
```

The scripts in `factory/bin/` carry Windows patches, each marked `# binley:`,
and `factory/bin/proc.py` holds the shared ones. From Git Bash run them as
`factory/bin/job ...`; from PowerShell as `python factory/bin/job ...`. Source
and licence (GPLv3): `factory/LICENSE`, from zazencodes-season-3
`src/software-factory-claude-code-v2`.
