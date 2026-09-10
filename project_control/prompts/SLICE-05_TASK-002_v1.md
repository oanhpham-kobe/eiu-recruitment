# TASK-S05-002 — HR Report Management Experience over Accepted Report Contracts

## Status
REPAIRED AFTER PRODUCER/SOURCE RECONCILIATION / REQUIRES INDEPENDENT OMP PROMPT REVIEW BEFORE TASK MATERIALIZATION OR DISPATCH

## Objective
Implement the Slice-05 HR Report Management vertical slice over the already accepted Interview/Report contracts. The HR experience must present one operational row per Application using the authoritative Current Round, expose the canonical HR-only Report drawer and controls, and route every mutation through trusted server/database commands.

This task MUST reuse accepted Slice-04 and TASK-S05-001 contracts where they are already correct. It MUST NOT widen the Interviewer-contextual read projection into an HR endpoint, duplicate Current Round or Final Decision Source logic, introduce browser table writes, or invent a second lifecycle command when a genuine accepted-contract/source mismatch should instead be repaired/reconciled.

## Canonical source authority
Read and reconcile at minimum:

### Product / business / permissions / security
- `recruitment_webapp/START_HERE.txt`
- `recruitment_webapp/review_pack/06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md`
- `recruitment_webapp/review_pack/02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
- `recruitment_webapp/review_pack/07_STATUS_AND_BUSINESS_RULES.md`
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
- `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md`
- `recruitment_webapp/review_pack/63_BATCH_OPERATION_SEMANTICS.md`
- `recruitment_webapp/review_pack/73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`
- `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
- Full Handover v1.18 / Business Logic Core v1.2 FROZEN / Technical Architecture v1.18 FROZEN.

### Design System v1.8 CURRENT
- `recruitment_webapp/design_system/00_README.md`
- `recruitment_webapp/design_system/MASTER.md`
- `recruitment_webapp/design_system/TABLE_LAYOUT.md`
- `recruitment_webapp/design_system/PAGE_OVERRIDES_V1_8.md`
- `recruitment_webapp/design_system/COMPONENTS.md`
- `recruitment_webapp/design_system/PATTERNS.md`
- `recruitment_webapp/design_system/ACCESSIBILITY.md`
- `recruitment_webapp/design_system/RESPONSIVE.md`
- `recruitment_webapp/design_system/I18N.md`

When source summaries conflict with executable accepted code, determine whether the difference is an accepted implementation detail or a genuine canonical mismatch. Repair only mismatches that this prompt explicitly reconciles or that independent review proves must be reconciled; otherwise preserve accepted behavior.

## Accepted implementation prerequisites
Consume, do not recreate, the accepted contracts from:
- `TASK-S04-002` — Interview report schema, report/status/note lifecycle commands, Current Round and Final Decision Source authorities, report/document persistence and field-aware concurrency foundation;
- `TASK-S04-005` — accepted participant/public-contract repairs;
- `TASK-S04-004` — accepted HR Interview UI/read-model and server-boundary conventions;
- `TASK-DS-006` — accepted production responsive/accessibility Design System foundation;
- `TASK-S05-001` — accepted Interviewer report contextual read projection and owner-only report mutation boundary.

In particular, preserve accepted `private.application_current_interview`, `private.interview_final_decision_source`, accepted report field/version behavior, and `save_interviewer_report`/`save_own_interviewer_report` semantics unless concrete canonical evidence proves a bounded repair is required.

## Mandatory source/accepted-tree reconciliation
The accepted integration tree currently has three known backend gaps/mismatches that are in scope for S05-002. They are not permission to invent alternative client behavior.

### 1. `set_report_visibility` — missing trusted command
Canonical authority requires:
- action: Hide/Show Interviewer visibility for the Current Interview/Current Round used by the HR Report aggregate;
- permission dependency: `reports.visibility + reports.view` (Root implicit);
- input includes exact target Interview, desired boolean visibility, and optimistic expected version;
- authoritative mutation updates `interviews.visible_to_interviewers` through one trusted transactional command;
- authenticated active internal actor resolution, fail-closed authorization, optimistic concurrency, audit, explicit ACLs and `search_path = ''` are required.

