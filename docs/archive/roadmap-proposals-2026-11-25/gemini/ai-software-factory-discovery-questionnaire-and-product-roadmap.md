> **Archived 25 Nov 2026.** Historical proposal, superseded by [reference/build-plan.md](../../../../reference/build-plan.md) (one roadmap). Its status claims and links are not maintained.

<!--
Exported copy of a planning document. The source original was left in place and was not modified or deleted.

- Source document: AI Software Factory — Discovery Questionnaire & Product Roadmap
- Source: exported from the operator's planning docs
- exported 25 Nov 2026, source: a planning conversation (per the operator)
-->

# **AI Software Factory — Discovery Questionnaire & Product Roadmap**

An automated, multi-stage software development infrastructure platform that turns human intent into verified, production-ready software via autonomous AI agents governed by deterministic guardrails and living repository specifications.

# **1\. Platform Vision & Core Architecture**

The platform governs the end-to-end software delivery process by moving sequentially through structured operational phases. Each stage enforces explicit validation mechanisms before handing off artifacts to downstream execution engines.

## **Core Lifecycle Stages**

* **1\. Discovery & Interrogation Phase:** AI acts as a structured researcher to capture scope, dependencies, reversibility, and edge cases before planning.  
* **2\. Specification & ADR Formalization:** Outputs living specifications (`docs/specs/<issue-id>.md`) and Architecture Decision Records (`docs/adr/ADR-<number>.md`) directly into the repository as an auditable source of truth.  
* **3\. Pre-Generation Steering & Planning:** Enforces machine-verifiable constraints via root/nested `AGENTS.md` files and requires a verified Implementation Plan before code generation starts.  
* **4\. Autonomous Execution & Inner-Loop Convergence:** Agents implement vertical slices inside isolated sandboxes, self-correcting iteratively against deterministic linters, type-checkers, and unit tests until green.  
* **5\. Fresh-Context Review & PR Gate:** Clean-context automated security, architecture, and spec-compliance audit prior to pull request creation and merge.

---

# **2\. Pre-Generation Discovery Questionnaire Template**

Used by the discovery agent during GitHub issue intake to eliminate ambiguity before planning or coding.

## **Section A: Context Boundaries & Scope**

* **Domain & Target Modules:** Which repository paths (`src/core/**`, `src/api/**`, `src/db/**`, UI) are in scope, and which are explicitly off-limits?  
* **External Dependencies & Integrations:** Are new third-party packages, external APIs, or live documentation lookups (e.g., Context7, framework best practices) required?  
* **Vertical Slice Decomposition:** How can this requirement be broken into independent, end-to-end testable vertical slices?

## **Section B: Risk Classification & Blast Radius**

* **Reversibility:** Can changes be rolled back cleanly without data loss or downtime?  
* **Data & Schema Impact:** Does this introduce database migrations, state mutations, or breaking API/webhook contract changes?  
* **Security & Auth Boundaries:** Does this touch authentication, RBAC/permissions, secrets, or external network ingress/egress?

### **Risk Tier Matrix**

| Risk Level | Trigger Conditions | Operational Protocol & Guardrails |
| :---- | :---- | :---- |
| **Tier 1 (Low)** | Single-module fix or UI tweak. Fully reversible with zero schema or API changes. | Automated spec checklist with single-pass plan verification. |
| **Tier 2 (Medium)** | Multi-file feature, internal API modification, or addition of new dependencies. | Full discovery Q\&A, vertical slice breakdown, and verified Implementation Plan. |
| **Tier 3 (High)** | Database schema migration, auth/security boundary changes, or breaking API contracts. | Full discovery Q\&A, formal ADR, explicit rollback plan, and mandatory human approval. |

## **Section C: Validation & Acceptance Criteria**

* **Testable Acceptance Criteria:** What specific inputs, outputs, and edge cases define "done"?  
* **Required Verification Suites:** Which unit, integration, contract, or E2E tests must pass before PR creation?  
* **Architectural Invariants:** Which linting rules, type constraints, and pattern templates must be enforced?

---

# **3\. Product Roadmap**

## **Phase 1: Foundation & Pre-Generation Controls (Weeks 1–3)**

### **Key Deliverables**

* Root and nested `AGENTS.md` steering architecture (Context Pyramid, Task Router, Always/Ask First/Never boundaries).  
* Living specification (`docs/specs/`) and Architecture Decision Record (`docs/adr/`) repository templates.  
* Automated Discovery Agent workflow triggered on new GitHub issues to run the 3-section interrogation questionnaire and assign Risk Tiers (Tier 1–3).  
* Implementation Plan gate blocking code generation until target files, edge cases, and test mappings are approved.

### **Exit Criteria**

100% of test issues produce a structured spec and verified Implementation Plan before any `src/**` file is modified.

---

## **Phase 2: Deterministic Inner-Loop Quality Harness (Weeks 4–6)**

### **Key Deliverables**

* Isolated sandbox execution environment with pre-configured package management (`pnpm --frozen-lockfile`) and secret scanning.  
* Pre-PR inner-loop verification harness enforcing strict static type-checking (`tsc`), AST linting (`ESLint` / architectural boundary rules), formatting, and unit test execution (`Vitest`).  
* Self-correction retry loop forcing the coding agent to resolve compiler, linter, and test failures autonomously before exiting.  
* Documentation and best-practice context injection (framework rules, Context7 / live docs integration) prior to generation.

### **Exit Criteria**

Agent self-corrects failing builds in isolated sandboxes with zero `--no-verify`, `@ts-ignore`, or `any` bypasses.

---

## **Phase 3: Fresh-Context Review & CI/CD Governance (Weeks 7–9)**

### **Key Deliverables**

* Clean-context reviewer agent evaluating generated diffs against the approved spec, ADR invariants, and OWASP security checks.  
* GitHub Actions CI pipeline blocking PR merges unless deterministic gates, branch coverage thresholds (\>= 90% on new domain logic), and fresh-context review pass.  
* Tier 3 human-in-the-loop approval checkpoints integrated into PR and issue workflows.

### **Exit Criteria**

Automated PR pipeline blocks non-compliant diffs and routes Tier 3 changes to human reviewers with full audit trails.

---

## **Phase 4: Multi-Tenant Platform & Self-Service Onboarding (Weeks 10–12)**

### **Key Deliverables**

* User-facing onboarding flow allowing external teams to initialize repositories with tailored `AGENTS.md`, discovery templates, and CI quality gates.  
* Telemetry dashboard tracking first-pass green rate, loop retry counts, spec-to-test coverage, and Tier 1/2/3 distribution.  
* Reusable domain packs (e.g., Full-Stack Web, API Microservice, Data Pipeline) with pre-built lint rules and coding pattern templates.

### **Exit Criteria**

External users can onboard a new repository and execute an end-to-end spec-to-PR workflow autonomously.
