# TASK-S07-004 — Physical Storage Cleanup Runner and Local Storage Integration

## Dispatch gate and exact baseline

This is an implementation prompt for future Owner dispatch, NOT current implementation authority. Current continuation stops after independent prompt/source PASS. Execution is permitted only after external prompt audit and explicit dispatch.

Repository: `oanhpham-kobe/eiu-recruitment`. Integration: `autonomy/continuous-integration-20260905-01`. Starting reporting HEAD: `f536c839e0999e66b498dbfcd40d321539a7b4cd`. Governed implementation baseline is the exact peeled commit of immutable `checkpoint/pre-S07-004-001`, or the latest independently PASS numbered replacement recorded in TASK_REGISTRY before dispatch. Resolve the ref and compare with the review's REVIEWED_SHA; never use a moving integration HEAD as a substitute. The baseline commit contains this prompt, so its own SHA is recorded by immutable ref and later evidence, not a fabricated self-hash.

Accepted predecessors:
- `checkpoint/S07-001-accepted-001` → `8397be35d64a65f4a693811e4fc6b9e43287a7cd`
- `checkpoint/S07-002-accepted-001` → `d99776aa6e07c0023ada9906211f6d1d4b17f5ed` (tag object `105506f6e68e1acb4e1b0cf732bbe5beb2b66136`)
- `checkpoint/S07-003-accepted-001` → `7317138779270087e3e425f48b13785923b17f42` (tag object `a2702995bb1b475d003ad8e85d4a2c58b7fcd75c`)
All predecessor checkpoints remain immutable. S07-003 formal exact-SHA Integration CI `34979021250` and Governance CI `34979021519` PASS.

Dependencies: `TASK-S02-003`, `TASK-S02-004`, `TASK-S04-002`, `TASK-S07-002`, `TASK-S07-003`; all DONE. Materialize and execute no sibling task or Slice-08.

## Source authority and preflight

