# TASK-S07-004 — Physical Storage Cleanup Runner and Local Storage Integration

## Dispatch gate and exact baseline

This is an implementation prompt for future Owner dispatch, NOT current implementation authority. Current continuation stops after independent prompt/source PASS. Execution is permitted only after external prompt audit and explicit dispatch.

Repository: `oanhpham-kobe/eiu-recruitment`. Integration: `autonomy/continuous-integration-20260905-01`. Starting reporting HEAD: `f536c839e0999e66b498dbfcd40d321539a7b4cd`. Governed implementation baseline is the exact peeled commit of immutable `checkpoint/pre-S07-004-002`, or the latest independently PASS numbered replacement recorded in TASK_REGISTRY before dispatch (superseding `checkpoint/pre-S07-004-001`). Resolve the ref and compare with the review's REVIEWED_SHA; never use a moving integration HEAD as a substitute. The baseline commit contains this prompt, so its own SHA is recorded by immutable ref and later evidence, not a fabricated self-hash.

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

Provide a bounded, server-only physical storage cleanup runner and local Supabase Storage integration that consumes the accepted S07-003 database cleanup contracts. This task owns the physical deletion runner, the separation between DB cleanup authorization and Storage provider deletion, crash/timeout recovery semantics, behavior-driven provider absence mapping, and real local Storage verification across both managed quarantine buckets (`candidate-quarantine` and `interview-quarantine`). It does not own bucket sweeps, provider daemon hosting, production scheduling, or production deployment.

### A. Narrow database worker capability binding

Accepted S07-003 establishes `storage_cleanup_worker` as `NOLOGIN NOINHERIT` with execute rights on cleanup RPCs revoked from `public`, `anon`, `authenticated`, and `service_role`. The S07-003 migration created `storage_cleanup_worker` and granted cleanup RPCs to it, but did NOT grant the role to `postgres` or `authenticator`.
- The runner must execute cleanup RPCs under this narrow role capability, not through `service_role` privilege broadening.
- The runner implementation must explicitly supply the database transport it actually uses:
  1. **PostgREST / Custom-JWT path (Recommended for TypeScript SupabaseClient runner)**:
     All accepted cleanup adapters in `web/src/lib/commands/storage-reservation.ts` take `workerClient: SupabaseClient` and invoke `workerClient.rpc()`. For PostgREST to switch to `storage_cleanup_worker` upon receiving a worker JWT, a narrow forward migration must execute:
     `GRANT storage_cleanup_worker TO authenticator;`
     This enables server-only creation of a worker client using a custom worker JWT signed by a server-controlled signing mechanism accepted by the project's current Supabase JWT configuration (not mandating legacy `SUPABASE_JWT_SECRET`), with short expiry, `role = storage_cleanup_worker`, and separate API key header. This allows existing typed `SupabaseClient` adapters to run natively. The PostgREST bridge must never expose worker credentials to browsers, must never grant cleanup RPCs to `service_role`, and must include role-denial regressions confirming `anon` and `authenticated` cannot assume the worker role.
  2. **Direct connection path (Alternative direct-DB runner adapter)**:
     In local scripts or database integration harnesses, user `postgres` can assume `storage_cleanup_worker` via `SET ROLE storage_cleanup_worker;` by virtue of being a PostgreSQL superuser/admin in local Supabase, NOT because of an explicit predecessor membership. If the runner chooses a direct database connection instead of PostgREST, it must implement an explicit direct-DB runner adapter that executes `SET ROLE storage_cleanup_worker;`, runs cleanup RPCs in independent transactions, and guarantees `RESET ROLE;`. A raw PostgreSQL connection cannot be passed unchanged to `SupabaseClient` adapters.
  - S07-004 requires a focused test proving:
    * Direct local session can assume `storage_cleanup_worker` via `SET ROLE storage_cleanup_worker;` when intended;
    * While operating under `storage_cleanup_worker`, cleanup RPCs succeed;
    * Calling the cleanup RPCs under `anon`, `authenticated`, or `service_role` remains denied;
    * Resetting the role (`RESET ROLE`) returns the session to base privileges and does not leave worker authority accidentally active.
  - Under either chosen transport, the implementation must provide the actual transport used by the runner and test it end-to-end against local Supabase, proving the narrow role capability is truly bound and enforced, not merely tested in a detached harness. Hosted token provisioning for production is deferred to operational deployment readiness; no production secrets are provisioned in S07-004.

### B. Storage-provider capability seam & destructive sequence

