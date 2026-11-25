# Factory use cases

Examples use fictional repositories and issue numbers. They describe expected workflows, not a recorded real-project execution. Follow the [quick start](README.md#quick-start) first.

## 01 / Deliver a small change

Label a scoped issue `factory` with acceptance criteria. Run:

```bash
python factory/bin/factory run project-alpha 42
python factory/bin/factory status project-alpha
```

Expected: intake and spec, builder changes in a worktree, deterministic gate, routed independent reviews, a PR and operator decision. Inspect evidence before merging. The first central real-project run is still open.

## 02 / Repair a failed quality gate

In a disposable test repository, create a task that includes a reproducible failing check. The gate should reject failed checks and send the job to bounded rework; after the configured limit, hand back to the operator. Do not weaken the test or change the protected policy to manufacture a pass.

## 03 / Demonstrate policy escalation

Use a disposable task that would touch a protected path or trigger an always-stop rule. Inspect the PR and decision record. Protected-path violations must not merge; human-required decisions must remain with the operator. Do not attempt a bypass.

## 04 / Monitor projects

```bash
python scripts/factory-dashboard.py
```

Open http://localhost:8020/ locally. Inspect project tabs, job states and PRs. Restart after onboarding another project. The dashboard is read-only; decisions stay with the operator. Do not expose it to the public internet.

## 05 / Reproduce the test evidence

```bash
python -m pip install -r requirements.txt
bash scripts/test.sh
```

The test suite uses stand-ins for GitHub and Claude in the central runner; it requires no model calls. Windows-only tests are skipped on other systems.

## Planned scenarios

Scheduled Hermes runs, shadow Dev council, holdout checks, deployment/rollback and weekly Kaizen are roadmap items. See the [build plan](reference/build-plan.md).