Read `project_control/reviews/S07_004_SOURCE_RECONCILIATION_v1.md`, accepted S07_001, S07_002, and S07_003 source reconciliations, current runtime/DAG, REVIEW.md, and canonical current sections:
- `review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` §§5–9;
- `review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§3, 10, 16 and trusted document deletion;
- `review_pack/41_STORAGE_AND_UPLOAD_SECURITY.md` (private buckets, staged lifecycle, signed bounds, durable Interview cleanup);
- `review_pack/42_PRIVACY_RETENTION_COMPLIANCE.md` and `66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md`;
- `review_pack/39_SECURITY_RLS_MATRIX.md`, `59_RLS_POLICY_BLUEPRINT.md`;
- `review_pack/47_AUDIT_LOGGING_SPEC.md`, `48_IDEMPOTENCY_CONCURRENCY_SPEC.md`, `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`;
- `source_registry.yaml` and `app_spec.yaml` cleanup/retention/session sections.

Effective ordered migrations and actual callers outrank starter schema and historical observations. Inspect accepted S07-003 cleanup RPCs, queue schema, reservation signing/finalization, and current/historical version references. Use symbol references before changing exported adapters; preserve user changes. Parent owns Todo and integration. Material DB work uses the project DB executor when delegated; no concurrent writers in one worktree.

## Bounded outcome

Provide a bounded, server-only physical storage cleanup runner and local Supabase Storage integration that consumes the accepted S07-003 database cleanup contracts. This task owns the physical deletion runner, the separation between DB cleanup authorization and Storage provider deletion, crash/timeout recovery semantics, object-not-found idempotency, and real local Storage verification. It does not own bucket sweeps, provider daemon hosting, production scheduling, or production deployment.

### A. Narrow database worker capability binding

Accepted S07-003 establishes `storage_cleanup_worker` as `NOLOGIN NOINHERIT` with execute rights on cleanup RPCs revoked from `public`, `anon`, `authenticated`, and `service_role`.
- The runner must execute cleanup RPCs under this narrow role capability, not through `service_role` privilege broadening.
- **Runtime postgrest/client binding**:
  If connecting via PostgREST client, establish the custom role bridge by adding a small forward migration:
  `grant storage_cleanup_worker to authenticator;`
  This enables server-only creation of a worker client signed by `SUPABASE_JWT_SECRET` containing `{ "role": "storage_cleanup_worker" }`. PostgREST assumes `storage_cleanup_worker` via `SET LOCAL ROLE`. Browser roles (`anon`, `authenticated`) have zero access; `service_role` remains revoked from cleanup RPCs.
- **Direct connection binding**:
  In local scripts or database integration harnesses, direct connection via `DATABASE_URL` as user `postgres` (which is a member of `storage_cleanup_worker`) may assume the role directly via `SET ROLE storage_cleanup_worker;`.
- Both approaches keep the DB capability narrow, server-only, non-browser, and locally testable without production secrets.

### B. Storage-provider capability seam & destructive sequence

Physical deletion of a private object requires a separate Storage provider capability (Storage API / `storage.from(bucket).remove([path])`):
- The runner must strictly decouple **DB cleanup authorization** from the **Storage provider deletion** capability.
- Possessing a Storage admin credential does not confer deletion authority; DB authorization is strictly authoritative.
- The runner executes the exact sequential lifecycle:
  1. **Claim**: Call `claimStorageCleanupJobs(workerId, limit, leaseSeconds, dbClient)`. Retain exact `storage_cleanup_id`, `worker_id`, `attempt_id`, and `fencing_token`.
  2. **Authorize**: Call `authorizeStorageCleanupAttempt({ storageCleanupId, attemptId, fencingToken, workerId }, dbClient)`.
     - If authorization returns `{ success: false, error_code: ... }` (e.g. `CLEANUP_WITHHELD`, `STALE_ATTEMPT`, `NOT_FOUND`): Do NOT call the Storage provider for this job; record the withheld/error outcome and skip to the next claimed job in the batch.
     - If authorization returns `{ success: true, data: ... }`: Extract the exact authorized `bucket_name` and `object_path`.
  3. **Physical Provider Delete**: Call `storageProvider.removeObject(authorized.bucket_name, authorized.object_path)` using the exact authorized pair.
  4. **Complete**: Report outcome via `completeStorageCleanupAttempt({ storageCleanupId, attemptId, fencingToken, workerId, success, errorCode }, dbClient)`.
- Prohibitions: No deletion before authorization; no bucket listing; no prefix guessing; no deletion targets derived from arbitrary caller parameters.

### C. Crash windows and idempotency

Handle all failure windows safely:
- **Window 1 (Auth commits, crash before delete)**: Queue remains `PROCESSING` with `tombstoned_at` set. After lease expiry, subsequent claim reclaims the job with a new `attempt_id`/`fencing_token`. Re-authorization succeeds (`tombstone_cleanup_id == p_q.storage_cleanup_id`). New worker deletes object.
- **Window 2 (Delete succeeds, crash before DB complete)**: Object removed from Storage, but queue remains `PROCESSING`. After lease expiry, reclaimed attempt authorizes and calls provider delete. Provider returns `OBJECT_NOT_FOUND` (404). Under Section D policy, absent object completes as `success: true`. Queue settles `DONE`.
- **Window 3 (Provider timeout / ambiguous outcome)**: Worker records `PROVIDER_TIMEOUT` or lease expires. Reclaimed attempt re-executes. If object was deleted $\rightarrow$ 404 $\rightarrow$ `DONE`. If not deleted $\rightarrow$ provider deletes $\rightarrow$ `DONE`. 5-attempt ceiling prevents infinite loop.
- **Window 4 (Lease expires in flight)**: Old worker attempting completion after lease expiry or reclaim receives `STALE_ATTEMPT`. It cannot overwrite newer attempts.
- **Window 5 (Reclaim during stale execution)**: Stale worker's credentials are invalidated. Reclaim owns the exclusive lease.

### D. Object-not-found semantics

When the Storage provider returns `OBJECT_NOT_FOUND` (HTTP 404) for an exact authorized `(bucket_name, object_path)`:
- The runner treats the absent object as desired terminal state achieved and calls `completeStorageCleanupAttempt(..., success: true)`.
- Rationale: DB authorization proved the object had terminal provenance and zero business references. An already-absent object satisfies the cleanup objective and cannot be resurrected (tombstone remains in provenance). This ensures self-healing crash recovery (Window 2) without false historical metrics.

### E. Network/transaction separation

- Storage provider network calls MUST execute strictly outside database transactions.
- Step 2 (`authorize_storage_cleanup_attempt`) commits independently, placing an immutable tombstone in `private.storage_cleanup_provenance` that prevents resurrection while the external call is in flight.
- Step 3 (Storage deletion) runs with zero open database transactions or row locks.
- Step 4 (`complete_storage_cleanup_attempt`) commits independently.

### F. Retention and safety invariants

Retain all S07-003 safeguards:
- Restricted to private managed temp buckets (`candidate-quarantine`, `interview-quarantine`).
- Current or historical Candidate document references block cleanup (`RETAINED_REFERENCE`).
- Current or historical Interview document references block cleanup (`RETAINED_REFERENCE`).
- Live reservations block cleanup (`LIVE_RESERVATION`).
- Unelapsed signed windows block cleanup (`SIGNED_WINDOW`).
- Genuinely detached legacy rows without reservation evidence fail closed (`UNKNOWN_PROVENANCE`).
- Tombstoned identities reject resurrection (`STORAGE_CLEANUP_IDENTITY_TOMBSTONED`).

## Local storage integration test requirements

The implementation must verify real physical provider behavior against a disposable local Supabase environment covering at least 12 test cases:
1. **Authorized deletion**: An authorized temp object is physically deleted from the quarantine bucket.
2. **Neighbor isolation**: A neighboring object in the same bucket/prefix is untouched and remains in Storage.
3. **No-authorization refusal**: A job where authorization was not obtained or was withheld causes zero Storage deletes.
4. **Retained current reference protection**: A reservation whose path is referenced by a current document causes zero Storage deletes.
5. **Retained historical reference protection**: A reservation whose path is referenced by a historical document causes zero Storage deletes.
6. **Stale attempt rejection**: A worker holding an expired lease or stale attempt cannot delete or complete.
7. **Terminal eligible object removal**: An expired/cancelled reservation past its signed window is authorized, deleted from Storage, and completed as `DONE`.
8. **Delete-success crash recovery**: Simulating a crash after provider delete causes subsequent reclaim to complete successfully upon encountering 404.
9. **Already-absent idempotency**: An already-absent authorized object (404) completes cleanly as `DONE`.
10. **Provider error / retry**: A temporary provider error records `errorCode` and leaves the queue row eligible for retry under the 5-attempt ceiling.
11. **Stale completion fence**: A reclaimed job rejects completion from the old worker attempt.
12. **Targeted non-sweep execution**: Deletion operates strictly on exact authorized `(bucket, path)` pairs without bucket listing or prefix sweeps.

## Expected implementation shape

- `web/src/lib/storage/cleanup-runner.ts`: Server-only runner module implementing single-job execution and bounded batch iteration.
- `web/src/lib/storage/storage-provider.ts`: Storage provider abstraction (with real Supabase Storage implementation and mock implementation for unit tests).
- `web/src/__tests__/storage-cleanup-runner.test.ts`: Unit tests verifying runner state machine, retry policy, error mapping, and crash window handling using mock providers.
- `supabase/tests/storage_cleanup_local_storage_test.sh`: Integration harness executing real physical object creation and deletion against local Supabase Storage containers.

## Implementation out of scope

- Production Vercel or Supabase deployment.
- Connected Supabase migrations or operations.
- Production cron/scheduler infrastructure.
- Continuous background daemon execution.
- Arbitrary bucket listing or wildcard sweeps.
- Malware scanner runtime execution.
- Email delivery provider runtime.
- Email History UI or administrative notification UI.
- General data archive/export/purge.
- `TASK-S07-005` or any second next task.

## Verification plan

Focused verification for future implementation:
- Unit tests: Runner state machine, mock provider tests, retry policy, error mapping (`npm run test -- src/__tests__/storage-cleanup-runner.test.ts`).
- Local integration tests: Physical Storage object lifecycle in local Supabase Storage (`supabase/tests/storage_cleanup_local_storage_test.sh`).
- Predecessor regressions: S07-003 SQL contract, S07-003 concurrency/fencing, S07-003 upgrade path, S02, S04, S07-002 regressions.
- Web verification: lint, typecheck, build.
- Governance validators: `validate_control_plane.py`, `validate_omp_native.py`.
- Exact-SHA formal CI: fresh Integration CI and Governance CI on integration branch.

## Stop conditions and source reopen

Stop immediately at prompt review PASS. Do not begin implementation. Do not dispatch an executor.

`SOURCE_REOPEN_REQUIRED: false`.
No canonical invariant requires modifying any accepted predecessor. Bounded physical cleanup is a pure downstream consumer of accepted S07-003 trusted contracts.
