# TASK-S06-002 — Independent Implementation Review R4

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R4`
- REVIEWED_SHA: `56dbbb9e261a9c1e4587169870c78a4de8d95956`
- VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_REQUIRED: `false`
- Reviewer: `eiu-reviewer` via OMP / Owner transport

## Exact-SHA confirmation

Reviewer confirmed detached reviewed HEAD exactly `56dbbb9e261a9c1e4587169870c78a4de8d95956` and compared it with R3 SHA `73f03e00b6c2f90874eb17419e57ca58715a6990`.

The R4 delta was confirmed as two added files only, with no deletion or historical migration rewrite:

- `supabase/migrations/20260912014500_internal_user_r4_authorization_prelock.sql`
- `supabase/tests/internal_user_r4_authorization_prelock_test.sh`

## Blocking findings

### 1. Contention regression does not prove lock overlap

The regression test starts email and Unit lock holders asynchronously and relies on a fixed sleep before invoking the tested RPC. It does not establish that each holder acquired its exact target lock before the RPC executes, nor prove that the holder remains locked through the RPC.

Smallest required repair:

- add a readiness handshake that confirms acquisition of each exact email/Unit lock;
- retain the holder until the tested RPC completes;
- fail if readiness or continued ownership cannot be established;
- release and clean up reliably.

### 2. Missing-auth coverage omits Unit contention

The test exercises missing trusted auth only against normalized-email advisory contention. It lacks a no-auth `unit_id` patch while the Unit row is contended.

Smallest required repair:

- add a synchronized missing-auth / contended-Unit case under an executable role with no trusted JWT subject;
- assert `UNAUTHENTICATED` without timeout while the Unit holder remains locked;
- release holder reliably afterward.

## Closed R3 blocker assessment

The production authorization-before-contention repair is statically closed. The R4 wrapper authenticates and authorizes before email normalization/advisory locking, Unit lookup/`FOR KEY SHARE`, target User locking, idempotency mutation, or audit mutation. The delegated implementation retains its own checks.

`private.current_app_user_id`, `private.is_root_admin`, and `private.has_permission` were assessed as non-row-locking authorization reads; rejected callers do not reach protected business-resource contention.

The review remains blocking only because the test evidence above does not yet prove the required runtime contention properties.

## Regression / reopen assessment

No production regression or source-reopen requirement was found. Authorized directory updates preserve Email → Unit → User business-resource order. The R4 migration remains append-only and preserves security-definer hardening, explicit ACL behavior, identity binding rules, durable history, owner eligibility, participant lifecycle safeguards, post-lock Google evidence verification, RBAC/privacy semantics, optimistic versioning, idempotency, audit behavior, and stable server-side errors.

## Verification note

The independent reviewer performed a read-only exact-SHA review. Producer run `34641136847` was treated only as supporting evidence. No tests, builds, linters, migrations, connected Supabase operations, or project-wide validation were executed by the reviewer.

## Evidence provenance

This artifact persists the reviewer verdict returned through Owner transport. The reviewer itself reported `EVIDENCE_PERSISTENCE: UNAVAILABLE`; this file does not claim reviewer-native persistence.