The accepted backend tree does not currently expose this command. Implement the missing trusted command (or a source-equivalent bounded repair) before wiring the UI. Do not implement visibility through direct browser `.from(...).update(...)`, Server Action table DML that bypasses the trusted command contract, or a client-only hidden-row illusion.

Visibility changes access only; they do not delete participants, reports, history, or PDF data. Hidden Current Round participants lose contextual Interviewer access; showing it again restores eligible access under the normal contextual predicates.

### 2. `bulk_change_report_status` — missing Phase-1 ALL_OR_NOTHING command
Canonical authority requires a visible HR bulk Report Status action:
- selected entities are exact Current-Round Interview IDs with aligned expected versions;
- each selected record requires `reports.manage_status + reports.view` (Root implicit through permission dependency rules);
- input is bounded to at most **100 selected items**; larger requests fail with `VALIDATION_ERROR`;
- target IDs are sorted deterministically (`ORDER BY id ASC` or equivalent stable ascending UUID ordering) before row-lock acquisition;
- re-resolve and revalidate Current Round + expected version for the full selected set under lock;
- semantics are the same authoritative semantics as `change_report_status`;
- one invalid/ineligible/stale/unauthorized selected item aborts the whole batch;
- every affected parent Submission is recalculated before commit;
- no partial status writes, partial Submission outcome recalculation, or per-item client mutation loop is allowed;
- deterministic parent/current-round locking and stable validation/recheck must prevent deadlocks and race-created partial behavior;
- audit must truthfully describe the batch and affected records.

The accepted backend tree does not currently expose this command. Add the canonical bulk command or refactor to a shared private status core only if doing so preserves `change_report_status` as the single public single-record writer semantics. Do not fake ALL_OR_NOTHING by issuing multiple independent `change_report_status` RPCs from the browser/server adapter.

### 3. `delete_or_inactivate_report` — accepted permission mismatch
The accepted command exists, but its current actor path is rooted in `reports.manage_status` and then separately checks `reports.view`.

Canonical permission authority for a concrete participant report delete/inactivate action is:

`reports.delete + reports.view`

Repair the existing accepted command permission path to the canonical dependency. Do not introduce a second delete/inactivate command and do not silently preserve `reports.manage_status` as the action permission.

Preserve the accepted command's report-specific usage/history hard-delete-vs-inactivate semantics, optimistic version behavior, audit and downstream guards unless canonical evidence identifies a separate contradiction.

## HR Report read model — dedicated minimum-safe projection
Do NOT widen or repurpose `get_interviewer_report_page` / `interviewer_report_private.get_interviewer_report_page_impl()`.

TASK-S05-001 is deliberately Interviewer-contextual and privacy-bounded. S05-002 requires a separate HR Report projection/DTO appropriate to `reports.view` and Root implicit access.

The HR read contract must be server-authoritative and minimum-safe:
- authenticated active internal actor;
- Root OR `reports.view` for page/read access;
- one main row per **Application**;
- the row exists only when the accepted authoritative Current Round resolves for that Application; Current Round is the highest `round_no` among `access_active` Interviews (`Application.is_active AND Interview.is_active`);
- the Report page must **never fall back to an inactive historical Interview** merely because the Application has Interview history; historical rounds remain history/detail only;
- the source rule that an Application needs Interview history is necessary but does not authorize fabricating a Current Round when no `access_active` Interview exists;
- row derives from the accepted Current Round authority, never a client-side `max(round_no)` guess;
- server-side pagination is by Application group, not raw Interview/report rows;
- stable sorting includes a deterministic ID tie-breaker;
- row DTO supports the canonical table fields: Candidate name, Position, Interview time, Location, current Report Status, HR Report Note and row/action identity/version data required for safe interaction;
- include Current Round visibility state for the HR visibility filter/control;
- aggregate drawer may additionally return the HR-owned data canonically required for that exact Application/Current Round: Report Status, Application HR owner display identity, HR Report Note, visibility, current participant report list in participant order, current Final Decision Source/metadata allowed to HR, last-updated metadata and safe link identifiers for `Xem thông tin phỏng vấn`;
- HR Final Decision Source may include `decision_updated_by` / `decision_updated_at` and source identity needed for the HR-only source display, but do not expose unrelated private-schema rows or raw technical internals beyond the minimum DTO;
- do not expose Candidate/Submission data unrelated to the Report page merely because HR has other permissions elsewhere;
- read authorization must not be delegated to navigation visibility or frontend hiding.

