# CONTEXT.md

What this product is and the rules it must keep. The short form of [README.md](README.md) and the [build plan](reference/build-plan.md); the build plan has the detail and the current status.

## What it is

A software factory. It takes a GitHub issue labelled `factory` through intake, spec, build, a deterministic gate, independent reviewers and an approver. Each issue becomes one PR, which is merged, sent back for changes, or handed to the operator.

The objective is one factory that takes signals (issues, bugs, requirements, market changes) to deployed, verified, monitored software across the operator's own projects, with the operator setting policy and not reviewing every change.

The user is the operator: the one person who sets policy and decides every job that stops.

## How it runs

- **Central, not per repo.** One factory serves every project. Nothing from the engine is copied into a project repo.
- **Claude Code is the development engine.** Every stage is one headless Claude Code run with its own agent definition.
- **The loop is a script.** `factory run` owns the control flow and starts one stage at a time.
- **Project config stays out of the project.** A project's `checks.sh`, `setup.sh` and path rules live in a private factory home, so the builder cannot change the checks or rules it is judged by.
- **The engine does every push and every GitHub call.** Agent stages run without the GitHub token.
- **Linux, then a container.** The engine is built on plain Linux and deployed as one container.
- **Own projects only.** Generality is added when a second project forces it.

## Hard rules

1. No unreviewed output: every PR is reviewed by at least one independent verifier.
2. Evidence over "PASS": a bare "PASS" counts as inconclusive.
3. A complexity increase above 50% on touched files blocks the PR for architecture review.
4. At most three review-fix rounds per job.
5. All secrets stay outside the sandbox.
6. Always-stop rules by label and path outrank everything, including the Dev council. A branch that fails the gate or touches a protected path does not merge in any mode.
7. Autonomy is earned per project, on measured jobs on a real project. In the default mode, `supervised`, every job stops for the operator until the Dev council has earned merge power. Only a person can select FullAuto mode; no agent, and not the factory itself, can turn it on.
8. Enforce in scripts and platform settings, not in prompts.
9. Backpressure before forward pressure: checks, budgets and isolation land before anything that creates more work.
10. This repo is public. Nothing in it names a real project, a private repo or a local path.

The scripts enforce rules 1, 2 and 4 today. Rule 3 is a target and is not built.

## Not building

- Steering a run while it is in progress. Feedback goes in between rounds.
- Other models for the builder or the reviewers. Only council seats use other vendors.
- A merge queue, a webhook server, a mobile app.
- Parallel builders inside one spec, Prometheus metrics, microVM isolation. Each waits for evidence that it is needed.
