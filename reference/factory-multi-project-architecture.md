# Factory Multi-Project Architecture

**Source:** Product Council design session, 2026-11-19
**Updated:** 2026-11-22

---

## Architecture

```
harry738/HyperSoftwareFactory  ← Factory platform (config, scripts, reference)
your-org/project-alpha         ← Project A
your-org/project-beta          ← Project B
your-org/project-gamma         ← Project C (future)
```

The factory lives in **HyperSoftwareFactory**, this repo. The target is to manage all projects through a single config file.

**Today:** the working factory is installed per project by copying `factory/` and `.claude/` into the project repo, and it does not read `config/projects.yaml`. Only the dashboard does (below). Whether the registry drives installs or is dropped is decided when the second project is onboarded (build plan S6.1).

## Config

`config/projects.yaml` defines every project. It is gitignored: this repo is public, and the registry names real projects and paths on your machine. `config/projects.example.yaml` shows its shape:

```yaml
projects:
  alpha:
    name: "Project Alpha"
    repo: "your-org/project-alpha"
    roadmap: "docs/product/roadmap.yaml"
    inbox: "docs/product/roadmap-inbox/"
    council_enabled: true   # true = Full Council at gates 2/3; false = Chair-only Fast Council
    sprint_cadence: weekly
    alert_channel: "telegram:[YOUR_TELEGRAM_CHAT_ID]"
    path: "/path/to/project-alpha"   # local checkout, read by the dashboard
```

Planned fields, added in build plan Step 5: `risk_paths`, `deploy`, `budget`, `baseline_target`.

## How signals are routed

```
Signal arrives → triage → tagged with project slug ("alpha", "gamma")
                         │
                    ┌────▼────┐
                    │  CONFIG  │
                    └────┬────┘
                         │
               Factory writes build spec
               to that project's roadmap-inbox/
                         │
                         ▼
              Project's own repo gets the spec
              Claude Code builds → PR → merge → deploy
```

## Dashboard

`python scripts/factory-dashboard.py` serves one dashboard with a tab and a kanban board per project. It reads each project's `<path>/factory/jobs/`, so a project needs `path` set and the factory installed in that checkout. Each tab shows the jobs running and the jobs waiting on you.

Still planned, one table across all projects:

```
  PROJECT       | INTAKE | BUILD | VERIFY | DEPLOY | COST TODAY
  ──────────────┼────────┼───────┼────────┼────────┼───────────
  alpha         │   0    │   2   │   1    │   0    │  $14.23
  beta          │   1    │   0   │   0    │   0    │   $1.20
  gamma         │   0    │   0   │   0    │   0    │   $0.00
```

## Onboarding a new project

```bash
# Interactive wizard
python scripts/factory-onboard.py --interactive

# Or CLI mode
python scripts/factory-onboard.py \
  --name gamma \
  --repo your-org/project-gamma \
  --council fast \
  --cadence weekly
```

The script:
1. Validates the slug and rejects one that is already registered
2. Checks the repo exists (interactive mode offers to create it, as a **private** repo)
3. Adds the project to `config/projects.yaml`
4. Writes drafts to `onboarding/<slug>/`: `roadmap.yaml` with a first RM, `roadmap-inbox/`, and a `.factory.md` project card

It does not push to the project repo. Review the drafts and commit them there yourself.

## Design decisions

| Decision | Why |
|---|---|
| Each project has its own repo | Own CI/CD, issues, PRs, secrets. Keeps concerns separate. |
| Factory lives in its own repo | One install, all projects benefit. |
| Config in YAML | Human-readable. Kept out of git: this repo is public and the projects are not. |
| Repo inbox pattern | Claude reads from `origin/main` — pushing to inbox is the delivery. |
| Vault stays local | Handovers are transient. Canonical docs live in GitHub. |
