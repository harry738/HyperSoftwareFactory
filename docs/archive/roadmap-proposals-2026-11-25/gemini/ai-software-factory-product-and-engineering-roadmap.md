> **Archived 25 Nov 2026.** Historical proposal, superseded by [reference/build-plan.md](../../../../reference/build-plan.md) (one roadmap). Its status claims and links are not maintained.

<!--
Exported copy of a planning document. The source original was left in place and was not modified or deleted.

- Source document: AI Software Factory — Product & Engineering Roadmap
- Source: exported from the operator's planning docs
- exported 25 Nov 2026, source: a planning conversation (per the operator)
-->

# AI Software Factory — Product & Engineering Roadmap

## Vision

Build an autonomous, spec-driven software factory platform that enables users to transform high-level intent into production-grade, verified software through structured discovery, deterministic pre-generation guardrails, self-correcting inner execution loops, and fresh-context verification.

---

## Phase 1: Foundation & Pre-Generation Guardrails (Weeks 1–3)

**Objective:** Establish deterministic steering documents and structured intent capture so agents start right the first time.

* **Milestone 1.1 — Root Steering Architecture (`AGENTS.md`):**  
  * Deploy root and nested `AGENTS.md` templates defining the Context Pyramid, Task Router, and Always / Ask First / Never operational boundaries.  
  * Enforce architectural invariants (e.g., domain logic isolation, schema-first boundary parsing).  
* **Milestone 1.2 — Automated Discovery & Interrogation Engine:**  
  * Implement the 3-part Discovery Issue Template (Context Boundaries, Risk Classification, Validation Criteria).  
  * Build interactive interrogation workflows that generate living specifications (`docs/specs/<issue-id>.md`) and Architecture Decision Records (`docs/adr/ADR-*.md`).  
* **Milestone 1.3 — Risk-Gated Planning Workflow:**  
  * Enforce Tier 1 / Tier 2 / Tier 3 risk routing, requiring verified vertical-slice Implementation Plans and human sign-off for Tier 3 changes prior to code generation.

---

## Phase 2: Deterministic Inner-Loop Execution & Quality Gates (Weeks 4–6)

**Objective:** Build self-correcting agent execution loops backed by machine-verifiable static analysis and automated tests.

* **Milestone 2.1 — Sandboxed Execution Harness:**  
  * Provision isolated container environments with pre-configured package managers, compilers, and environment variables.  
* **Milestone 2.2 — Pre-PR Quality Gate Pipeline:**  
  * Integrate strict static type-checking, AST linting, formatting checks, and secret scanning into local pre-commit hooks and GitHub Actions.  
  * Configure autonomous retry loops so agents self-correct failing lint, type, or unit test checks until the build is green.  
* **Milestone 2.3 — Spec-to-Test Traceability:**  
  * Require every acceptance criterion in `docs/specs/<issue-id>.md` to map to automated unit/integration tests with \>= 90% branch coverage on new domain logic.

---

## Phase 3: Fresh-Context Verification & Autonomous PR Lifecycle (Weeks 7–9)

**Objective:** Eliminate reviewer bias and ensure production readiness before human review.

* **Milestone 3.1 — Fresh-Context Reviewer Agent:**  
  * Spin up isolated, clean-context review agents that audit diffs against `AGENTS.md`, the approved spec, security baselines, and architectural boundaries.  
* **Milestone 3.2 — Automated PR Assembly & Audit Trail:**  
  * Auto-generate pull requests linking the living spec, ADR, test coverage report, and rollback plan.  
* **Milestone 3.3 — Multi-Tenant Platform & User Workspace:**  
  * Enable end users to onboard repositories, customize `AGENTS.md` rule packs, and launch end-to-end software factory runs via web UI and CLI.

---

## Phase 4: Ecosystem Integrations & Continuous Optimization (Weeks 10–12)

**Objective:** Expand platform capabilities with external best-practice knowledge bases and telemetry-driven improvements.

* **Milestone 4.1 — External Best-Practice & Docs Connectors:**  
  * Integrate live documentation retrieval (e.g., Context7) and framework-specific best-practice rule packs (e.g., Chrome/web performance, OWASP security).  
* **Milestone 4.2 — Factory Telemetry & Loop Analytics:**  
  * Track first-pass green build rates, retry loop counts, and spec-drift metrics to continuously refine steering prompts and lint rules.
