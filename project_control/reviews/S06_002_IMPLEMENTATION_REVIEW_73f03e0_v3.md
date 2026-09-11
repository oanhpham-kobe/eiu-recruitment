# TASK-S06-002 — Independent Implementation Review R3

WORK_ID: S06-002-IMPLEMENTATION-REVIEW-001-R3
REVIEWED_SHA: 73f03e00b6c2f90874eb17419e57ca58715a6990
RESULT: BLOCKING_REPAIR
SOURCE_REOPEN_REQUIRED: NO

## Scope

Targeted exact-SHA R3 re-review of the unresolved R2 concurrency / lifecycle / identity findings, the R3 repair delta, directly crossed RBAC and locking invariants, and concrete regression risk introduced by the repair.

## Closed R2 findings

1. Durable master-reference history no longer requires the prior master-row lock on the old reference path. `private.record_master_reference_history(..., false)` only records durable history; the existing once-referenced retention contract remains intact.
2. Resource-blocking interview participant lifecycle now acquires participant / actor User rows in deterministic order before Internal User advisory locks and revalidates current participant activity after the complete lock set.
3. New participant selection / restoration now locks and revalidates the selected Internal User even when the Interview is otherwise dormant.
4. First Google identity bind re-verifies the exact normalized trusted Google email after normalized-email, target User-row, and Internal User locks are held.

Producer exact-SHA verification run 34628766807 was PASS. Those results are supporting evidence, not a substitute for independent review.

## Blocking finding

### B1 — `update_internal_user_directory` performs privileged contention before authorization

R3 replaces the public wrapper so it may acquire:

- the normalized-email advisory transaction lock; and
- an Organizational Unit `FOR KEY SHARE` row lock

before delegating to `public.update_internal_user_directory_s06_002_r2_impl(...)`.

However the delegated implementation performs the canonical authorization checks first: `auth.uid()` must exist, then the caller must resolve to an Internal User with either Root Admin or `users.directory_manage` permission. The R3 wrapper therefore changes the order from:

`AUTHN -> AUTHZ -> validation/business locks`

to:

`email/unit contention -> AUTHN -> AUTHZ`.

Because the wrapper is `SECURITY DEFINER` and executable by `authenticated`, a caller that is authenticated but lacks `users.directory_manage` can still enter the email advisory-lock and Unit row-lock contention paths before receiving `FORBIDDEN`. A missing auth context can likewise reach the pre-lock code before the delegated implementation returns `UNAUTHENTICATED` when the SQL role permits invocation.

This is a real RBAC/concurrency regression: unauthorized principals can consume privileged lock resources and observe timing dependent on protected resource contention. It violates the accepted authorization-before-side-effects/locks ordering of the underlying command.

## Required R4 repair

Smallest sufficient repair:

1. Put the same authentication + directory-management authorization guard at the start of the public R3 wrapper, before email normalization/pre-lock and before Unit lookup/lock.
2. Keep the delegated implementation guards as defense in depth.
3. Preserve the accepted R3 lock order for authorized callers (`Email -> Unit -> User`) and do not reopen already-closed R2 findings.
4. Add focused regression evidence proving an unauthorized authenticated principal returns `FORBIDDEN` without waiting on a contended target email advisory lock / Unit lock; similarly prove missing auth returns `UNAUTHENTICATED` before pre-lock contention where invocable.
5. Run focused R4 verification plus the directly crossed Internal User/RBAC/concurrency regressions, then submit the new exact candidate SHA for targeted R4 independent review.

## Boundaries

- Do not serialize product into integration before an exact-SHA R4 PASS.
- Do not mutate accepted historical migrations.
- Do not push/merge `main` or create/merge a PR.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase.