Physical deletion of a private object requires a separate Storage provider capability (Storage API / `storage.from(bucket).remove([path])`):
- The runner must strictly decouple **DB cleanup authorization** from the **Storage provider deletion** capability.
- Possessing a Storage admin credential does not confer deletion authority; DB authorization is strictly authoritative.
- The runner executes the exact sequential lifecycle:
  1. **Claim**: Call `claimStorageCleanupJobs(workerId, limit, leaseSeconds, dbClient)`. Retain exact `storage_cleanup_id`, `worker_id`, `attempt_id`, and `fencing_token`.
  2. **Authorize**: Call `authorizeStorageCleanupAttempt({ storageCleanupId, attemptId, fencingToken, workerId }, dbClient)`.
     - **Envelope vs Adapter Contract**: Distinguish the raw SQL RPC return envelope (`{ success: true, data: ... }` / `{ success: false, error_code: ... }`) from the accepted TypeScript adapter contract (`authorizeStorageCleanupAttempt` in `web/src/lib/commands/storage-reservation.ts` returns `Promise<AuthorizedStorageCleanupJob>`, while `runStorageCleanupRpc` throws on RPC errors and on `{ success: false, error_code: ... }`).
     - **Per-Job Exception Handling**: In the TypeScript runner, invoke `authorizeStorageCleanupAttempt` within per-job try/catch exception handling:
       * On success: directly consume the returned `AuthorizedStorageCleanupJob` (extracting `bucket_name`, `object_path`, `attempt_id`, `fencing_token`).
       * On failure / denial: `authorizeStorageCleanupAttempt` throws an Error (e.g. `authorize_storage_cleanup_attempt error: CLEANUP_WITHHELD`, `STALE_ATTEMPT`, `NOT_FOUND`). Catch the error, extract the safe failure code, perform zero Storage provider calls for this job, record the withheld/error outcome, and skip to the next claimed job in the batch.
     - **Batch Regression Requirement**: Require a batch regression test in unit/integration tests with a denied first job and a subsequent eligible job proving the batch continues cleanly without calling the provider on the denied job.
  3. **Physical Provider Delete**: Call `storageProvider.removeObject(authorized.bucket_name, authorized.object_path)` using the exact authorized pair.
  4. **Complete**: Report outcome via `completeStorageCleanupAttempt({ storageCleanupId, attemptId, fencingToken, workerId, success, errorCode }, dbClient)`.
- Prohibitions: No deletion before authorization; no bucket listing; no prefix guessing; no deletion targets derived from arbitrary caller parameters.

### C. Crash windows and idempotency

Handle all failure windows safely:
- **Window 1 (Auth commits, crash before delete)**: Queue remains `PROCESSING` with `tombstoned_at` set. After lease expiry, subsequent claim reclaims the job with a new `attempt_id`/`fencing_token`. Re-authorization succeeds (`tombstone_cleanup_id == p_q.storage_cleanup_id`). New worker deletes object.
- **Window 2 (Delete succeeds, crash before DB complete)**: Object removed from Storage, but queue remains `PROCESSING`. After lease expiry, reclaimed attempt authorizes and calls provider delete. Provider reports the object already absent. Under Section D policy, absent object completes as `success: true`. Queue settles `DONE`.
- **Window 3 (Provider timeout / ambiguous outcome)**: Worker records `PROVIDER_TIMEOUT` or lease expires. Reclaimed attempt re-executes. If object was deleted $\rightarrow$ absent $\rightarrow$ `DONE`. If not deleted $\rightarrow$ provider deletes $\rightarrow$ `DONE`. 5-attempt ceiling prevents infinite loop.
- **Window 4 (Lease expires in flight)**: Old worker attempting completion after lease expiry or reclaim receives `STALE_ATTEMPT`. It cannot overwrite newer attempts.
- **Window 5 (Reclaim during stale execution)**: Stale worker's credentials are invalidated. Reclaim owns the exclusive lease.

### D. Object-not-found / provider absence semantics

When the Storage provider returns a response indicating an exact authorized object `(bucket_name, object_path)` is already absent:
- **Policy**: An already-absent authorized object achieves the desired terminal end-state (object does not exist in Storage).
- **Behavior-Driven Mapping**: The implementation must NOT hardcode an assumption that absence manifests solely as HTTP 404. Local integration tests must inspect the actual local Supabase Storage client `remove()` response for an already-absent object (e.g. empty data array, specific status, or error code) and authoritatively map that absence result to successful cleanup (`success: true`).
- **Strict Error Discrimination**: Permission failures, missing bucket, invalid credentials, malformed requests, network errors, or ambiguous provider responses MUST NOT be collapsed into "object absent". They remain reportable errors.
- **Rationale**: The database authorization step already proved that the object has terminal provenance and zero live/historical business references. An already-absent object cannot harm retention and cannot be resurrected (tombstone remains in provenance). Completing as success allows self-healing after crash-after-delete (Window 2) and idempotent replays without fabricating deletion metrics.

