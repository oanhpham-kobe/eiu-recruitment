# TASK-S04-004 — HR Interview Scheduling UI (v3 Reconciled)

## Goal
Implement the production HR Interview scheduling surface over the accepted Slice-04 trusted commands. This task is the UI/server seam only; it MUST NOT change existing SQL contracts, RLS, migrations, or command behavior.

## Canonical sources
- `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` §§3–15, especially §§4, 7, 9–13, 15 and canonical predicates.
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§1, 6–8.
- `recruitment_webapp/review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md` for mutation retry, optimistic-version, schedule-resource lock, and participant concurrency semantics.
- `recruitment_webapp/review_pack/command_registry.yaml` relevant Application/Interview commands.
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`: AC-COPY-03, AC-PART-OPER-02..04, AC-SCH-SRC-01, AC-CRIT-QA-01 and the current acceptance IDs bound to application reactivation / participant operational eligibility.
- `recruitment_webapp/design_system/PAGE_OVERRIDES_V1_8.md` §Interview and the applicable table/accessibility standards.

## Accepted backend baseline and precedence
Consume the complete ordered accepted Slice-04 implementation chain relevant to this UI:
1. `supabase/migrations/20260906060000_interview_schema_and_conflict_locking.sql`
2. `supabase/migrations/20260906070000_interview_lifecycle_commands.sql`
3. `supabase/migrations/20260906080000_copy_interview_schedule.sql`
4. `supabase/migrations/20260906090000_application_reactivation_and_participant_contract_repair.sql`

For any function body or signature replaced by a later migration, the later ordered migration is the effective accepted public surface. In particular, the `20260906090000` migration supersedes removed participant overloads and adds the accepted `reactivate_application` contract. Do not call superseded overloads and do not reconstruct their semantics in the browser.

The accepted round-allocation command originates in the `20260906060000` migration:
- `create_next_interview_round(p_application_id uuid, p_idempotency_key uuid default null)`

Effective repaired participant surface:
- `add_interview_participant(p_interview_id uuid, p_app_user_id uuid, p_idempotency_key uuid)`
- `remove_interview_participant(p_interview_participant_id uuid, p_expected_version bigint)`
- `readd_interview_participant(p_interview_participant_id uuid, p_restore_mode text, p_idempotency_key uuid)`
- `reorder_interview_participants(p_interview_id uuid, p_ordered_participant_ids uuid[], p_expected_versions bigint[])`

`readd_interview_participant` supports only the accepted restore modes:
- `RESTORE_OLD_REPORT`
- `CREATE_NEW_REPORT`

Application reactivation uses:
- `reactivate_application(p_application_id uuid, p_expected_version bigint)`

Save Copy uses the accepted atomic command and exact optimistic/idempotency inputs from `20260906080000`:
- `copy_interview_schedule(p_source_interview_id uuid, p_target_application_id uuid, p_expected_source_version bigint, p_expected_target_application_version bigint, p_expected_target_round_id uuid, p_expected_target_round_version bigint, p_start_at timestamptz, p_end_at timestamptz, p_interview_format_id uuid, p_room_id uuid, p_meeting_link text, p_interview_note text, p_participant_app_user_ids uuid[], p_idempotency_key uuid)`

Keep application reactivation distinct from interview-round reactivation:
- inactive Application -> `reactivate_application`
- inactive Interview round -> `reactivate_interview`

## Required behavior
1. Add the authorized Interview page and navigation using existing app-shell patterns. Group rows by Application; show nested rounds; pagination unit is Application, not raw Interview. One expanded Application at a time is permitted.
2. Support Active / Inactive / All history filtering. Inactive latest rounds remain visible as `Vòng N — Không hoạt động` and expose only authorized Reactivate affordance. Inactive Applications use the accepted application reactivation command rather than a child-round mutation.
3. Use explicit server-side wrappers for all reads and every mutation. The browser MUST NOT orchestrate multi-write behavior or own authorization. Derive actor permissions server-side; map only to existing trusted commands/RPCs.
4. Implement accessible dialogs/drawers for create-next-round, edit/save schedule, copy draft/save-copy, participant add/remove/re-add/reorder, schedule-status change, reschedule-confirmed, application reactivate, interview reactivate, and delete/inactivate where the accepted command exists.
5. Copy is a prefilled client draft only. Save Copy calls only `copy_interview_schedule`; requires the exact source/target optimistic tokens and one operation-scoped idempotency key, allows same/different Application selection, accepts editable logistics/participants, keeps Demo Topic blank, and renders structured conflict/stale/permission errors without raw SQL details.
6. Use the current server-returned state after each command. Disable duplicate submission while pending; preserve and send exact optimistic/idempotency tokens where required; do not optimistic-write business state.
7. Idempotency-key lifecycle is operation-scoped: generate a key once for a distinct user mutation intent and reuse that same key for every retry of that same intended mutation, including a retry after transport ambiguity/timeout. Generate a different key only for a genuinely new user mutation intent. Never regenerate a key merely because the same operation is retried.
8. For participant mutations, forward the effective accepted arguments exactly:
   - add: one operation-scoped idempotency key, reused on retry;
   - remove: current participant `expected_version`;
   - re-add: one accepted restore mode plus one operation-scoped idempotency key, reused on retry;
   - reorder: ordered current participant IDs plus their aligned expected-version array.
9. Application Reactivate must forward `p_expected_version` and render stable server errors, including where returned: `STALE_VERSION`, `INVALID_STATE`, `ACTIVE_APPLICATION_OWNER_REASSIGN_REQUIRED`, `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`, `SCHEDULE_CONFLICT_CANDIDATE`, `SCHEDULE_CONFLICT_ROOM`, `SCHEDULE_CONFLICT_INTERVIEWER`, and `FORBIDDEN`. Do not duplicate the command's owner/resource/participant preflight in client code.
10. Respect UI contract: `Ứng tuyển` means exact Submission selector, creation does not infer latest Submission; create-next-round obeys the latest-active/not-HIRED gate; schedule status semantics, Confirmed edit restriction, format normalization feedback, participant ordering/snapshots, and conflict messages match source.
11. Preserve semantic HTML, labels, keyboard operation, focus restoration, visible focus, status text beyond color, accessible validation/error association, responsive table overflow behavior, and no PII search text in URL.

## Scope and non-goals
- Reuse current project components, server-action patterns, Supabase server clients, error/result conventions, and tests. Search before adding shared components/helpers.
- Do not create a generic state library, a generic modal framework, an alternate RPC abstraction, client-side authorization, direct browser database calls, email delivery UI, document upload UI, reports, master-data work, or unrelated refactors.
- Do not modify `recruitment_webapp/` authority sources.
- Do not modify the accepted Slice-04 migrations or their accepted regression tests, including `20260906060000_interview_schema_and_conflict_locking.sql`, `20260906070000_interview_lifecycle_commands.sql`, `20260906080000_copy_interview_schedule.sql`, and `20260906090000_application_reactivation_and_participant_contract_repair.sql`.
- If current accepted implementation contradicts a canonical source, stop and report the exact blocker; do not silently repair SQL inside this UI task.

## Verification
- Add consumer-observable unit/component tests for command result/error handling, copy draft/save behavior, participant/order and status/restricted-control behavior.
- Add focused coverage proving create-next-round uses the accepted round-allocation command and preserves one operation-scoped idempotency key across retries of the same mutation intent.
- Add focused coverage proving Save Copy forwards all accepted source/target optimistic tokens and reuses the same operation-scoped idempotency key when the same intended Save Copy is retried.
- Add focused coverage proving application-reactivation wrapper behavior, expected application-version forwarding, owner-reassignment-required handling, inactive-current-participant handling, and post-command server-state refresh.
- Add focused coverage proving the repaired participant argument shapes, accepted re-add restore modes, idempotency-key reuse for add/re-add retries, expected-version forwarding for remove, and aligned expected-version arrays for reorder.
- Run focused tests plus existing web lint/typecheck/build as appropriate.
- Run React Doctor on changed scope.
- Run browser QA against the actual local Interview surface: keyboard/dialog/focus behavior, same- and cross-Application Copy flows, an expected conflict, inactive Application filtering/reactivation, inactive Interview-round reactivation, participant re-add mode selection, same-intent retry protection, and responsive overflow.
- Report exact SHA, changed paths, verification output, and any canonical contract blocker. Do not push, merge, deploy, or update `project_control/`.