If implemented as a database RPC / privileged helper, follow the accepted security pattern: explicit schema/function ACLs, qualified object names, `search_path = ''`, active actor checks, minimum allowlisted DTO, RLS/permission-safe behavior and adversarial tests. If an invoker wrapper delegates to a privileged helper, preserve the S05-001 principle that the privileged implementation is not broadly exposed as a generic data surface.

## Required HR product behavior

### Main table
The HR Report page shows exactly one main row per Application with an authoritative Current Round. Historical rounds remain history/detail data; they do not become duplicate main rows or fallback aggregate rows.

Canonical columns and order come from Design System `TABLE_LAYOUT.md`:

`Select | Họ và tên | Vị trí | Thời gian phỏng vấn | Địa điểm | Trạng thái | Ghi chú | Action`

Hard design geometry:
- semantic `<table>` + `<colgroup>` + `table-layout: fixed`;
- exact HR Report desktop min-width `1610px`;
- widths: `48 | 240 | 300 | 240 | 200 | 190 | 300 | 92` px;
- table horizontal scroll is contained inside its own scroller; header/toolbar stay outside that horizontal scroller;
- sticky context columns = Select + Họ và tên;
- table/header/body/status typography follows DS v1.8 and is never reduced below the approved operational minimum merely to fit;
- important business text wraps; generic `overflow-wrap:anywhere` is not the default for normal cells.

### Filters / search / pagination
At minimum support the source-backed HR visibility filter:
- Tất cả / All;
- Đang hiển thị / Visible;
- Đang ẩn / Hidden.

Support Report Status filtering/search/pagination patterns as required by the accepted page conventions. Server-side pagination is by Application.

URL/state rules:
- page/sort/status/visibility and other non-sensitive filters may be URL state where useful;
- Candidate name/email/phone or other PII search text MUST NOT be serialized into shareable URL query parameters;
- locale switching preserves route, page/filter/sort/selection where safe and any open unsaved form state.

### HR drawer
The HR Report aggregate drawer contains **Report data only; it does not repeat Interview data**.

Canonical aggregate actions, permission-gated independently:
- Edit HR Note / Report management action(s) under the corresponding permissions;
- Change Report Status (`reports.manage_status + reports.view`);
- Hide/Show Interviewer (`reports.visibility + reports.view`);
- Xem / View;
- PDF affordance only within the PDF boundary below;
- link `Xem thông tin phỏng vấn` / equivalent to the Interview module.

The aggregate drawer MUST NOT expose a generic `Xóa` / Delete action.

Delete/Inactive appears only next to a concrete participant `interview_report_id`, and only when the caller has `reports.delete + reports.view`.

Drawer content includes:
- Current Round Report Status;
- Application-owned HR responsible display value (ownership changes remain `applications.manage`, not a Report mutation);
- HR Report Note;
- Current Round visibility;
- current participant reports;
- HR-only current Final Decision Source information;
- latest update metadata;
- Interview information link.

If the caller has `reports.edit_interviewer + reports.view`, each concrete Interviewer report may expose Edit. Reuse the accepted `save_interviewer_report` field-aware HR mutation; do not use the S05-001 owner-only command for HR editing.

### Report Status
HR sees the canonical raw eight Current Round states without Interviewer masking:
- `INTERVIEW_SCHEDULING`
- `AWAITING_INTERVIEW`
- `WAITING_FOR_REPORT`
- `REPORT_SUBMITTED`
- `FOLLOW_UP`
- `ON_HOLD`
- `HIRED`
- `REJECTED`

HR changes status manually; do not invent a forced sequence. `change_report_status` remains the single-record trusted writer and must recalculate the parent Submission in the same transaction. `update_hr_report_note` remains note-only and never changes status/outcome.

New Current Round behavior, Application outcome derivation, and Submission recalculation remain accepted Slice-04 authority and must not be re-derived in the browser.

### Single + bulk status UX
Design System requires one toolbar `Status` dropdown for selected rows. Authorized row status badges may open the same StatusMenu/validation path for single-row changes; read-only badges are not interactive.

