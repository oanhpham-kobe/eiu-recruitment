# EIU Recruitment — Current Repository Deep Research

Status: IN PROGRESS
Research date: 2026-09-26
Repository: `oanhpham-kobe/eiu-recruitment`
Research branch: `autonomy/continuous-integration-20260905-01`
Baseline implementation SHA at research start: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
Research mode: read/diagnose first; no runtime implementation changes.

## Purpose

Create a durable, fact-based assessment of the current repository so recovery/continuation work does not depend on chat context. This file is intentionally usable as a handoff source for an independent Astra/OMP review.

## Research work breakdown

Each unit should be independently completable and checkpointed here before moving on.

- [x] DR-00 — establish immutable research baseline and repository control-plane map.
- [ ] DR-01 — reconstruct canonical Phase-1 product scope vs implemented user-facing runtime.
- [ ] DR-02 — reconstruct slice/task state machine and detect planning/state mismatches.
- [ ] DR-03 — inspect runtime architecture and distinguish sound boundaries from accidental duplication/debt.
- [ ] DR-04 — inspect CI/governance/review lifecycle cost and identify throughput bottlenecks.
- [ ] DR-05 — inspect production-readiness gaps: deployment, email delivery, storage/documents, security/ops.
- [ ] DR-06 — inspect frontend maintainability and UX completion gaps.
- [ ] DR-07 — synthesize KEEP / SIMPLIFY / ADD / DEFER recovery recommendations and prioritize next execution path.
- [ ] DR-08 — prepare independent Astra/OMP review handoff from this file if needed.

## Verified baseline

At research start, the integration branch points to:

`8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4` — `chore(governance): close accepted TASK-S08-001 lifecycle`

The research process may add documentation-only commits after this SHA. Runtime conclusions must continue to distinguish the original implementation baseline from later research-document commits.

## Early verified findings

### F-01 — Product scope is narrower than the governance/review surface

Canonical Phase-1 scope centers on the recruitment workflow Candidate → Submission/Application → Interview rounds → report, with Phase-1 UI including Application, Interview, Report, Master Data, and Users & Permissions. Dashboard/KPI/Candidate Database are future/hidden scope.

Implication: process/architecture complexity should be judged against this relatively bounded Phase-1 product rather than against a large general-purpose enterprise platform.

### F-02 — Governance/specification burden is materially large

The repository contains extensive pre-implementation review packs, prompt/re-review artifacts, task evidence and governance state. Even foundational tasks carry large acceptance/evidence sets. Full DB verification replays local Supabase migrations and regression gates across slices.

This does not prove the controls are wrong; DR-04 must separate controls that buy real safety from controls whose marginal value is below their throughput cost.

### F-03 — User-facing Slice-06 completion appears inconsistent with product truth

Canonical Phase-1 expects Master Data and Users & Permissions UI. However, the current runtime navigation exposes only Application, Interview and Report. Existing Slice-06 tasks explicitly establish backend/security contracts while excluding the Master Data management page and deferring the Users & Permissions management UI to later work.

Yet Slice-06 is represented as complete in current planning state. This is a candidate planning/state-model mismatch: completion of backend prerequisites may be getting conflated with completion of the user-facing slice. DR-01/DR-02 will verify exact source lines and downstream planner consequences.

### F-04 — Email capability is currently an outbox contract, not live external delivery

Current email work supports composing/enqueueing/consuming outbox-style email contracts but excludes live SMTP/SendGrid/Resend/background delivery in the relevant implementation task. The UI action therefore must not be interpreted as proof that mail is actually delivered externally.

DR-05 will determine whether this is correctly represented as a production-readiness gap or intentionally out of current release scope.

### F-05 — Runtime architecture is broadly coherent; rewrite is not presently justified

The observed server-action/read-adapter/typed-command/Supabase-RPC layering has a coherent security and transaction rationale. Authorization/validation occurs at multiple layers. Some of that is legitimate defense in depth; some may be duplicative maintenance burden.

Current evidence supports KEEP/SIMPLIFY investigation, not a framework/data-model rewrite.

### F-06 — Frontend orchestration debt exists in high-workflow components

`InterviewPage` and `SubmissionDetailDrawer` currently coordinate many mutation, dialog, selection, document/email/status workflows in large client components. This is refactorability debt rather than evidence of architectural collapse.

Likely direction: extract workflow hooks and focused subcomponents while preserving accepted contracts.

### F-07 — Delivery process volume is high enough to warrant explicit throughput analysis

At the research baseline, the integration branch is hundreds of commits ahead of `main` and the project has accumulated hundreds of GitHub Actions runs. Commit/run count is not itself a defect, but combined with exact-SHA review, repair/re-review and serialized evidence gates it is a strong signal that governance verification may be consuming a large fraction of elapsed delivery time.

DR-04 will quantify representative task lifecycles rather than relying on raw counts alone.

## Research rules

1. Do not infer DONE from slice labels alone; compare canonical product truth, task exclusions, runtime surface, and production behavior.
2. Do not recommend removing a security/control layer until its threat/consistency value is understood.
3. Separate product completeness, engineering quality, governance completeness, and production readiness; they are different dimensions.
4. Prefer exact repository evidence over historical chat summaries.
5. Write each completed DR unit into this file before starting the next one.
6. If Astra/OMP is invoked, provide this file plus a minimal exact-SHA source set so the reviewer can independently challenge the conclusions rather than inherit them as assumptions.

## Next unit

`DR-01 — canonical Phase-1 product scope vs implemented user-facing runtime`

Questions to answer:

- What exact Phase-1 modules/workflows are required by canonical product sources?
- Which are actually reachable in the current runtime UI at the baseline SHA?
- Which required behaviors exist only as backend contracts?
- Which UI actions are prototypes or partial contracts rather than production-capable behavior?
- Which missing surfaces are true blockers versus acceptable future work?