### E. Network/transaction separation

- Storage provider network calls MUST execute strictly outside database transactions.
- Step 2 (`authorize_storage_cleanup_attempt`) commits independently, placing an immutable tombstone in `private.storage_cleanup_provenance` that prevents resurrection while the external call is in flight.
- Step 3 (Storage deletion) runs with zero open database transactions or row locks.
- Step 4 (`complete_storage_cleanup_attempt`) commits independently.

### F. Retention and safety invariants

Retain all S07-003 safeguards:
- Restricted to private managed temp buckets (`candidate-quarantine` and `interview-quarantine`). Both buckets must be explicitly provisioned in the local environment and covered by integration tests.
- Current or historical Candidate document references block cleanup (`RETAINED_REFERENCE`).
- Current or historical Interview document references block cleanup (`RETAINED_REFERENCE`).
- Live reservations block cleanup (`LIVE_RESERVATION`).
- Unelapsed signed windows block cleanup (`SIGNED_WINDOW`).
- Genuinely detached legacy rows without reservation evidence fail closed (`UNKNOWN_PROVENANCE`).
- Tombstoned identities reject resurrection (`STORAGE_CLEANUP_IDENTITY_TOMBSTONED`).

## Local storage integration test requirements

The implementation must verify real physical provider behavior against a disposable local Supabase environment covering both `candidate-quarantine` and `interview-quarantine`:
1. **Candidate-quarantine authorized deletion**: An authorized temp object in `candidate-quarantine` is physically deleted from Storage.
2. **Interview-quarantine authorized deletion**: An authorized temp object in `interview-quarantine` is physically deleted from Storage (ensuring both managed buckets are provisioned and proven).
3. **Neighbor isolation**: A neighboring object in the same bucket/prefix is untouched and remains in Storage.
4. **No-authorization refusal**: A job where authorization was not obtained or was withheld causes zero Storage deletes.
5. **Retained current reference protection**: A reservation whose path is referenced by a current document causes zero Storage deletes.
6. **Retained historical reference protection**: A reservation whose path is referenced by a historical document causes zero Storage deletes.
7. **Stale attempt rejection**: A worker holding an expired lease or stale attempt cannot delete or complete.
8. **Terminal eligible object removal**: An expired/cancelled reservation past its signed window is authorized, deleted from Storage, and completed as `DONE`.
9. **Delete-success crash recovery**: Simulating a crash after provider delete causes subsequent reclaim to complete successfully upon encountering the absent object.
10. **Already-absent idempotency**: An already-absent authorized object completes cleanly as `DONE` under behavior-driven absence mapping.
11. **Provider error / retry**: A temporary provider error records `errorCode`, leaves queue row eligible for retry under the 5-attempt ceiling, and does NOT collapse into success.
12. **Targeted non-sweep execution**: Deletion operates strictly on exact authorized `(bucket, path)` pairs without bucket listing or prefix sweeps.
13. **Local worker capability verification**: Direct local session proves `SET ROLE storage_cleanup_worker` can invoke cleanup RPCs, `RESET ROLE` clears authority, and `anon`/`authenticated`/`service_role` remain denied.

## Expected implementation shape

- `web/src/lib/storage/cleanup-runner.ts`: Server-only runner module implementing single-job execution and bounded batch iteration.
- `web/src/lib/storage/storage-provider.ts`: Storage provider abstraction (with real Supabase Storage implementation and mock implementation for unit tests).
- `web/src/__tests__/storage-cleanup-runner.test.ts`: Unit tests verifying runner state machine, retry policy, error mapping, and crash window handling using mock providers.
- `supabase/tests/storage_cleanup_local_storage_test.sh`: Integration harness executing real physical object creation and deletion against local Supabase Storage containers covering both `candidate-quarantine` and `interview-quarantine`.

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
- Local integration tests: Physical Storage object lifecycle in local Supabase Storage covering both buckets and role assumption (`supabase/tests/storage_cleanup_local_storage_test.sh`).
- Predecessor regressions: S07-003 SQL contract, S07-003 concurrency/fencing, S07-003 upgrade path, S02, S04, S07-002 regressions.
- Web verification: lint, typecheck, build.
- Governance validators: `validate_control_plane.py`, `validate_omp_native.py`.
- Exact-SHA formal CI: fresh Integration CI and Governance CI on integration branch.

## Stop conditions and source reopen

Stop immediately at prompt review PASS. Do not begin implementation. Do not dispatch an executor.

`SOURCE_REOPEN_REQUIRED: false`.
No canonical invariant requires modifying any accepted predecessor. Bounded physical cleanup is a pure downstream consumer of accepted S07-003 trusted contracts.