For HR Report responsive behavior:
- row status badge uses the approved 144px benchmark width; long English labels wrap inside the badge rather than stretching the cell;
- row menu is anchored to the trigger element bounds, never raw pointer coordinates;
- selection, outside interaction, Escape and same-trigger toggle dismiss it;
- Escape restores focus to the trigger;
- the toolbar and row entry points must converge on the same business semantics, not separate mutation implementations.

Bulk selection shows a selected-count state and must report blocking records/errors without implying partial success when the backend transaction aborts. UI selection must respect the canonical 100-item server batch bound rather than silently chunking one user intent into multiple independently committed transactions.

### HR Report Note
Reuse `update_hr_report_note` and its accepted optimistic trusted-command behavior. HR Note is HR-only and must never leak into the Interviewer DTO/UI. Status and note remain separate mutations.

### HR editing an Interviewer report
Only `reports.edit_interviewer + reports.view` allows this action (Root implicit). Reuse accepted field-aware patch/merge behavior:
- request carries expected version + base values for patched fields;
- HR same-field stale conflict -> `STALE_VERSION` / reload;
- disjoint field edits preserve both changes;
- HR vs Interviewer same-field semantics remain Interviewer-preferred as accepted;
- HR-to-HR stale save blocks;
- do not perform stale whole-row overwrite.

The qualitative/final-decision report fields remain exactly the accepted eight text fields. No scoring/rating/stars/points/percentage model may be added.

### Final Decision Source
Reuse the accepted Current Round Final Decision Source authority. Do not create a second source algorithm.

The HR drawer may display the HR-permitted source identity/update metadata and the whole final-decision block. Preserve all accepted invariants:
- only active/current reports of current participants in Current Round are source candidates;
- eligible source has at least one non-blank decision field;
- order by decision timestamp descending then deterministic report UUID tie-break;
- all three decision fields come atomically from one source report;
- qualitative-only edits do not change decision source metadata;
- clearing all decision fields makes that report ineligible and falls back to the next eligible source;
- no eligible source -> blank block.

### Visibility
Visibility belongs to the Current Interview Session, not to an individual report row. Hide/Show applies to the Current Round used by the aggregate.

The UI may hide/show the action based on permission, but backend `set_report_visibility` remains authoritative. A visibility mutation must not alter Report Status, HR Note, participants, report records, Final Decision Source, Application outcome or Submission status.

### Delete / Inactive
Only a concrete participant report can be deleted/inactivated. Use the repaired existing `delete_or_inactivate_report` command.

- no aggregate-level Delete;
- permission = `reports.delete + reports.view`;
- optimistic expected version;
- preserve canonical unused-vs-used lifecycle classification/history retention;
- do not treat deleting/inactivating an Interview Session as a Report action.

## Navigation and permission presentation
The Phase-1 HR sidebar item `Báo cáo phỏng vấn` is rendered when the user has the corresponding page permission according to accepted permission-aware navigation. Presentation is not authorization.

A limited HR user with only `reports.view` may read the page/drawer but must not receive mutation controls they lack. Each mutation still independently validates its exact action permission + view prerequisite on the server.

## Design System / accessibility / responsive / i18n requirements
Use accepted production primitives rather than feature-local copies where they exist.

### Interaction / layout
- Institutional enterprise / clean productivity direction; preserve readable data and operational context.
- Sticky Page Header -> Sticky Action Toolbar -> content -> horizontal table scroller.
- Detail Drawer uses accepted `DetailDrawer` behavior: sticky header, scrollable body, sticky footer where editing requires it; desktop preferred 820px bounded by available content width; responsive full-screen/sheet behavior below the breakpoint.
- Nested interactive controls stop row-open/expand behavior.
- destructive report-specific Delete/Inactive uses an explicit confirmation describing the consequence.

### Accessibility
- semantic controls before ARIA simulation;
- visible `focus-visible` for all controls including sticky columns;
- table remains semantic;
- clickable StatusBadge has an accessible change-status name/state; read-only badge is not exposed as a button;
- Drawer/Modal/status menu focus containment/return is correct; mobile backgrounds are inert/semantically hidden while overlays are active;
- Escape dismissal and focus restoration are verified;
- persistent labels, connected validation errors and accessible async status/error feedback;
- warn/protect unsaved long-form edits where closing/navigating would discard them;
- status meaning never relies on color alone;
- 200% text zoom preserves content/functionality; 400% reflow is verified where applicable, with wide semantic tables retaining the allowed two-dimensional-scroll exception;
- automated axe checks supplement, not replace, manual keyboard/screen-reader sanity checks.

