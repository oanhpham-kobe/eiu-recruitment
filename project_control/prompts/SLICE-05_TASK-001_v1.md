# TASK-S05-001 — Interviewer Report Experience over Accepted Report Contracts

## Status
PROPOSED / REQUIRES INDEPENDENT OMP PROMPT REVIEW BEFORE MATERIALIZATION OR DISPATCH

## Objective
Implement the first Slice-05 production vertical slice for an Interviewer to discover eligible interview-report records, open the current/historical rounds they are contextually allowed to read, create or edit only their own report on the current writable round, and view the shared current-round preview — strictly over the already accepted Slice-04 report/interview contracts.

This task MUST NOT recreate, fork, or silently supersede Slice-04 schema/RPC behavior.

## Canonical sources
- `recruitment_webapp/review_pack/06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md`
- `recruitment_webapp/review_pack/02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
- Full Handover v1.18 / Business Logic v1.2 FROZEN / Technical Architecture v1.18 FROZEN
- Design System v1.8 CURRENT and accepted DS production primitives

## Accepted implementation prerequisites
Consume the accepted Slice-04 contracts, especially:
- `TASK-S04-002` — report schema, lifecycle/report mutations, participant/report history and derived views;
- `TASK-S04-005` — participant public-contract repair;
- `TASK-S04-004` — accepted Interview UI/read-model conventions;
- `TASK-DS-006` — production responsive/accessibility foundation.

Do not alter accepted trusted-command semantics unless concrete source/implementation contradiction is proven and escalated through the source-reconciliation rule.

## Required product behavior
### Interviewer read scope
An active internal user may read an Interview round only when all contextual predicates for that exact round are satisfied: parent Application access-active, Interview access-active, current participant row for the caller, `visible_to_interviewers = true`, and caller active. A newer current round must not erase read access to an older round that the interviewer actually participated in. Removing the participant revokes access to that round. No cross-round or cross-candidate transitive access.

### Interviewer write scope
Create/edit is allowed only for the caller's own report and only when the target Interview is the Application's Current Round, caller is the current participant owner, caller is active, session is visible/access-active, and that Interview's own report status is non-final/writable. `HIRED` and `REJECTED` are read-only until HR changes status back to a non-final state.

### Form fields
No scoring, stars, ratings, numeric rubric, or invented evaluation scale.

All fields are optional:
- Professional Knowledge
- Necessary Skills
- Qualities and Personality
- Strengths and Limitations
- Other
- Conclusion
- Expected Specific Job Assigned
- Expected Recruitment Time

Blank final-decision fields are valid; do not add a conclusion-required invariant.

### Concurrency
Use the accepted field-aware report patch/merge contract. Requests carry expected version and base values for patched fields. Preserve authoritative server behavior: disjoint edits merge; same-field conflict policy follows the canonical HR/interviewer rules; no stale whole-row overwrite. Caller-owned idempotency identifiers are created once per user intent and reused on retry where the accepted command requires them.

### Preview
Shared preview uses Current Round only. Render active/current participants in participant order with accepted name/title snapshots. Empty fields remain structurally renderable. Removed participants disappear from the current preview without deleting history. Final Decision Source is the single eligible current-round report with latest valid decision timestamp and deterministic UUID tie-break; never merge the three final-decision fields across multiple reports.

Interviewer must not see HR-only final-source metadata (`decision_updated_by`, source-selection internals), HR Note, HR owner controls, or another interviewer's edit controls.

## UI / accessibility / responsive requirements
- Add/complete the Interviewer-facing `Báo cáo phỏng vấn` route using accepted internal navigation and shared production primitives rather than feature-local primitive duplication.
- Drawer/view combines Interview info + Report info for Interviewer, matching canonical role behavior.
- Before report: actions expose `Báo cáo PV`, `Xem`, and downstream-safe PDF affordance behavior only where implemented authority exists.
- After report: expose `Edit`, `Xem`, and downstream-safe PDF affordance behavior only where implemented authority exists.
- Focus containment, Escape dismissal, focus restoration, keyboard operation, semantic controls, accessible names/errors, and WCAG 2.2 AA behavior must follow the accepted DS foundation.
- Verify representative phone/tablet/desktop behavior; do not regress existing InternalAppShell/navigation.

## Explicit exclusions
- No HR aggregate Report page/drawer implementation in this task except shared code strictly required by the Interviewer vertical slice.
- No Report Status mutation UI for HR.
- No HR Report Note editing.
- No HR edit-other-interviewer flow.
- No report delete/inactivate UI.
- No email sending.
- No new scoring/rating model.
- No multi-round merged PDF.
- No official pixel-perfect PDF template invention or final integration. `OPEN_GAPS.md: ASSET-001` remains deferred until the PDF-template task is materialized and the Owner supplies the official template.
- No Vercel deployment and no connected Supabase migration application.

## Security / authorization invariants
- Browser performs zero direct business-table writes.
- Mutations flow through Next.js Server Actions / accepted server boundary and authoritative trusted commands.
- Do not expose service-role credentials.
- Backend/RLS/contextual authorization remains authoritative; hidden buttons are not security controls.
- Preserve `reports.view` and contextual Interviewer access semantics; do not grant Interviewer HR permission codes.

## Verification
Impact-selected focused verification first, then normal task acceptance gates for changed domains.

At minimum verify:
1. contextual read: current + eligible historical round, participant removal, hidden session, inactive parent/user;
2. current-round-only create/edit and final-status read-only behavior;
3. owner-only report editing and no cross-report mutation;
4. all eight optional fields, including all-blank and blank decision block cases;
5. field-aware concurrency with disjoint merge, same-field conflict behavior, and same-user stale multi-tab protection;
6. final-decision-source preview semantics and participant-order/remove behavior;
7. absence of scoring/rating UI/data assumptions;
8. HR-only metadata absence from Interviewer UI;
9. keyboard/focus/a11y semantics;
10. responsive browser QA at representative phone/tablet/desktop widths;
11. lint, typecheck, production build, and affected automated tests;
12. directly crossed Slice-04 shared invariants only — do not rerun unrelated domains without impact evidence.

If implementation changes database contracts despite the no-recreation rule, treat that as a high-risk shared-contract change: prove necessity from canonical source, run clean migration replay + focused DB regressions, and require independent review before downstream consumption.

## Producer / review lifecycle
Producer performs focused verification and exact-diff self-review, then presents an exact candidate SHA.

Independent OMP implementation review must evaluate the exact candidate SHA against this prompt, canonical source, accepted Slice-04 prerequisites, security/privacy/concurrency invariants, and directly affected shared contracts. `BLOCKING_REPAIR` findings receive minimal bounded repair plus targeted exact-SHA re-review. PASS then proceeds through serialized integration and exact-SHA CI under the active autonomy governance.

## Stop / escalation rules
Stop and return `OWNER_DECISION_REQUIRED` or source-reopen evidence if canonical authority cannot resolve a business/architecture/security/privacy/data-integrity ambiguity. Do not invent missing Product/Business/Design decisions.
