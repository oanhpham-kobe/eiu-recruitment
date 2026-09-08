# TASK-S05-001 — Interviewer Report Experience over Accepted Report Contracts

## Status
REPAIRED AFTER OMP PROMPT REVIEW / REQUIRES INDEPENDENT OMP RE-REVIEW BEFORE MATERIALIZATION OR DISPATCH

## Objective
Implement the first Slice-05 production vertical slice for an Interviewer to discover eligible interview-report records, open the current/historical rounds they are contextually allowed to read, create or edit only their own report on the current writable round, and view the shared current-round preview — strictly over the already accepted Slice-04 report/interview contracts.

This task MUST NOT recreate, fork, or silently supersede accepted Slice-04 mutation/schema behavior. Minimal additive read-only projection work is permitted only where the accepted backend does not yet expose the canonical Interviewer contextual read contract described below.

## Canonical sources
- `recruitment_webapp/review_pack/06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md`
- `recruitment_webapp/review_pack/02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
- `recruitment_webapp/design_system/RESPONSIVE.md`
- `recruitment_webapp/design_system/I18N.md`
- Full Handover v1.18 / Business Logic v1.2 FROZEN / Technical Architecture v1.18 FROZEN
- Design System v1.8 CURRENT and accepted DS production primitives

## Accepted implementation prerequisites
Consume the accepted Slice-04 contracts, especially:
- `TASK-S04-002` — report schema, lifecycle/report mutations, participant/report history and derived views;
- `TASK-S04-005` — participant public-contract repair;
- `TASK-S04-004` — accepted Interview UI/read-model conventions;
- `TASK-DS-006` — production responsive/accessibility foundation.

Do not alter accepted trusted-command mutation semantics unless a concrete source/implementation contradiction is proven and escalated through the source-reconciliation rule.

### Additive contextual read-model allowance
Canonical Slice-05 Interviewer reads may require a minimal additive read-only projection/RPC/server adapter because existing HR-oriented reads such as `loadInterviewPage` require HR-only `interviews.view`, while Interviewer access is contextual.

Such additive read work is explicitly permitted when necessary, but it MUST:
- preserve accepted Slice-04 mutation/RPC semantics rather than replace or fork them;
- authorize from the authenticated active internal caller and the exact canonical contextual predicates;
- derive Current Round server-side from the accepted authoritative Current Round contract, never from client guesses;
- return only the minimum Interviewer-safe DTO needed for discovery/detail/edit/preview;
- expose only permitted Application/Interview context, the caller's own editable report/version/base values, permitted participant snapshot data, safe display status, and shared current-round preview data;
- never grant Interviewers broad HR permission codes such as `interviews.view` or `reports.view`;
- never expose `hr_report_note`, HR owner identity/controls, `decision_updated_by`, technical final-source internals, private-schema rows, unrelated Candidate/Submission data, or another Interviewer's private edit state;
- keep browser direct business-table writes at zero;
- if implemented as a database RPC or SECURITY DEFINER helper, follow canonical fail-closed ACL/search-path/RLS security rules and focused adversarial tests.

A minimal additive contextual read projection is not considered forbidden Slice-04 mutation recreation.

## Required product behavior

### Interviewer read scope
An active internal user may read an Interview round only when all contextual predicates for that exact round are satisfied: parent Application access-active, Interview access-active, current participant row for the caller, `visible_to_interviewers = true`, and caller active. A newer current round must not erase read access to an older round that the interviewer actually participated in. Removing the participant revokes access to that round. No cross-round or cross-candidate transitive access.

### Interviewer-facing status projection
The raw target Interview `report_status_code` remains authoritative server-side for write authorization and business rules, but the Interviewer-facing UI MUST project the canonical eight raw states as follows:

| Raw HR Current Round status | Interviewer presentation |
|---|---|
| `INTERVIEW_SCHEDULING` | `INTERVIEW_SCHEDULING` |
| `AWAITING_INTERVIEW` | `AWAITING_INTERVIEW` |
| `WAITING_FOR_REPORT` | `WAITING_FOR_REPORT` |
| `REPORT_SUBMITTED` | `REPORT_SUBMITTED` |
| `FOLLOW_UP` | `REPORT_SUBMITTED` |
| `ON_HOLD` | `REPORT_SUBMITTED` |
| `HIRED` | `REPORT_SUBMITTED` |
| `REJECTED` | `REJECTED` |

Do not leak `FOLLOW_UP`, `ON_HOLD`, or `HIRED` as distinct Interviewer-facing lifecycle labels. `REJECTED` remains visible as Rejected. VI/EN labels must come from the canonical i18n/status copy and preserve the same mapping in both locales.

This presentation masking MUST NOT weaken write authorization: the server still evaluates the raw target-round status, so raw `HIRED` and `REJECTED` remain final/read-only even though Interviewer display masks `HIRED` as `REPORT_SUBMITTED`.

### Interviewer write scope
Create/edit is allowed only for the caller's own report and only when the target Interview is the Application's Current Round, caller is the current participant owner, caller is active, session is visible/access-active, and that Interview's own raw report status is non-final/writable. Raw `HIRED` and `REJECTED` are read-only until HR changes status back to a non-final state.

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

For the same Interviewer account in multiple tabs, stale conflicting save remains blocked as canonically defined; do not turn owner-wins into permission for stale same-account multi-tab overwrite.

### Preview and Final Decision Source
Shared preview uses Current Round only. Render active/current participants in `participant_order` with accepted name/title snapshots. Empty fields remain structurally renderable. Removed participants disappear from the current preview without deleting history.

Final Decision Source MUST follow the complete canonical rule:
- source candidates are only active/current reports belonging to current participants of the Current Round;
- a candidate report is eligible only when at least one of the three decision fields is non-blank: Conclusion, Expected Specific Job Assigned, Expected Recruitment Time;
- `decision_updated_at` and `decision_updated_by` change only when at least one of those three decision fields actually changes;
- edits only to qualitative evaluation fields (`Professional Knowledge`, `Necessary Skills`, `Qualities and Personality`, `Strengths and Limitations`, `Other`) MUST NOT change Final Decision Source ordering/metadata;
- select the eligible report ordered by `decision_updated_at DESC`, then deterministic `interview_report_id DESC` UUID tie-break;
- all three final-decision fields come atomically from that one selected report; never merge final-decision fields across Interviewers;
- if the current source clears all three decision fields, it becomes ineligible and the source falls back to the next most recent eligible report under the same ordering;
- if no eligible report remains, the shared final decision block is blank.

Interviewer must not see HR-only final-source metadata (`decision_updated_by`, source-selection internals), HR Note, HR owner controls, or another Interviewer's edit controls.

## UI / accessibility / responsive / i18n requirements
- Add/complete the Interviewer-facing `Báo cáo phỏng vấn` route using accepted internal navigation and shared production primitives rather than feature-local primitive duplication.
- Drawer/view combines Interview info + Report info for Interviewer, matching canonical role behavior.
- Before report: actions expose `Báo cáo PV`, `Xem`, and downstream-safe PDF affordance behavior only where implemented authority exists.
- After report: expose `Edit`, `Xem`, and downstream-safe PDF affordance behavior only where implemented authority exists.
- Focus containment, Escape dismissal, focus restoration, keyboard operation, semantic controls, accessible names/errors, and WCAG 2.2 AA behavior must follow the accepted DS foundation.
- Verify the canonical responsive matrix at 360, 390, 430, 768, 1024, and desktop reference width; additionally test constrained-height overlay/drawer behavior.
- Responsive presentation must preserve the same business workflow and actions across widths; do not create mobile-specific mutation semantics or hide business-critical actions.
- Support canonical `VI | EN`. Translate UI chrome/status/form labels/helpers/errors/empty/loading/preview labels, but do not auto-translate Interviewer-entered report content.
- Locale switching must preserve in-progress report draft values and applicable filter/search/page/tab/query state; changing language must not change the business timezone or Current Round context.
- Long VI/EN labels must remain legible without clipping or reducing operational text below Design System minimums.

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
- Preserve contextual Interviewer access semantics; do not grant Interviewer HR permission codes.
- `hr_report_note`, HR owner identity, technical Final Decision Source metadata, and unrelated Candidate/Submission data must be excluded at the server projection/RPC boundary, not merely hidden by UI.
- Safe read DTOs/projections must fail closed for inactive user, inactive Application, inactive Interview, removed participant, invisible session, or non-participated round.

## Verification
Impact-selected focused verification first, then normal task acceptance gates for changed domains.

At minimum verify:
1. contextual read: current + eligible historical round, participant removal, hidden session, inactive parent/interview/user, and no transitive cross-round/candidate read;
2. additive read DTO/RPC authorization if introduced: Interviewer positive path plus anonymous/Candidate/other-Interviewer/inactive-user denials; prove HR Note, HR owner identity, private technical metadata, unrelated Candidate/Submission data, and another Interviewer's private edit state are absent from the server-returned shape;
3. authoritative server Current Round derivation and no client-side round guess;
4. current-round-only create/edit and raw-final-status read-only behavior;
5. canonical eight-raw-state Interviewer status projection in both VI and EN, including `FOLLOW_UP`/`ON_HOLD`/`HIRED` => `REPORT_SUBMITTED` and `REJECTED` => `REJECTED`, while raw `HIRED` still blocks editing;
6. owner-only report editing and no cross-report mutation;
7. all eight optional fields, including all-blank and blank decision block cases;
8. field-aware concurrency with disjoint merge, same-field conflict behavior, and same-user stale multi-tab protection;
9. Final Decision Source eligibility, `decision_updated_at DESC` + `interview_report_id DESC` ordering, whole-block atomic selection, qualitative-only edit isolation, clear-all fallback, and no-eligible-source blank state;
10. participant-order/remove behavior in current preview;
11. absence of scoring/rating UI/data assumptions;
12. HR-only metadata absence from both Interviewer server DTO and UI;
13. keyboard/focus/a11y semantics and constrained-height overlay behavior;
14. responsive browser QA at 360, 390, 430, 768, 1024, desktop reference, plus constrained-height overlay checks;
15. bilingual VI/EN coverage for route labels, status labels, form labels/errors, empty/loading states and preview; locale switching preserves report drafts and applicable filter/search/page/tab/query state without translating user-entered report content;
16. lint, typecheck, production build, and affected automated tests;
17. directly crossed Slice-04 shared invariants only — do not rerun unrelated domains without impact evidence.

If implementation adds the explicitly permitted minimal contextual read projection/RPC, treat its authorization/privacy boundary as high-risk shared-contract work: prove necessity from canonical source, run focused database/security regressions (and clean migration replay if a migration is introduced), and require independent review before downstream consumption. This allowance does not authorize replacement of accepted Slice-04 mutation contracts.

## Producer / review lifecycle
Producer performs focused verification and exact-diff self-review, then presents an exact candidate SHA.

Independent OMP implementation review must evaluate the exact candidate SHA against this prompt, canonical source, accepted Slice-04 prerequisites, security/privacy/concurrency invariants, and directly affected shared contracts. `BLOCKING_REPAIR` findings receive minimal bounded repair plus targeted exact-SHA re-review. PASS then proceeds through serialized integration and exact-SHA CI under the active autonomy governance.

## Stop / escalation rules
Stop and return `OWNER_DECISION_REQUIRED` or source-reopen evidence if canonical authority cannot resolve a business/architecture/security/privacy/data-integrity ambiguity. Do not invent missing Product/Business/Design decisions.
