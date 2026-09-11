# TASK-S06-002 Independent Implementation Re-Review Gate R3

## Identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R3`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- R2_REVIEWED_SHA: `7c37d46fa504b5d98b156735d7355f1d938be0bf`
- R2_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_EXPECTATION: `false`
- EXACT_R3_SHA: supplied in the immutable coordinator handoff; reviewer must verify that exact SHA contains this gate before review.

## R2 blocker reconciliation required

1. Prove the complete Unit/User/Application graph. Unchanged `app_users.unit_id` history capture must not take a new-reference Unit lock; true directory Unit selection must lock Unit before target User; bulk/lifecycle/HR-role public races with non-null Unit must terminate without deadlock while preserving S06-001 durable history and active-master validation.
2. Interview operationalization must row-lock all current participant and actor FK User rows before Internal User advisory locks, then revalidate current participants. Cover uncancel and schedule by an HR who is also a current participant racing Root lifecycle administration.
3. New participant selection/restoration must use User row -> advisory -> post-lock active revalidation regardless of Interview dormancy. Historical remove/reorder maintenance remains allowed. Cover deactivation-first CANCELLED add and unscheduled re-add.
4. First Google bind must repeat `private.verified_google_auth_email(auth.uid())` after normalized-email advisory, target User row and Internal User advisory locks; it must equal the original advisory-key email and fail closed on evidence change.

## Required verification

- zero-state migration replay;
- focused Internal User/RBAC/Identity tests;
- R2 dormant-history and lock-order tests;
- R3 public-command staged concurrency tests;
- crossed Application/Interview/copy/bulk regressions;
- all retained S06-001 seed/history/durable-history regressions;
- full web install/audit/design/lint/typecheck/build/test;
- `supabase db lint --local --level error`;
- `git diff --check`;
- static proof that accepted migrations were not rewritten.

## Review boundary

Review exact immutable R3 SHA only. Reviewer is read-only and must not modify implementation, refs, integration, `main`, PRs, Vercel, connected Supabase, or later Slice-06 state.
