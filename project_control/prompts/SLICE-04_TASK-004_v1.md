# TASK-S04-004 — HR Interview Scheduling UI

## Goal
Implement the production HR Interview scheduling surface over the accepted Slice-04 trusted commands. This task is the UI/server seam only; it MUST NOT change existing SQL contracts, RLS, migrations, or command behavior.

## Canonical sources
- `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` §§3–15, especially §§4, 7, 9–13, 15 and canonical predicates.
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§1, 6–8.
- `recruitment_webapp/review_pack/command_registry.yaml` relevant Interview commands.
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`: AC-COPY-03, AC-PART-OPER-02..04, AC-SCH-SRC-01, AC-CRIT-QA-01.
- `recruitment_webapp/design_system/PAGE_OVERRIDES_V1_8.md` §Interview and the applicable table/accessibility standards.
- Accepted backend implementations: `supabase/migrations/20260906070000_interview_lifecycle_commands.sql` and `supabase/migrations/20260906080000_copy_interview_schedule.sql`.

## Required behavior
1. Add the authorized Interview page and navigation using existing app-shell patterns. Group rows by Application; show nested rounds; pagination unit is Application, not raw Interview. One expanded Application at a time is permitted.
2. Support Active / Inactive / All history filtering. Inactive latest rounds remain visible as `Vòng N — Không hoạt động` and expose only authorized Reactivate affordance.
3. Use explicit server-side wrappers for all reads and every mutation. The browser MUST NOT orchestrate multi-write behavior or own authorization. Derive actor permissions server-side; map only to existing trusted commands/RPCs.
4. Implement accessible dialogs/drawers for create-next-round, edit/save schedule, copy draft/save-copy, participant add/remove/re-add/reorder, schedule-status change, reschedule-confirmed, reactivate, and delete/inactivate where the accepted command exists.
5. Copy is a prefilled client draft only. Save Copy calls only `copy_interview_schedule`; requires source and target tokens, allows same/different Application selection, accepts editable logistics/participants, keeps Demo Topic blank, and renders structured conflict/stale/permission errors without raw SQL details.
6. Use the current server-returned state after each command. Disable duplicate submission while pending; preserve and send exact optimistic/idempotency tokens where required; do not optimistic-write business state.
7. Respect UI contract: `Ứng tuyển` means exact Submission selector, creation does not infer latest Submission; schedule status semantics, Confirmed edit restriction, format normalization feedback, participant ordering/snapshots, and conflict messages match source.
8. Preserve semantic HTML, labels, keyboard operation, focus restoration, visible focus, status text beyond color, accessible validation/error association, responsive table overflow behavior, and no PII search text in URL.

## Scope and non-goals
- Reuse current project components, server-action patterns, Supabase server clients, error/result conventions, and tests. Search before adding shared components/helpers.
- Do not create a generic state library, a generic modal framework, an alternate RPC abstraction, client-side authorization, direct browser database calls, email delivery UI, document upload UI, reports, master-data work, or unrelated refactors.
- Do not modify `recruitment_webapp/` authority sources or accepted Slice-04 SQL migrations/tests.

## Verification
- Add consumer-observable unit/component tests for command result/error handling, copy draft/save behavior, participant/order and status/restricted-control behavior.
- Run focused tests plus existing web lint/typecheck/build as appropriate.
- Run React Doctor on changed scope.
- Run browser QA against the actual local Interview surface: keyboard/dialog/focus behavior, same- and cross-Application Copy flows, an expected conflict, inactive filtering/reactivation affordance, and responsive overflow.
- Report exact SHA, changed paths, verification output, and any canonical contract blocker. Do not push, merge, deploy, or update project_control.
