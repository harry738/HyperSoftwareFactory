# AGENTS.md

Rules for changing this repo, for people and agents. What the product is and its hard rules are in [CONTEXT.md](CONTEXT.md).

## Layout

| Path | What's in it |
|---|---|
| `factory/bin/` | The engine: `factory` (command line), `run` (the loop), `job` (state machine), `gate`, `route`, `frontier`, `proc.py` |
| `factory/config.json`, `factory/checks.sh` | Templates that `factory onboard` copies into a project's config folder |
| `.claude/agents/`, `.claude/skills/factory/`, `.claude/hooks/` | The stage agents, the `/factory` skill and the hook that blocks hand merges |
| `scripts/` | The registry wizard, the multi-project dashboard, and `test.sh` |
| `config/` | Examples only. `config/self.example/` is this repo's own project config |
| `reference/` | The [build plan](reference/build-plan.md) (what exists, what is next) and the longer-term architecture |

## Setup and tests

```bash
pip install -r requirements.txt
bash scripts/test.sh
```

`scripts/test.sh` runs every `test_*.py` under `scripts/` and `factory/` and stops at the first failure. CI runs the same command. It needs Python 3, git and bash, and `lsof` on Linux. It needs no GitHub access and makes no model calls.

- Tests are plain Python scripts: `test_*` functions with bare `assert`, run from `__main__`. There is no test framework.
- `factory/test_run.py` runs the central layout end to end, with stand-ins for `gh` and `claude`.
- `factory/test_factory.py` covers the Windows patches and runs only on Windows; `scripts/test.sh` skips it elsewhere.

The only page is the dashboard: `cd factory && python -m http.server`, then open `/dashboard.html`. Its user is the operator.

## Conventions

- `factory/` uses the Python standard library only. PyYAML is the one dependency, and only `scripts/` uses it.
- Scripts in `factory/bin/` have no file extension and start with a docstring that gives their usage.
- `factory/bin/job` is the only writer of job state.
- Enforce in scripts and platform settings, not in prompts. `factory run` owns the control flow; no model decides what happens next.
- The agents are project-neutral: nothing in `.claude/agents/` names or assumes a project. A project's rules live in that project's own `AGENTS.md`.
- A `# ponytail:` comment marks a deliberate simplification and names its limit. A `# binley:` comment marks a Windows patch, to be deleted once the container works.
- `factory/**`, `*.sh` and the agent definitions use LF line endings (`.gitattributes`).
- `factory/`, `.claude/agents/` and `.claude/skills/factory/` are GPLv3; the rest is MIT. Vendored skills keep their own licences.
- `README.md` and the build plan's status column describe what exists. A change in behaviour updates them.

## Public repo

This repo is public. Nothing in it names a real project, a private repo or a local path: not code, tests, docs, examples or commit messages. Those live in the private factory home (`$FACTORY_HOME`), with each project's `checks.sh`, `setup.sh` and path rules. Secrets are in neither. Examples use placeholders such as `your-org/project-alpha`.
