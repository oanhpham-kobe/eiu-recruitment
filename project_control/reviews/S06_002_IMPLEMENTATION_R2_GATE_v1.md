# TASK-S06-002 Independent Implementation Re-Review Gate R2

## Identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R2`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- R1_REVIEWED_SHA: `a7aa037e26cda6ba70153539c1dfc15c3fba37e6`
- R1_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_EXPECTATION: `false`
- EXACT_R2_SHA: supplied in the immutable coordinator handoff; reviewer must verify that exact SHA contains this gate before review.

This gate intentionally lives **inside the reviewed candidate tree**. A Git commit cannot embed its own future SHA without changing that SHA; therefore the coordinator supplies the exact 40-character R2 SHA out-of-band and the reviewer must verify `git rev-parse HEAD` equals it and that this file exists at that SHA.

## R1 blocker reconciliation required

1. The R1 gate and Owner-transported R1 evidence must now both exist in the reviewed task tree. This R2 gate must also exist at the reviewed SHA.
2. `authenticated` must still lack raw `app_users.auth_user_id` SELECT, while every retained request-scoped server consumer uses `get_current_internal_session()` or `get_current_internal_binding_status()` instead of filtering `app_users` by the hidden column.
3. Statement-level participant eligibility recheck must apply only to canonical `resource_blocking` Interviews. CANCELLED/inactive/unscheduled/fully-elapsed history must permit unrelated remove/reorder maintenance of retained inactive participants.
4. Application owner writers and Internal User lifecycle writers must share deterministic **target app_users row -> internal-user advisory -> revalidate** ordering. Verify the accepted `create_or_update_application()` path, reactivation path, direct trigger coverage, HR-role removal and lifecycle command composition.
5. First Google bind and Root rebind must share deterministic **normalized-email advisory -> target app_users row -> internal-user advisory -> revalidate** ordering.

## Required verification

- zero-state migration replay;
- focused `internal_user_rbac_identity_test.sh`, including the R2 dormant-history/own-binding regression;
- `internal_user_lifecycle_concurrency_test.sh`, including deterministic public-command owner/lifecycle and first-bind/rebind lock staging;
- crossed Application reactivation/participant, Interview lifecycle, round/conflict, copy and bulk regressions;
- all retained S06-001 canonical seed/history/durable-history regressions;
- full web install/audit/design/lint/typecheck/build/test;
- static proof that the listed request-scoped server files no longer query `app_users` by `auth_user_id`;
- `supabase db lint --local --level error`;
- `git diff --check`.

## Review boundaries

Review only the exact immutable R2 SHA supplied by the coordinator. Do not modify implementation, refs, integration, `main`, Vercel, connected Supabase, or later task state.

## Required output

Return `WORK_ID`, reviewed repository/branch/SHA, `VERDICT`, `SOURCE_REOPEN_REQUIRED`, blockers, observations, verification executed, identity-bind assessment, RBAC/visibility assessment, lifecycle-concurrency assessment, security assessment, accepted-contract reuse assessment, acceptance statement, and truthful evidence persistence coordinates or `UNAVAILABLE`.
