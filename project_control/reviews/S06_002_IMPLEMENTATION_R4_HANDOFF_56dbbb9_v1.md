# TASK-S06-002 — Independent Implementation Review R4 Handoff

Copy-ready targeted independent review request for `eiu-reviewer`.

## Review identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R4`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- EXACT_REVIEW_SHA: `56dbbb9e261a9c1e4587169870c78a4de8d95956`
- PRIOR_REVIEWED_SHA: `73f03e00b6c2f90874eb17419e57ca58715a6990`
- PRIOR_VERDICT: `BLOCKING_REPAIR`
- PRIOR_REVIEW_EVIDENCE_BRANCH: `review/S06-002-IMPL-73f03e0-v3`
- PRIOR_REVIEW_EVIDENCE: `project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_73f03e0_v3.md`
- SOURCE_REOPEN_EXPECTATION: `false`
- R4_EXACT_VERIFIER_RUN: `34641136847` (`SUCCESS`)

## R4 delta

Relative to exact R3 SHA `73f03e00b6c2f90874eb17419e57ca58715a6990`, R4 is append-only and changes only:

1. `supabase/migrations/20260912014500_internal_user_r4_authorization_prelock.sql`
2. `supabase/tests/internal_user_r4_authorization_prelock_test.sh`

The migration places the canonical `auth.uid()` and Root Admin / `users.directory_manage` authorization guard before the R3 normalized-email advisory lock and Unit `FOR KEY SHARE` pre-lock. The delegated R2 implementation retains its own guards as defense in depth.

The regression test proves:

- an authenticated principal without `users.directory_manage` returns `FORBIDDEN` without waiting on a contended target-email advisory lock;
- the same unauthorized principal returns `FORBIDDEN` without waiting on a contended Unit row lock;
- missing trusted auth context returns `UNAUTHENTICATED` without waiting on the target-email advisory lock; and
- an authorized Root caller still reaches the accepted R3 pre-lock/delegated update path successfully using an intentionally unbound target, consistent with the existing no-email-change-after-identity-bind contract.

## Producer verification evidence

Exact verifier run `34641136847` checked out exact candidate SHA `56dbbb9e261a9c1e4587169870c78a4de8d95956` and completed successfully with:

- exact SHA / delta static checks: PASS
- zero-state Supabase migration replay: PASS
- R4 authorization-before-prelock regression: PASS
- focused Internal User / RBAC / Identity regressions: PASS
- retained R1/R2/R3 lifecycle concurrency suite: PASS
- database lint (`--level error`): PASS

Treat all CI as producer evidence only; do not infer review acceptance from CI.

## Reviewer instruction

Inspect **exact SHA `56dbbb9e261a9c1e4587169870c78a4de8d95956`** and confirm exact equality before reviewing.

Targeted re-review must determine whether the R3 blocking finding is closed without reopening previously closed R2 findings:

1. Verify `public.update_internal_user_directory(...)` now returns `UNAUTHENTICATED` / `FORBIDDEN` before any normalized-email advisory lock, Unit lookup/row lock, target User lock, idempotency mutation, audit mutation, or other privileged contention.
2. Verify authorized callers still preserve the accepted lock order required by R3 and delegation does not create a new inversion.
3. Verify the new regression fixture is contract-correct, especially the intentionally unbound target used for the authorized email-change path.
4. Sanity-check that R4 does not regress granular permission privacy, Root-only identity semantics, optimistic versioning/idempotency/audit behavior, durable master history, participant lifecycle locking, or first-Google-bind re-verification already closed in R3.
5. Check the R3→R4 diff for any new security, concurrency, privacy, data-integrity, or migration-replay regression.

## Required verdict

Return exactly:

- `WORK_ID: S06-002-IMPLEMENTATION-REVIEW-001-R4`
- `REVIEWED_SHA: 56dbbb9e261a9c1e4587169870c78a4de8d95956`
- `VERDICT: PASS | BLOCKING_REPAIR`
- `SOURCE_REOPEN_REQUIRED: true | false`
- blocking findings, if any, ordered highest risk first;
- evidence persistence coordinates if available, otherwise explicitly `UNAVAILABLE`.

Do not write product code, mutate task/integration/main refs, serialize the candidate, create/merge a PR, deploy Vercel, or apply migrations to connected Supabase.