### Responsive
Representative production QA widths:
`360, 390, 430, 768, 1024, desktop reference (1280–1440+)`, plus constrained-height overlay checks.

Internal HR remains desktop-first, but the accepted responsive UAT rules are normative:
- dense tablet tables may retain contained horizontal scrolling;
- mobile may use a source-permitted structured summary only if comparison/action reachability is preserved;
- no business-critical action disappears merely because width is narrow;
- drawer/nav becomes accessible sheet/full-screen behavior as appropriate;
- responsive presentation never creates a second business workflow or mutation semantics.

### I18N
Support canonical `VI | EN`, default VI.
Translate all system UI: page/title/actions/table/filter/status/drawer/form/confirmation/error/loading/empty/preview chrome. Do not auto-translate HR Note, Interviewer-entered report text or other user-entered business content.

Locale switch:
- preserves route/filter/page/sort/selection and unsaved edits where safe;
- updates document language and locale-aware date/number presentation;
- does not change the business timezone (`Asia/Ho_Chi_Minh`);
- does not clip long VI/EN labels or reduce operational text to fit.

## Security / authorization invariants
- Browser performs zero direct business-table writes for Report management.
- Trusted mutation stays server/database authoritative.
- No service-role/secret credentials in browser code.
- Resolve authenticated active internal actor server-side; inactive/unknown actors fail closed.
- RLS remains enabled for exposed business tables; privileged functions do not use RLS bypass as a substitute for authorization.
- `SECURITY DEFINER` functions use `search_path = ''`, qualified object names and explicit grants/revokes.
- Permission dependencies are backend-enforced, not only UI-disabled.
- Minimum-safe DTOs prevent accidental cross-module data exposure.
- Optimistic/field-aware concurrency remains authoritative.
- Multi-row/bulk commands use deterministic locking, bounded input and atomic rollback.
- Audit/security audit records reflect the actual actor/action/entity and do not log unnecessary sensitive business content.

## PDF boundary / ASSET-001
`ASSET-001` remains unresolved and non-blocking for ordinary Report management.

Do not invent a pixel-perfect official Report PDF template, dimensions, typography or branded layout. Do not merge multiple rounds into one PDF.

The current Report/PDF concept remains Current-Round-only. An on-screen Download PDF affordance may be retained/wired only if an already accepted safe downstream implementation exists and doing so does not pretend official-template acceptance. Otherwise render a truthful disabled/deferred state consistent with the product source. Official template integration remains a later Owner-asset-gated task.

## Explicit exclusions
- No rewrite/reimplementation of the Interviewer Report page accepted in TASK-S05-001.
- No widening of `get_interviewer_report_page` for HR.
- No new Interview Report schema or scoring model.
- No recreation of Current Round, Application outcome or Final Decision Source authority.
- No change to Application HR ownership from the Report module; owner change remains `applications.manage`.
- No Interview scheduling/participant/document management except read/link context required by this page.
- No multi-round merged PDF and no invented official PDF template.
- No email sending/attachments implementation in this task.
- No production Vercel deployment.
- No connected Supabase DEV/production migration application without explicit Owner authorization.
- No merge/push to `main`.

## Required verification
Use impact-selected focused verification first, then normal changed-domain acceptance gates. At minimum prove:

