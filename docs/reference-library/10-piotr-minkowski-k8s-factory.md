# 10 Piotr Mińkowski — self-hosted factory on Kubernetes, Tekton and vLLM

Local reference-library notes only. Not in pull request #47. Not pushed from this review. Reviewed 25 November 2026 (Europe/London).

## Source

- **Author:** Piotr Mińkowski ([@piotr_minkowski](https://x.com/piotr_minkowski)), software architect and blogger.
- **Posted:** 20 November 2026, 08:39 UTC (08:39 UK time, Europe/London)
- **X post:** https://x.com/piotr_minkowski/status/2123697657936007565
- **Post text:** "I built an AI software factory that runs on Kubernetes. Open an issue or review a PR. Then, a GitHub webhook hits Tekton. Tekton pulls the context and starts an agent in a pipeline. The agent talks to a vLLM model in the same cluster."
- **Video:** about 39 seconds. **Not watched.** The linked repo README was used instead.
- **Repo:** https://github.com/piomin/ai-software-factory — "AI Software Factory running on Kubernetes / OpenShift with Tekton and vLLM." GitHub API on 25 November 2026: default branch `master`, 210 stars, last push 24 November 2026, 21:57 UTC (21:57 UK). Licence field was empty in the API (`None`); do not invent a licence.
- **README** fetched from `master` (the `main` raw URL 404'd). Related earlier blog posts exist (Tekton + Claude Code on OpenShift, 29 October 2026; OpenCode on Kubernetes, 7 October 2026); this entry relies on the post and the repo README.
- **Added:** 25 November 2026. Nothing was posted or replied to on X.

**Review date:** 25 November 2026 (Europe/London)

**Tags:** LLM provider spec (local / in-cluster model; data stays on the LAN except GitHub); Phase 2 (isolated runs, plan → agent → verify → publish); Phase 1 (plan comment, restrictions on who may trigger). Roster: recorded pipeline is the orchestrator, not a model choosing the next step.

**Scores:** Relevance H for the local-model and scripted-pipeline match. Actionability M (ideas yes; not a lift-and-shift to OpenShift). Novelty M.

**Dedupe:** Overlaps the LLM spec and E6 isolation; overlaps Holmes on plan-then-build. The README's "enables auto-merge" conflicts with the operator's rule and with the same README's "pull request with human approval" caption.

**What was and was not covered:** Post + README. The 39-second video was not watched.

## Summary

A self-hosted factory: GitHub issues, comments and PR reviews (HMAC-checked webhooks, CEL filters) start **Tekton PipelineRuns**. Stages: print-event → fetch-skills → prepare → plan → agent → verify → publish. The coding agent is **OpenCode**, talking to an open model (Qwen) served by **vLLM on GPU nodes in the same cluster**. "Nothing leaves the cluster except the calls to GitHub."

Pipelines include `issue-agent`, `@ai` comment handling, PR-comment follow-up, and an hourly `requirements-agent` that breaks down `requirements`-labelled issues and keeps at most three tasks open. Triggers only accept `OWNER`, `MEMBER` or `COLLABORATOR` (and the app's own task issues). Forks and strangers' issues on a public repo do nothing.

The overview figure describes "the pull request with human approval." The `issue-agent` table row also says it "enables auto-merge." The README later lists a **plan-approval gate** and a **reviewer agent** among further ideas (the plan-approval gate is described as something to add for larger issues). Do not treat auto-merge as the recommended part.

## What applies (review bar)

| Bar | Mapping (proposals only) |
|---|---|
| **Direct match** | Scripted, recorded control flow; plan then implement then verify; isolation per job; local/LAN models so code and issue text need not leave the machine (`data_leaving_lan` defaults to deny). |
| **Incorporate** | Keep (or tighten) trigger authentication so strangers cannot start factory jobs. A plan-as-comment plus wait-for-approval label is a concrete Phase 1 gate. In-cluster or LAN vLLM/Ollama as a first-class binding is already in the LLM spec. |
| **Inspiration** | Tekton-on-OpenShift as *an* execution substrate; requirements decomposition with a concurrency cap; Prometheus on the model server. |
| **Do not incorporate** | Enabling GitHub auto-merge. Rewriting `factory run` as a Tekton/OpenShift stack. Assuming the empty licence field is MIT. |
