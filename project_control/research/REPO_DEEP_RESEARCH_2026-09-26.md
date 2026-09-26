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
- [x] DR-01 — reconstruct canonical Phase-1 product scope vs implemented user-facing runtime.
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

### F-03 — User-facing Slice-06 completion is inconsistent with canonical Phase-1 product truth

Canonical Phase-1 expects Master Data and Users & Permissions UI. The baseline runtime navigation exposes only Applications, Interviews and Reports, including for Root Admin. The complete runtime route tree has no corresponding Master Data or Users & Permissions management route.

The two Slice-06 tasks deliberately implement backend/security prerequisites and explicitly exclude their management pages, while the Slice Registry marks Slice-06 `DONE`. This is now verified as a planning/state-model mismatch rather than a navigation-only omission.

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

## DR-01 — Canonical Phase-1 product scope vs implemented runtime

Status: COMPLETE
Evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`

### Canonical Phase-1 navigation truth

The frozen/current product sources classify the following internal modules as `PHASE1_RENDERED`:

1. Phiếu ứng tuyển / Applications
2. Interview
3. Báo cáo phỏng vấn / Interview Reports
4. Danh mục / Master Data — when authorized
5. Người dùng & Phân quyền / Users & Permissions — when authorized

They classify Dashboard, Nhu cầu tuyển dụng, Candidate Database, and KPI & Reports as `FUTURE_HIDDEN`. Their absence from production Phase-1 navigation is therefore correct, not a product gap.

The candidate-facing portal is a separate required workflow surface and exists independently of the internal navigation list.

### Baseline runtime surface

| Surface | Canonical Phase-1 state | Baseline runtime evidence | DR-01 classification |
|---|---|---|---|
| Candidate portal | Required workflow | `/candidate` route with form-session, privacy, submission/edit and document workflow | IMPLEMENTED / REACHABLE |
| Phiếu ứng tuyển | PHASE1_RENDERED | `/` route loads Application Inbox and shell nav exposes Applications | IMPLEMENTED / REACHABLE |
| Interview | PHASE1_RENDERED | `/interviews` route and shell nav item | IMPLEMENTED / REACHABLE |
| Báo cáo phỏng vấn | PHASE1_RENDERED | `/reports` route and shell nav item | IMPLEMENTED / REACHABLE |
| Danh mục | PHASE1_RENDERED when authorized | No management route/nav item in baseline tree; S06-001 explicitly implements backend prerequisite for later UI and forbids building the management page | BACKEND CONTRACT ONLY / REQUIRED UI MISSING |
| Người dùng & Phân quyền | PHASE1_RENDERED when authorized | No management route/nav item in baseline tree; S06-002 explicitly implements backend/security prerequisite for later UI and forbids building the management page | BACKEND CONTRACT ONLY / REQUIRED UI MISSING |
| Dashboard | FUTURE_HIDDEN | Not rendered | CORRECTLY DEFERRED |
| Nhu cầu tuyển dụng | FUTURE_HIDDEN | Not rendered | CORRECTLY DEFERRED |
| Candidate Database | FUTURE_HIDDEN | Not rendered | CORRECTLY DEFERRED |
| KPI & Reports | FUTURE_HIDDEN | Not rendered | CORRECTLY DEFERRED |

### Root-admin reachability check

`web/src/components/shell/navigation.ts` defines exactly three default internal destinations: Applications, Interviews and Reports. `ROOT_ADMIN` receives that same three-item set. Therefore the two missing administration surfaces are not merely hidden from ordinary HR by permissions; they are absent from the baseline shell even for Root Admin.

### Slice-06 planning contradiction

`TASK-S06-001` is explicitly a shared-contract backend prerequisite. Its objective is a backend contract for a **later Master Data UI**, and its non-goals explicitly exclude the Master Data management page/table/drawer.

`TASK-S06-002` is explicitly a shared security/backend prerequisite for a **later Users & Permissions management UI**, and explicitly excludes building that management page.

The Slice-06 task set at the baseline contains those backend tasks but no later UI task, while `SLICE_REGISTRY.yaml` records:

`SLICE-06: {name: Master Data / Users & Permissions, status: DONE, current_task: TASK-S06-002}`

This creates a false-completeness risk: a planner that trusts slice `DONE` may never schedule the canonical user-facing completion work.

### Product-completeness conclusion

**Canonical Phase-1 user-facing scope is not complete at the baseline SHA.** The highest-confidence missing user-facing surfaces are:

- Master Data management UI;
- Users & Permissions management UI.

This is a HIGH planning/product-completeness issue, but not evidence that the accepted backend contracts should be rewritten. The likely recovery direction is to add focused UI tasks over the accepted S06 contracts, subject to DR-02 state-model repair and later architecture review.

### Boundaries deliberately not over-claimed in DR-01

DR-01 does not equate a visible button/page with production readiness. External email delivery, official PDF layout, malware scanning, deployment, connected Supabase state, backup/restore and release operations are classified later under DR-05.

Likewise, the official report PDF layout remains a separate concern from the implemented `/reports` web experience.

## Research rules

1. Do not infer DONE from slice labels alone; compare canonical product truth, task exclusions, runtime surface, and production behavior.
2. Do not recommend removing a security/control layer until its threat/consistency value is understood.
3. Separate product completeness, engineering quality, governance completeness, and production readiness; they are different dimensions.
4. Prefer exact repository evidence over historical chat summaries.
5. Write each completed DR unit into this file before starting the next one.
6. If Astra/OMP is invoked, provide this file plus a minimal exact-SHA source set so the reviewer can independently challenge the conclusions rather than inherit them as assumptions.

## Next unit

`DR-02 — slice/task state machine and planning-state correctness`

Split into small checkpoints:

- `DR-02A` — reconstruct the current state machine from Slice Registry, Task Registry, Autonomy Run State and Current State without judging it yet.
- `DR-02B` — compare those states with canonical product/runtime truth; identify false completeness, stale pointers, ambiguous DONE semantics or planner blind spots.

Only after DR-02B should the research recommend how the control-plane completion model should change.
