# TASK-S04-005 — Application Reactivation and Participant Command Contract Repair

## Goal
Implement the missing canonical `reactivate_application` trusted command and repair the participant RPC surface before Interview UI dispatch. Add exactly one append-only migration ordered after `20260906080000_copy_interview_schedule.sql` and one focused SQL regression; do not modify accepted migrations through that cutoff.

## Authority
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§5–8.
- `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` §§9, 11, 263–275.
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`: AC-APP-REACT-04, AC-APP-REACT-05, AC-APP-REACT-PAST-01, AC-PART-OPER-02..04.
- Ordered accepted migrations through `20260906080000_copy_interview_schedule.sql` are effective implementation authority. The shared parent-first lock rule is additionally defined in `20260905120000_bulk_submission_status_and_application_assignment.sql` and `recruitment_webapp/review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md`.

## Required command repair
1. Add exactly `public.reactivate_application(uuid,bigint)`. It requires Root or `applications.manage`; lock the immutable parent Submission `FOR UPDATE` before re-reading and locking the Application `FOR UPDATE`, then verify immutable identity and expected version. Lock relevant child Interviews deterministically before participant snapshots and resource locks. Require an active eligible HR/root owner (or explicit same-transaction reassignment only if canonical contract already exposes it), audit, and parent status recalculation.
2. Repair Application soft-inactivation and reactivation as a round-trip: inactivation changes only `applications.is_active` and preserves every child `interviews.is_active`; Reactivate changes only the parent after checking preserved active children that are non-CANCELLED, have complete intervals, and `end_at > transaction_now`. Revalidate their current Participants and deterministic Candidate/Room/Interviewer conflicts. Fully elapsed intervals never block; any relevant conflict rolls back all changes. Intentionally inactive child rounds never revive.
3. Remove stale overloads and leave exactly these participant RPC signatures: `add_interview_participant(uuid,uuid,uuid)`, `remove_interview_participant(uuid,bigint)`, `readd_interview_participant(uuid,text,uuid)`, and `reorder_interview_participants(uuid,uuid[],bigint[])`. Root is implicit; non-root requires both `interviews.participants` and `interviews.view`, never `interviews.manage`. Every controlled-search-path SECURITY DEFINER function must check its exact caller predicate, revoke `PUBLIC`/`anon`, and grant execute only to `authenticated`.
4. Keep expected-version, audit, report archival/restore, participant snapshot/order, idempotency, and error contracts from existing accepted lifecycle commands. Do not weaken RLS/grants or modify UI.

## Tests
Add focused SQL tests proving: exact RPC signatures/no stale overloads; unauthenticated failure; Root success; `applications.manage` non-Root Reactivate success and application-view-only failure; participant-plus-view non-Root success; participant-only, view-only, manage-plus-view-without-participants failures; stale version; inactive owner/current participant; relevant Candidate/Room/Interviewer conflicts; fully elapsed overlap success; Application inactivate→reactivate with mixed active/inactive child flags preserved; atomic rollback/audit/recalculation. Run local reset, focused suite, S04-001/S04-002/S04-003 regressions, and diff check. Do not push/merge/deploy or alter project_control.
