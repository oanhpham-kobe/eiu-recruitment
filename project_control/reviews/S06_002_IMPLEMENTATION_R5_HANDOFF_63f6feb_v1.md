# TASK-S06-002 — OMP Independent Implementation Review R5 Handoff

> Status: `OMP_REVIEW_PROMPT_READY`
>
> This artifact is a copy-ready prompt for OMP. Its presence does **not** mean `eiu-reviewer` has been invoked. `eiu-reviewer` is invoked only when this prompt is actually sent to OMP.

You are OMP. Dispatch this review to the independent project reviewer named exactly:

`eiu-reviewer`

Do not perform the review as the producer/coordinator. The reviewer must independently inspect the exact GitHub SHA below.

## Review identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R5`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- EXACT_REVIEW_SHA: `63f6feba352852af5826dd582d1c42159edd66d6`
- PRIOR_REVIEWED_SHA: `56dbbb9e261a9c1e4587169870c78a4de8d95956`
- PRIOR_WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R4`
- PRIOR_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_EXPECTATION: `false`
- PRIOR_REVIEW_EVIDENCE_BRANCH: `review/S06-002-IMPL-56dbbb9-v4`
- PRIOR_REVIEW_EVIDENCE_COMMIT: `dd0eb84eb985327591a4b36f8988ed00db8b389b`
- PRIOR_REVIEW_EVIDENCE_PATH: `project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_56dbbb9_v4.md`
- PRODUCER_EXACT_VERIFIER_RUN: `34642569919` — PASS

## Exact-SHA discipline

Before reviewing:

1. Fetch repository state from GitHub.
2. Inspect exact SHA `63f6feba352852af5826dd582d1c42159edd66d6` in detached/exact-SHA mode.
3. Explicitly confirm reviewed HEAD equality.
4. Compare against prior reviewed R4 SHA `56dbbb9e261a9c1e4587169870c78a4de8d95956`.
5. Do not substitute the moving task branch for exact SHA review.
6. Treat producer CI as supporting evidence only, never as acceptance.

## R4 blocker repair scope

The prior R4 review found production authorization-before-contention statically closed, but returned `BLOCKING_REPAIR` for two test-evidence defects:

1. contention tests did not prove the target lock holder had acquired the exact email/Unit lock before the tested RPC or retained it through the RPC;
2. missing-auth coverage omitted Unit-row contention.

The R5 candidate intentionally leaves the R4 production migration unchanged. Relative to prior reviewed SHA `56dbbb9e261a9c1e4587169870c78a4de8d95956`, the only intended changed file is:

- `supabase/tests/internal_user_r4_authorization_prelock_test.sh`

Verify this independently from Git.

## Required targeted review

### 1. Prove exact lock acquisition before each tested RPC

Review the synchronized holder protocol in `supabase/tests/internal_user_r4_authorization_prelock_test.sh`.

For every contended case, verify that the holder transaction:

- acquires the **exact target resource lock first**;
  - normalized-email advisory xact lock for email cases; or
  - `FOR UPDATE` on the exact Organizational Unit row for Unit cases;
- only after target acquisition, acquires a unique readiness advisory **transaction** lock;
- remains in the same open transaction while the tested RPC executes.

Verify that the test does not invoke the RPC until it has independently observed:

- exactly one holder backend with the expected unique `application_name`; and
- the readiness advisory lock already held by that holder transaction.

The readiness mechanism must be logically sufficient to prove target-lock acquisition happened first.

### 2. Prove continued ownership through RPC completion

Verify that after the tested RPC returns, and before holder release, the test establishes that:

- the holder shell/backend is still alive;
- exactly one expected holder backend still exists; and
- the readiness transaction lock is still held.

Because the target lock and readiness lock are acquired in the same open transaction and transaction-scoped, confirm this proves that the target email advisory lock / Unit row lock remained held throughout the tested RPC.

Reject the evidence if a race still permits the holder transaction to release before or during the tested call.

### 3. Verify deterministic release and cleanup

Verify that each holder is released only after the post-RPC ownership assertion, using explicit backend termination/cleanup rather than relying on a short sleep expiry.

Confirm test cleanup cannot leave holder backends or locks alive on normal or failure exit.

### 4. Unauthorized email contention

While the exact normalized-email advisory lock is synchronously confirmed held, an authenticated Internal User without Root Admin or `users.directory_manage` must:

- return `FORBIDDEN`;
- not hit statement timeout;
- return while the holder remains locked.

### 5. Unauthorized Unit contention

While the exact Unit row is synchronously held `FOR UPDATE`, the same unauthorized caller must:

- return `FORBIDDEN`;
- not hit statement timeout;
- return while the holder remains locked.

### 6. Missing-auth email contention

Under executable role `authenticated` but without trusted JWT subject, while the exact email advisory lock is confirmed held, the RPC must:

- return `UNAUTHENTICATED`;
- not hit statement timeout;
- return while the holder remains locked.

### 7. Missing-auth Unit contention — prior R4 blocker #2

Under executable role `authenticated` but without trusted JWT subject, while the exact Unit row is synchronously held `FOR UPDATE`, the `unit_id` patch RPC must:

- return `UNAUTHENTICATED`;
- not hit statement timeout;
- return while the holder remains locked.

This case is mandatory for PASS.

### 8. Authorized success control

Confirm the authorized Root Admin control still reaches the delegated directory implementation successfully and persists both email and Unit changes. The target remains intentionally identity-unbound because accepted identity contracts forbid email change after identity binding.

### 9. Production-code immutability across R4 → R5

Verify that `supabase/migrations/20260912014500_internal_user_r4_authorization_prelock.sql` is byte-for-byte unchanged between R4 SHA `56dbbb9e261a9c1e4587169870c78a4de8d95956` and R5 SHA `63f6feba352852af5826dd582d1c42159edd66d6`.

No product/schema repair is expected in R5. Any production-code delta outside the targeted test repair must be surfaced.

### 10. Regression sanity check

Confirm there is no reason to reopen the R4 production assessment or previously closed R2/R3 contracts, including:

- authorization before protected business-resource contention;
- Email → Unit → User lock ordering for authorized updates;
- durable Master Data reference history;
- Application owner eligibility;
- Interview participant/resource operationalization ordering;
- dormant/CANCELLED/unscheduled participant add/re-add lifecycle rules;
- post-lock Google identity evidence revalidation;
- no automatic identity rebind;
- Root-only non-root identity changes;
- granular permission privacy and HR permission semantics;
- optimistic versioning, idempotency, audit behavior, and stable server-side errors.

## Producer evidence

Producer exact verifier run `34642569919` completed `success` for exact candidate `63f6feba352852af5826dd582d1c42159edd66d6` and reported PASS for:

- exact-SHA/static repair-delta checks;
- zero-state Supabase migration replay;
- synchronized R4 authorization-before-prelock regression;
- focused Internal User/RBAC/Identity regressions;
- retained R1/R2/R3 lifecycle concurrency;
- database lint at error level;
- clean Supabase stop.

This is producer evidence only and must not be treated as independent acceptance.

## Required verdict

Return exactly these top-level fields:

`WORK_ID: S06-002-IMPLEMENTATION-REVIEW-001-R5`

`REVIEWED_SHA: 63f6feba352852af5826dd582d1c42159edd66d6`

`VERDICT: PASS | BLOCKING_REPAIR`

`SOURCE_REOPEN_REQUIRED: true | false`

Then provide:

- exact-SHA equality confirmation;
- assessment of both prior R4 blockers;
- blocking findings, if any, highest risk first;
- regression/reopen assessment;
- producer-evidence treatment;
- evidence persistence coordinates if reviewer-native persistence succeeds, otherwise explicitly `EVIDENCE_PERSISTENCE: UNAVAILABLE`.

## Reviewer boundaries

`eiu-reviewer` must NOT:

- write or repair product/test code;
- mutate task, integration, review-dispatch, or `main` refs;
- serialize candidate into integration;
- create or merge a PR;
- deploy Vercel;
- apply migrations to connected Supabase;
- infer PASS from producer CI.

If a blocker exists, return `BLOCKING_REPAIR` with the smallest sufficient repair requirement. If no blocker remains, return `PASS`.