1. HR read projection: anonymous/Candidate/Interviewer/unauthorized/internal-inactive denial; Root and `reports.view` positive path; minimum-safe DTO and no unrelated cross-module leakage.
2. Grouping: one main row per Application with an authoritative Current Round; no fallback to inactive historical rounds; no duplicate historical-round rows; stable deterministic pagination by Application.
3. HR table/design contract: exact columns/order/1610px min-width/colgroup, sticky Select + Name, horizontal-scroll containment, 16px operational typography, wrapping and loading/empty geometry.
4. Report Status single mutation: all eight raw HR states, manual/flexible transition behavior, Current Round restriction, optimistic stale rejection, parent Submission recalculation and audit.
5. `bulk_change_report_status`: exact Current-Round IDs + expected versions, maximum 100 items, deterministic ascending target locking, full-set Current Round re-resolution, `reports.manage_status + reports.view` for all, ALL_OR_NOTHING rollback, no partial derived-status changes, affected Submission recalculation, adversarial stale/unauthorized/mixed-validity/race cases.
6. `set_report_visibility`: exact Current Round target, `reports.visibility + reports.view`, optimistic concurrency, audit, hide revokes eligible Interviewer contextual access, show restores it, and no unrelated status/note/report/outcome mutation.
7. `delete_or_inactivate_report` permission repair: `reports.delete + reports.view`; prove `reports.manage_status` alone is insufficient; preserve report-specific lifecycle semantics and aggregate drawer has no Delete.
8. HR Report Note: separate note-only command, `reports.manage_status + reports.view`, HR-only confidentiality, no status/outcome side effect.
9. HR edit Interviewer report: `reports.edit_interviewer + reports.view`, accepted field-aware concurrency, HR stale/same-field rejection, disjoint merge, no stale whole-row overwrite.
10. Final Decision Source: accepted eligibility/order/atomic whole-block/fallback behavior remains unchanged; HR sees allowed source metadata while Interviewer privacy remains unchanged.
11. Limited-HR action matrix: view-only HR gets read UI only; each action control and backend denial matches exact permissions; navigation hiding is never treated as security.
12. Search/filter/state: visibility filter; status/filter/page behavior; PII search absent from URL; locale switch preserves non-sensitive state and unsaved edits.
13. Status UX: toolbar single Status dropdown + authorized row badge using one semantic path; 144px badge benchmark, anchored menu, same-trigger/outside/selection/Escape dismissal and focus restoration.
14. Drawer/modal/destructive confirmation keyboard/focus behavior, background inertness for responsive sheets, unsaved-change protection, accessible async errors/status.
15. Responsive QA at 360/390/430/768/1024/desktop + constrained-height overlays; no hidden business-critical actions and no duplicated mobile mutation path.
16. VI/EN coverage for all system chrome/status/filter/drawer/error/loading/empty states; user-entered report/note text remains untranslated; timezone unchanged.
17. Security regression for every new/modified RPC/helper: ACLs, `search_path = ''`, qualified references, active actor checks, RLS expectations and no browser/service-role credential leak.
18. Clean local migration replay if SQL migration(s) are added; focused Supabase/database tests for permission/RLS/locking/concurrency; no connected migration application.
19. lint, typecheck, production build, affected automated tests, accessibility checks and directly crossed shared-contract regressions.
20. exact diff/source integrity review proving no TASK-S05-001 reopening, no unrelated source changes, no main mutation/deployment/connected migration.

## Producer / review lifecycle
Before implementation is materialized or dispatched:
1. Coordinator/producer performs source reconciliation of this exact prompt against the fixed integration baseline and accepted implementation;
2. exact prompt-review target is persisted;
3. independent OMP prompt/source reconciliation review evaluates the exact target;
4. required verdict is `PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`, with explicit `SOURCE_REOPEN_REQUIRED: true|false`;
5. only `PASS` with `SOURCE_REOPEN_REQUIRED: false` releases TASK-S05-002 materialization/dispatch.

After implementation:
- producer performs focused verification + exact-diff self-review and presents an exact candidate SHA;
- independent OMP implementation review is mandatory on that exact candidate SHA;
- blocking findings receive the smallest bounded repair + targeted exact-SHA re-review;
- accepted candidate is serialized into integration;
- if integration SHA differs, perform targeted exact-SHA integration-equivalence/final acceptance review;
- run exact-SHA Integration CI + Governance CI;
- on PASS create immutable accepted checkpoint;
- persist POST-CI bookkeeping and continue AUTONOMOUS outer loop.

If OMP is not directly invokable from the Coordinator runtime, governance requires truthful `WAITING_EXTERNAL_REVIEW` state plus a complete copy-ready Owner transport package before yielding. The handoff package is transport material, not review evidence.

## Stop / escalation rules
Return `OWNER_DECISION_REQUIRED` only when canonical Product/Business/Design/Technical authority cannot resolve a material business, security, privacy, architecture or data-integrity ambiguity.

A proven accepted-code/source contradiction with clear canonical resolution (including the three known reconciliations above) is a bounded implementation repair, not automatically a source reopen.

Do not invent missing product/design decisions. Do not cross the explicit main/deployment/connected-migration boundaries.
