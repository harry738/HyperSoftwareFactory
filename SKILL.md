---
name: hypersoftwarefactory-onboarding
description: Guide an operator through safe onboarding and a supervised first job in the central HyperSoftwareFactory.
---

# Onboard with an agent

Use this skill to guide the operator, not to give an agent independent control over merges. Read [AGENTS.md](AGENTS.md), [CONTEXT.md](CONTEXT.md), and the [build plan](reference/build-plan.md) first. This skill targets the central scripted CLI, not the legacy per-repo `/factory` skill.

## 1. Inspect readiness

- Use a non-production project with a useful test suite and required CI.
- Check Python 3, Git, bash, Linux/WSL (including lsof), authenticated GitHub CLI and installed, signed-in Claude Code.
- Confirm the operator authorises the repository and any model spend. Never request credentials in chat, commit secrets or print tokens.
- Use project-scoped credentials as described in the build plan; do not relax branch protection or expose a private factory home.

## 2. Install and onboard

```bash
git clone https://github.com/harry738/HyperSoftwareFactory.git
cd HyperSoftwareFactory
python -m pip install -r requirements.txt
export FACTORY_HOME="$HOME/factory-home"
python factory/bin/factory onboard your-org/project-alpha
```

Use a real repository only in the operator's private environment. Review the readiness checklist. Configure the project's checks.sh (the template intentionally fails), optional setup.sh and config.json in the private factory home. Confirm the base branch, protected and sensitive paths, trusted logins, budgets and `unattended_merge: false`. Confirm project AGENTS.md or CLAUDE.md and CONTEXT.md. Ensure required CI is enabled. Do not change policy merely to get a passing run.

## 3. Run one supervised job

Ask the operator to choose a small, well-scoped issue with acceptance criteria and label it `factory`. Obtain approval before starting a paid run.

```bash
python factory/bin/factory run project-alpha 42
python factory/bin/factory status project-alpha
```

Replace 42 with the chosen issue number. Inspect the resulting PR, test results, review evidence and job status. Do not merge or deploy on the operator's behalf, bypass failed checks, write job state directly, or enable FullAuto. Report blockers and stop if the environment is not ready.

## 4. Hand back evidence

Summarise the job, PR, checks, reviewer outcomes, cost/time if recorded, outstanding risks and operator decision needed. Redact private information. A failed gate, inconclusive review or missing evidence is not success.

The central runner has stand-in tests; a signed-in real-project run remains to be demonstrated. See [SECURITY.md](SECURITY.md) and [USE_CASES.md](USE_CASES.md).
