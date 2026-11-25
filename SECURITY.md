# Security and governance

The factory is a supervised pilot, not a production security boundary or an autonomous delivery service. Follow [CONTEXT.md](CONTEXT.md) and the [build plan](reference/build-plan.md).

| Control | Current position |
|---|---|
| Scripted control flow and state | Implemented; agents do not own transitions |
| Private project rules and checks | Outside the builder worktree; logical separation, not hard filesystem isolation |
| GitHub credentials | Engine owns API/push operations; GitHub tokens stripped from stage environments |
| Independent reviews | Read-only tools and branch-unchanged checks; some UI/UX tools can still write elsewhere |
| Quality and risk gates | Scripted checks, protected paths, label/path policy and bounded repair |
| Cost/time controls | Stage/job/daily budgets and stage time/turn limits in code |
| Container and egress | Local Docker image/proxy checks passed; signed-in run and hard engine/agent separation open |
| Anti-slop complexity threshold, full secret isolation | Target controls, not fully implemented |
| Audit evidence | Append-only events and PR evidence; not a cryptographically signed audit trail |

## Safe operating posture

Keep `unattended_merge: false` and required branch protection. Use a disposable or low-risk project first. Keep project names, paths, secrets, logs and private configs outside public repositories. Review each job and its evidence. Keep the dashboard bound to localhost. Do not treat a model verdict as permission to bypass a gate or protected path.

No autonomy level has been earned on a real project. FullAuto is planned and operator-selectable only; hard policy boundaries must continue to apply. Do not rely on planned controls to protect production data.

## Residual risk and reporting

Worktrees do not sandbox agents. Agent and engine currently share a container user; a malicious input or dependency may still cross logical boundaries. Reviewers' tool restrictions are not equivalent to OS-enforced read-only access. Verify isolation and credentials before any sensitive workload. Report suspected vulnerabilities privately to the repository maintainer (for example through GitHub private vulnerability reporting if enabled). Do not post secrets or exploit details in public issues. No dedicated response SLA is claimed.
