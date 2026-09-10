# S05-002 Independent Prompt / Source Reconciliation Review

WORK_ID: S05-002-PROMPT-REVIEW-001

REVIEWED_REPOSITORY: oanhpham-kobe/eiu-recruitment

REVIEWED_BRANCH: autonomy/continuous-integration-20260905-01

REVIEWED_SHA: 1f831a767906e4322e0fc2370d593b5c51e323d5

REVIEWED_TARGET: project_control/prompts/SLICE-05_TASK-002_v1.md

REVIEW_TYPE: INDEPENDENT_PRE_IMPLEMENTATION_PROMPT_SOURCE_RECONCILIATION

VERDICT: PASS

SOURCE_REOPEN_REQUIRED: false

## Exact-target and baseline verification

- Reviewed the prompt from commit `1f831a767906e4322e0fc2370d593b5c51e323d5`, tree `151b0093eb7724d8e85798dc912fa11701c7a261`; not a mutable working-tree copy.
- The exact prompt file is byte-equivalent at integration HEAD `605f8a79196c6af55ac75e54c072b457d526f4c4`. The reviewed prompt is an ancestor of that control-plane head; later changes are control-plane state/evidence only.
- `origin/checkpoint/S05-001-accepted-001` resolves to accepted SHA `ef0bd9e534dec0cc85ef6503fbe0369eda56d555`.
- Durable accepted review references resolve to `03ea6eb5417023e52f54edf4e863b7e585bea975` (R6 implementation evidence) and `c1b9eaed5b314ce9f64cbe2301494b04922ab57e` (final integration-equivalence evidence).

## BLOCKING_FINDINGS

NONE

## NON_BLOCKING_OBSERVATIONS

NONE

## Accepted contract reuse assessment

### Current Round

PASS. The prompt binds its HR read model to `private.application_current_interview`, defines Current Round as highest `round_no` over `access_active` (`Application.is_active AND Interview.is_active`), requires Application-group pagination and deterministic sorting, and expressly forbids inactive historical fallback. This matches the normative predicate source (`73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`) and accepted view in `20260906060000_interview_schema_and_conflict_locking.sql`.

### Final Decision Source

PASS. The prompt preserves `private.interview_final_decision_source`: current, active, unarchived report of a current participant; one nonblank decision field; `decision_updated_at DESC, interview_report_id DESC`; all three decision fields from one selected report; and fallback when the selected source becomes ineligible. It prohibits a replacement algorithm and preserves the rule that qualitative edits do not move decision metadata.

### Report schema and lifecycle

PASS. The prompt retains the eight qualitative/final-decision text fields and prohibits scoring, rating, stars, points and percentages. It retains `change_report_status` as the only single-record status writer, mandates same-transaction parent Submission recalculation, and keeps `update_hr_report_note` separate, HR-only and outcome-neutral.

### Field-aware concurrency

PASS. HR edit-other-interviewer behavior must reuse accepted `save_interviewer_report`, not owner-only `save_own_interviewer_report`; expected version/base-value patching, disjoint merge, HR same-field stale rejection, HR-to-HR stale rejection, and accepted Interviewer-wins same-field semantics are all explicit. Whole-row stale overwrite is forbidden.

### S05-001 Interviewer privacy/read projection

PASS. The prompt forbids widening `public.get_interviewer_report_page` and `interviewer_report_private.get_interviewer_report_page_impl()`. It requires a distinct HR projection with active internal actor plus Root or `reports.view` authorization and an allowlisted HR DTO. It retains the interviewer contextual predicate and excludes HR Note/source metadata from interviewer surfaces.

### Existing trusted commands and known bounded repairs

PASS. Direct accepted SQL confirms the prompt's three reconciliation items:

1. `set_report_visibility` is canonically required but absent from the accepted backend. The prompt requires one trusted optimistic/audited command with `reports.visibility + reports.view`, active actor resolution, fail-closed authorization, explicit ACLs, qualified references and `search_path = ''`; it forbids browser DML, Server Action table DML, and client-only visibility.
2. `bulk_change_report_status` is canonically required but absent from the accepted backend. The prompt requires exact Current-Round Interview IDs and aligned versions, a 100-item `VALIDATION_ERROR` bound, stable ascending lock order, full-set lock/re-resolution/revalidation, all-or-nothing rollback, per-parent Submission recalculation before commit, truthful auditing, and no client/server loop over single-row commands. It permits a shared private status core only while retaining `change_report_status` as authoritative single-row semantics.
3. Accepted `delete_or_inactivate_report` starts with `private.interview_command_actor('reports.manage_status')`, although canonical command coverage requires `reports.delete + reports.view`. The prompt correctly repairs that existing command instead of adding a competitor and preserves report-specific hard-delete/inactivate history semantics.

## Design system assessment

### HR Report table geometry

PASS. The prompt requires the authoritative semantic `<table>` with `<colgroup>` and fixed layout, desktop minimum width `1610px`, exact widths `48 | 240 | 300 | 240 | 200 | 190 | 300 | 92`, contained horizontal scrolling, and sticky `Select + Họ và tên` context columns. It preserves the approved operational >=16px scale, readable wrapping, and the rule against generic `overflow-wrap:anywhere`.

### Toolbar and status controls

PASS. The prompt requires exactly one toolbar Status dropdown, an authorized row badge using the same validation/business path, noninteractive read-only badges, the 144px badge benchmark with wrapped long English labels, trigger-bound menu placement, and selection/outside/Escape/same-trigger dismissal with Escape focus restoration.

### Aggregate drawer and delete boundary

PASS. The prompt requires Report-only aggregate data, excludes generic Delete, and permits Delete/Inactive only against a concrete `interview_report_id` under `reports.delete + reports.view`. Application HR ownership remains an `applications.manage` concern.

### Accessibility, responsive behavior and VI/EN

PASS. The prompt preserves native semantic controls, visible focus, focus containment/restoration, background inertness for responsive overlays, accessible status/error feedback, destructive confirmation, unsaved-edit protection, text-plus-color status meaning, 200% zoom/400% reflow rules, axe plus manual keyboard/screen-reader checks, the required `360/390/430/768/1024/desktop` and constrained-height QA, and state-preserving `VI | EN`. It translates system chrome while leaving HR Note and Interviewer-entered report content untranslated and retains the `Asia/Ho_Chi_Minh` business timezone.

## Security assessment

### Actor and authorization

PASS. Page/read, every mutation, and Limited-HR action behavior require independent server-side active actor and exact permission checks. Navigation/control visibility is stated to be presentation only.

### RLS, ACL and DTO boundary

PASS. The prompt preserves RLS, requires explicit function/schema ACLs, qualified references and `search_path = ''` for privileged code, prohibits public/anon exposure, requires minimum-safe DTOs, and forbids broadening the interviewer private helper into an HR data surface.

### Trusted write and browser credential boundary

PASS. The prompt requires zero browser business-table writes, rejects direct Supabase table UPDATE and server-adapter direct table DML as substitutes, and forbids service-role/secret browser credentials.

### Bulk integrity and verification

PASS. The prompt specifies deterministic locking, lock-time full-set Current Round/version revalidation, bounded input, atomic rollback, no partial derived Submission status, adversarial stale/unauthorized/mixed-validity/race tests, and clean local migration replay if SQL is added. It expressly prohibits connected Supabase DEV/production migration application.

## Acceptance statement

This exact prompt at `1f831a767906e4322e0fc2370d593b5c51e323d5` can be released for TASK-S05-002 materialization and implementation. The three accepted-code/canonical-source reconciliations are bounded repairs with clear canonical resolutions; they do not reopen TASK-S05-001 or require Product source reopening. Implementation remains subject to the prompt's independent implementation review, exact-SHA integration-equivalence review when needed, and exact-SHA CI/governance gates.

## Independent reviewer corroboration

An `eiu-reviewer` worker was dispatched through OMP Agent Hub as `SlowPromptReviewer` for a bounded read-only reconciliation of the same exact prompt tree. It returned `PASS`, `SOURCE_REOPEN_REQUIRED: false`, and no blockers. This corroborates, but does not replace, the direct source and accepted-code evidence above.
