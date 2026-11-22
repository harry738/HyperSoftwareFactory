# Assurance hardening recommendations

**Reviewed:** 2026-11-22  
**Scope:** the working factory in `factory/` and `.claude/`.

**Principle:** Implementation agents must not be the sole authority that accepts or merges their own output.

## Priority 0 — prevent unsafe autonomous merges

| ID | Finding | Recommendation | Status in this PR |
|---|---|---|---|
| P0-01 | Protected paths ignore new files and rename destinations | Inspect additions, deletions, modifications and both rename endpoints; test workflow creation | Implemented |
| P0-02 | Reviews are not attached to immutable inputs | Bind verdicts to head SHA, base SHA and hashes of issue/spec; recheck on approval and merge | Implemented |
| P0-03 | An agent's risk opinion can trigger merge | Deterministic path-based risk floor; unknown paths MEDIUM; no unattended merges by default | Implemented, disabled by default |
| P0-04 | Original acceptance criteria can be silently narrowed | Require explicit scope-change declaration and issue-to-spec traceability; escalate altered or missing information | Partial |

P0-04 is a **structural safeguard**, not proof of semantic equivalence. A model can still incorrectly claim an unchanged requirement. Keep human review until an independent traceability evaluation is in place.

### How the new controls work

At entry to review, `job` records the exact head SHA, base SHA, and SHA-256 of `issue.md` and `spec.md`. Each reviewer writes `COMMIT: <full SHA>` after its verdict; the approver records the reviewed commit too. A stale review, changed spec, moved base or changed head blocks approval/merge. Merge synchronises the base and runs checks again, and refuses if the review binding is no longer valid.

`factory/config.json` now contains `risk_paths` and a fail-closed `merge_policy.allow_unattended: false`. The risk floor is calculated from *changed paths*, with HIGH outranking MEDIUM and LOW; agent intake can raise but cannot lower that risk. Unmatched paths default to MEDIUM. With unattended merging disabled, the factory escalates the approved PR for human review and manual GitHub merge. Turning this on requires a deliberate risk-policy review and stronger independent verification.

The configurable path patterns are a conservative baseline, **not** a complete security policy for every project. High-impact project-specific paths must be added before any unattended merge is considered.

### Tests

```bash
python scripts/test_factory_onboard.py
python -m unittest discover -s factory -p test_assurance.py -v
```

The new GitHub Actions workflow runs both tests on Windows and Linux. The older `factory/test_factory.py` checks Windows integration behaviour in a project environment and is not replaced.

## Priority 1 — next implementation work

| ID | Recommendation | Exit criterion |
|---|---|---|
| P1-01 | Enforce genuinely read-only reviewers, using separate workspaces and credentials | Reviewer cannot write implementation files or modify verifier evidence |
| P1-02 | Isolate agents in short-lived containers or VMs with scoped credentials and egress | Tests prove no access to sibling projects, host secrets or forbidden hosts |
| P1-03 | Hard run-level dollar and wall-clock budgets | Deliberately runaway job terminates within its assigned limits |
| P1-04 | Mandatory test, browser and security evidence in review outputs | No evidence means INCONCLUSIVE; approval cannot proceed |
| P1-05 | Project-specific policy profiles; remove Binley references from generic agents | Generic workflow supports two distinct project domains |
| P1-06 | Required GitHub branch rulesets and review/check conditions | Merge denied by GitHub itself when checks or approvals are missing |
| P1-07 | Security scanning: secrets, dependencies, SAST and changed complexity | Intentionally bad test fixtures fail the configured checks |
| P1-08 | Negative-path and integration benchmark with real issues | Ten jobs cover FAIL, CHANGES, escalations, resumption and merge |

This PR does **not** implement P1-01 through P1-08 in full. CI is a portable unit-level starting point, not a complete integration suite. Repository rulesets require repository administration and are not set by these commits.

## Priority 2 — scale and portability after assurance

| ID | Recommendation | Exit criterion |
|---|---|---|
| P2-01 | Provider-neutral Claude Code / Codex / Cursor adapter | Same task and evidence schema works with at least two engines |
| P2-02 | Central project registry driving versioned installations | Second project onboarded without manual code-copy drift |
| P2-03 | Cross-job event log, accurate cost attribution and Kaizen | Reproducible metrics for throughput, cost, human edits and escapes |
| P2-04 | Review mixed GPLv3/MIT licensing and imported-skill provenance | Redistribution and modification rights explicitly documented |
| P2-05 | Bounded parallelism and recovery | Twenty jobs at concurrency three, no lost or duplicate actions |
| P2-06 | Monitored deployment and rehearsed rollback | Simulated bad release triggers verified rollback |

## Conditions before unattended merging

1. Require passing PR checks and appropriate human approvals in GitHub, independently of agent instructions.
2. Test protected additions, moved base, altered requirements, stale verdicts and high-risk paths as *negative* cases.
3. Demonstrate truly read-only independent review and verifiable behavioural/security evidence.
4. Run ten real pilot jobs, including failure, repair, escalation and recovery scenarios.
5. Approve each project's LOW-risk patterns; unclassified paths must never implicitly become LOW.
6. Revoke unattended-merge permission if an escaped defect or unexpected merge occurs.

**Baseline evidence:** Binley demonstrated one mostly successful job and a manual merge. This does not yet justify unattended production release.
