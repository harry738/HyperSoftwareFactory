# Factory Multi-Project Architecture

**Source:** Product Council design session, 2026-11-19
**Updated:** 2026-11-22

---

## Architecture

```
harry738/HyperSoftwareFactory  ← Factory platform (config, scripts, reference)
harry738/hyper-trading-system  ← Project A
harry738/HyperAISystemsOS      ← Project B
harry738/propInfo.co.uk        ← Project C (future)
```

The factory lives in **HyperSoftwareFactory**, this repo. The target is to manage all projects through a single config file.

**Today:** the working factory is installed per project by copying `factory/` and `.claude/` into the project repo, and it does not read `config/projects.yaml`. Whether the registry drives installs or is dropped is decided when the second project is onboarded (build plan S6.1).

## Config

`config/projects.yaml` defines every project:

```yaml
projects:
  hts:
    name: "Hyper Trading System"
    repo: "harry738/hyper-trading-system"
    roadmap: "docs/product/roadmap.yaml"
    inbox: "docs/product/roadmap-inbox/"
    council_enabled: true   # true = Full Council at gates 2/3; false = Chair-only Fast Council
    sprint_cadence: weekly
    alert_channel: "telegram:[YOUR_TELEGRAM_CHAT_ID]"
```

Planned fields, added in build plan Step 5: `risk_paths`, `deploy`, `budget`, `baseline_target`.

## How signals are routed

```
Signal arrives → triage → tagged with project slug ("hts", "propinfo")
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

The planned factory dashboard shows all projects in one view:

```
  PROJECT       | INTAKE | BUILD | VERIFY | DEPLOY | COST TODAY
  ──────────────┼────────┼───────┼────────┼────────┼───────────
  hts           │   0    │   2   │   1    │   0    │  $14.23
  hyperos       │   1    │   0   │   0    │   0    │   $1.20
  propinfo      │   0    │   0   │   0    │   0    │   $0.00
```

## Onboarding a new project

```bash
# Interactive wizard
python scripts/factory-onboard.py --interactive

# Or CLI mode
python scripts/factory-onboard.py \
  --name propinfo \
  --repo harry738/propInfo.co.uk \
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
| Config in YAML | Human-readable, git-tracked, PR-reviewable. |
| Repo inbox pattern | Claude reads from `origin/main` — pushing to inbox is the delivery. |
| Vault stays local | Handovers are transient. Canonical docs live in GitHub. |
