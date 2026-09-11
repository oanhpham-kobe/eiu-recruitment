# TASK-S06-002 — Independent Implementation Review R3 Handoff

Copy-ready independent review request for `eiu-reviewer`.

## Review identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R3`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- EXACT_REVIEW_SHA: `73f03e00b6c2f90874eb17419e57ca58715a6990`
- PRIOR_BLOCKED_SHA: `7c37d46fa504b5d98b156735d7355f1d938be0bf`
- PRIOR_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_EXPECTATION: `false`
- REVIEW_GATE: `project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_73f03e0_v1.md`
- CANDIDATE_CONTAINED_GATE: `project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_v1.md`

## Reviewer instruction

Check out or inspect **exact SHA `73f03e00b6c2f90874eb17419e57ca58715a6990`**. Confirm HEAD equality before review. Treat worker run `34628250213` and exact verifier `34628766807` only as producer evidence; do not infer acceptance from CI.

Re-review the four R2 blockers end-to-end:

1. Unit/User/Application durable-history lock graph and public bulk assignment versus lifecycle/HR-role administration.
2. Interview operationalization ordering for actor/current-participant User rows versus Internal User advisories, including schedule/uncancel races.
3. Dormant/CANCELLED/unscheduled new participant add/re-add restoration versus deactivation while retaining allowed historical maintenance.
4. First Google bind trusted Auth evidence freshness after the full lock set and equality with the original normalized email key.

Also verify no regression in: safe directory read surface, granular permission privacy, HR default/granular permission semantics, Root-only non-root identity change, no auto-rebind, optimistic versioning/idempotency/audit contracts, accepted S06-001 durable history, Application owner eligibility, canonical resource-blocking participation semantics, and stable server-side error mapping.

## Required verdict

Return:

- `WORK_ID: S06-002-IMPLEMENTATION-REVIEW-001-R3`
- `REVIEWED_SHA: 73f03e00b6c2f90874eb17419e57ca58715a6990`
- `VERDICT: PASS | BLOCKING_REPAIR`
- `SOURCE_REOPEN_REQUIRED: true | false`
- blocking findings, if any, ordered highest risk first;
- evidence persistence coordinates if the reviewer can persist them, otherwise explicitly `UNAVAILABLE`.

Do not write product code, mutate refs, integrate the candidate, push/merge `main`, create/merge a PR, deploy Vercel, or apply connected Supabase migrations.
