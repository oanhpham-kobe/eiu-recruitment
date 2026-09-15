# TASK-S07-004 — Checkpoint B: cleanup runner core and narrow runtime binding

WORK_ID: S07-004-CHATGPT-CHECKPOINT-B-001
PRODUCER: EXTERNAL_CHATGPT
INDEPENDENT_IMPLEMENTATION_REVIEWER: OMP / eiu-reviewer (pending final frozen candidate)
SOURCE_REOPEN_REQUIRED: false

## Baseline

- Immutable task baseline: `checkpoint/pre-S07-004-002`
- Baseline SHA: `9af517c0f83af1c3337f6e7b12dd50595aaea9f0`
- Implementation branch: `chatgpt/TASK-S07-004-physical-storage-cleanup-runner`
- Owner role override: `project_control/reviews/S07_004_OWNER_ROLE_OVERRIDE_v1.md`

## Implemented through this checkpoint

1. `web/src/lib/storage/cleanup-runner.ts`
   - bounded claim -> authorize -> exact provider delete -> complete sequence;
   - caller cannot supply destructive bucket/path;
   - per-job authorization denial performs zero provider calls and batch continues;
   - provider failures report only accepted safe retry codes through the same attempt/fencing identity;
   - stale/expired completion is not retried with modified attempt identity.

2. `web/src/lib/storage/storage-provider.ts`
   - separate Storage provider capability seam;
   - exact `storage.from(bucket).remove([path])` deletion only;
   - behavior-driven authoritative-absence helper;
   - missing bucket/generic 404 is not silently treated as absent;
   - provider timeout/unavailable/temporary failure maps to the S07-003 completion allowlist.

3. `web/src/lib/storage/cleanup-worker-client.ts`
   - server-only Supabase/PostgREST worker client;
   - explicit injected URL/API key/worker access token;
   - no token minting, persistence, production secret provisioning, or browser exposure.

4. `supabase/migrations/20260916010000_storage_cleanup_worker_runtime_binding.sql`
   - grants `storage_cleanup_worker` membership only to PostgREST `authenticator` for role switching;
   - explicitly revokes membership from anon/authenticated/service_role;
   - does not re-grant cleanup RPC EXECUTE to service_role.

5. `supabase/tests/storage_cleanup_worker_binding_test.sql`
   - asserts authenticator membership;
   - asserts anon/authenticated/service_role non-membership;
   - asserts service_role/browser roles remain denied cleanup RPC EXECUTE;
   - exercises local role assumption/reset without physical deletion.

6. `web/src/__tests__/storage-cleanup-runner.test.ts`
   - denied-first/eligible-second batch continuation;
   - exact authorized target only;
   - provider timeout through same fenced attempt;
   - stale completion rejection after provider I/O;
   - accepted claim/lease input bounds;
   - bounded adapter error extraction;
   - object-absence vs missing-bucket discrimination;
   - Supabase provider success/absence/outage mapping.

## Verification completed at Checkpoint B

A strict isolated TypeScript compile was run against the new core modules using stubs matching the accepted `SupabaseClient` and S07-003 cleanup adapter interfaces:

`CORE_TYPESCRIPT_STATIC_COMPILE: PASS`

This is supporting syntax/type-shape evidence only. It is NOT claimed as the repository's formal `npm run typecheck`, unit suite, database replay, or local Storage integration.

Current execution environment does not provide Docker or Supabase CLI, so the producer has NOT claimed local DB/Storage execution in this checkpoint.

## Explicitly pending for Checkpoint C

- real disposable local Supabase Storage integration harness;
- both `candidate-quarantine` and `interview-quarantine` physical deletion;
- behavior observation for already-absent `remove()` result;
- custom worker JWT / PostgREST end-to-end role-binding proof;
- retained current/historical reference no-delete cases;
- terminal cleanup DONE, crash-after-delete recovery, provider retry, stale attempt, neighbor isolation and no-sweep cases;
- integration-CI wiring for new S07-004 gates;
- full repository Web/DB verification;
- canonical control-plane reconciliation before final review candidate.

## Safety declarations

- Connected Supabase mutation: NO
- Vercel deployment: NO
- Production Storage delete: NO
- `main` mutation: NO
- PR create/merge: NO
- TASK-S07-005 materialized: NO
- S07-003 reopened: NO
- Implementation accepted: NO

This is a resumable implementation checkpoint, not an acceptance candidate.
