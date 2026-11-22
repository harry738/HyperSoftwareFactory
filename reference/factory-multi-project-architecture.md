# Factory Multi-Project Architecture

**Source:** Product Council design session, 2026-11-19
**Filed:** 2026-11-19

---

## Architecture

```
harry738/HyperAISystemsOS    ← Factory platform (code, config, reference)
harry738/hyper-trading-system ← Project A
harry738/propInfo.co.uk      ← Project B (future)
```

The factory lives in **HyperAISystemsOS** — the OS repo. It manages all projects through a single config file.

## Config

`config/projects.yaml` defines every project:

```yaml
projects:
  hts:
    name: "Hyper Trading System"
    repo: "harry738/hyper-trading-system"
    roadmap: "docs/product/roadmap.yaml"
    inbox: "docs/product/roadmap-inbox/"
    council_enabled: true
    sprint_cadence: weekly
    alert_channel: "telegram:[YOUR_TELEGRAM_CHAT_ID]"
```

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

The factory dashboard shows ALL projects in one view:

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
python3 scripts/factory-onboard.py --interactive

# Or CLI mode
python3 scripts/factory-onboard.py \
  --name propinfo \
  --repo harry738/propInfo.co.uk \
  --council false \
  --cadence weekly
```

The wizard:
1. Checks repo exists (creates if needed)
2. Creates `docs/product/roadmap.yaml` with first RM
3. Creates `docs/product/roadmap-inbox/`
4. Writes `.factory.md` project card
5. Adds project to `config/projects.yaml`
6. Outputs next steps

## Design decisions

| Decision | Why |
|---|---|
| Each project has its own repo | Own CI/CD, issues, PRs, secrets. Keeps concerns separate. |
| Factory lives in its own repo | HyperAISystemsOS is the OS — one install, all projects benefit. |
| Config in YAML | Human-readable, git-tracked, PR-reviewable. |
| Repo inbox pattern | Claude reads from `origin/main` — pushing to inbox is the delivery. |
| Vault stays local | Handovers are transient. Canonical docs live in GitHub.