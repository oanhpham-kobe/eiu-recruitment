# TASK-S04-005 — Application Reactivation and Participant Command Contract Repair

## Goal
Implement the missing canonical `reactivate_application` trusted command and repair the participant RPC surface before Interview UI dispatch. SQL migration plus focused SQL regression only.

## Authority
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§5–8.
- `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` §§9, 11, 263–275.
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`: AC-APP-REACT-04, AC-APP-REACT-05, AC-APP-REACT-PAST-01, AC-PART-OPER-02..04.
- Ordered accepted migrations through `20260906080000_copy_interview_schedule.sql` are effective implementation authority.

## Required command repair
1. Add one authenticated `public.reactivate_application` with pinned signature, expected Application version, application lock then parent Submission lock, active eligible HR/root owner validation (or explicit same-transaction reassignment only if canonical contract already exposes it), reactivation audit, and parent status recalculation.
2. Preserve historical identity and child history. Restore access-active context only after every non-elapsed child that would become resource-blocking passes current participant-active checks and deterministic Candidate/Room/Interviewer conflict checks. Fully elapsed intervals never block; any relevant conflict rolls back all changes.
3. Remove stale participant RPC overloads and leave exactly one approved signature each for add, remove, re-add, reorder. Root is implicit; non-root requires both `interviews.participants` and `interviews.view`, not `interviews.manage`. Revoke PUBLIC/anon; authenticated only.
4. Keep expected-version, lock order, audit, report archival/restore, participant snapshot/order, idempotency, and error contracts from existing accepted lifecycle commands. Do not weaken RLS/grants or modify UI.

## Tests
Add focused SQL tests proving unauthenticated, view-only, manage-only, participant-only, Root, stale version, inactive owner/current participant, relevant Candidate/Room/Interviewer conflicts, fully elapsed overlap success, atomic rollback/audit/recalculation, and no ambiguous participant overload remains. Run local reset, focused suite, S04-001/S04-002/S04-003 regressions, and diff check. Do not push/merge/deploy or alter project_control.
