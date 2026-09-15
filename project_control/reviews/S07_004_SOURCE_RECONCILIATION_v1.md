# S07-004 source reconciliation — Physical storage cleanup runner and local storage integration

Producer reconciliation, not new product authority or independent review.
Starting reporting SHA: `f536c839e0999e66b498dbfcd40d321539a7b4cd`.
Authoritative accepted predecessor: `TASK-S07-003 — Storage Cleanup Eligibility and Result-Fencing Trusted Contracts` accepted at `checkpoint/S07-003-accepted-001` (`7317138779270087e3e425f48b13785923b17f42`, annotated tag `a2702995bb1b475d003ad8e85d4a2c58b7fcd75c`).
This dispatch authorizes prompt materialization and independent prompt review only. Implementation is NOT started.

## Decision and accepted inputs

Materialize exactly **TASK-S07-004 — Physical Storage Cleanup Runner and Local Storage Integration**.
This task is the direct downstream consumer of the accepted S07-003 database cleanup contracts (discovery, claim, eligibility authorization, fencing token rotation, tombstone tracking, and attempt completion). It implements a bounded, server-only physical deletion runner and proves real Storage deletion against disposable local Supabase storage buckets (`candidate-quarantine`, `interview-quarantine`).

Direct dependencies:
- `TASK-S02-003` (reservation/cleanup protocol) — DONE
- `TASK-S02-004` (staged finalization) — DONE
- `TASK-S04-002` (Interview reservation cleanup) — DONE
- `TASK-S07-002` (scan terminal cleanup producer) — DONE (`checkpoint/S07-002-accepted-001`)
- `TASK-S07-003` (storage cleanup trusted contracts) — DONE (`checkpoint/S07-003-accepted-001`)

No subsequent tasks are materialized; scanner execution, email sender execution, Email History UI, notification management, archive/purge, and production deployment remain separate unmaterialized future branches.

## Canonical authority and current implementation

Current review-pack authority (source_registry v1.18):
- Module 11 §§5–9: Private storage reservation, signed URLs, and cleanup queuing.
- Module 37 §§3, 10, 16: System maintenance, quarantine isolation, and secure disposal.
- Module 41: Two-phase candidate staged / interview hard-delete upload lifecycle.
- Module 42: Business retention policy (retained document rows immutable; physical cleanup restricted to unreferenced temp objects).
- Module 47: Audit logging and minimization of destructive operations.
- Module 48: Concurrency control, deterministic locking, and idempotency.
- Module 39/59: RLS and role-based capability boundaries.
- Module 66: Archive/purge governance (destructive cleanup is not automatic archive).
- Module 73: Canonical predicates and document reference validation.
- App spec: `candidate_form_session`, `upload_reservation`, `interview_upload_cleanup`, `retention`.

Current implementation reality:
- `20260915010000_storage_cleanup_trusted_contracts.sql`: Creates `private.storage_cleanup_provenance`, `public.storage_cleanup_queue` hardening, narrow role `storage_cleanup_worker` (NOLOGIN NOINHERIT), and trusted RPCs (`discover_expired_storage_cleanup`, `claim_storage_cleanup_jobs`, `authorize_storage_cleanup_attempt`, `complete_storage_cleanup_attempt`). All cleanup RPCs are revoked from `public`, `anon`, `authenticated`, and `service_role`.
- `web/src/lib/commands/storage-reservation.ts`: Defines typed client adapters (`discoverExpiredStorageCleanup`, `claimStorageCleanupJobs`, `authorizeStorageCleanupAttempt`, `completeStorageCleanupAttempt`) accepting an explicit `workerClient: SupabaseClient`.
- `web/src/lib/storage/buckets.ts`: Defines managed bucket constants (`candidate-quarantine`, `interview-quarantine`).
- `web/src/lib/supabase/admin.ts`: Creates admin client via `serviceRoleKey`. This client cannot invoke cleanup RPCs directly because execute rights are revoked from `service_role`.

---

## Required architecture questions resolved

### A. Narrow database worker capability

Accepted S07-003 establishes a strictly capability-bounded database security posture:
- `storage_cleanup_worker` role is `NOLOGIN NOINHERIT`.
- Execute rights on all four cleanup RPCs are revoked from `public`, `anon`, `authenticated`, and `service_role`.
- Only `storage_cleanup_worker` possesses `GRANT EXECUTE` on the cleanup RPCs.

**Runtime Binding Mechanism**:
1. **Local integration tests and standalone scripts**:
   PostgreSQL role membership established in S07-003 assigns `storage_cleanup_worker` membership to `postgres` (`storage_cleanup_worker | postgres`). Direct database sessions connecting via `DATABASE_URL` as user `postgres` can invoke the RPCs or execute `SET ROLE storage_cleanup_worker;`.
2. **Server-only PostgREST / SupabaseClient runtime**:
   Supabase PostgREST connects to PostgreSQL as the `authenticator` role. In standard Supabase architecture, PostgREST switches to the role specified in the JWT `role` claim via `SET LOCAL ROLE <role>`. For `authenticator` to switch to `storage_cleanup_worker`, `storage_cleanup_worker` must be granted to `authenticator`:
   `GRANT storage_cleanup_worker TO authenticator;`
   When granted:
   - A server-only client created with a custom JWT signed by `SUPABASE_JWT_SECRET` (which is never exposed to browsers) containing `{ "role": "storage_cleanup_worker" }` allows PostgREST to cleanly assume `storage_cleanup_worker`.
   - Cleanup capabilities remain completely revoked from `service_role`, `authenticated`, and `anon`.
   - No reusable database login password or browser-accessible credential is created.
   - If S07-004 chooses the PostgREST custom JWT path, a small forward migration solely containing `GRANT storage_cleanup_worker TO authenticator;` is authorized to establish this bridge. Alternatively, if a direct database connection pool or internal server gateway is used, direct role assumption is equally valid.
   - Both mechanisms preserve the narrow accepted capability without broadening `service_role` grants.

### B. Storage-provider capability

Physical deletion of private objects from Storage requires a distinct provider capability (Storage Admin API / `storage.from(bucket).remove([path])`):
- The physical runner strictly separates the **DB cleanup authority** seam from the **Storage provider deletion** seam.
- Possessing a Storage service-role key or Admin token does NOT grant authority to delete an object.
- The runner must obtain an explicit, successful `AuthorizedStorageCleanupJob` from `authorize_storage_cleanup_attempt(...)` before issuing any provider delete call.
- The provider client is invoked strictly with the exact `(bucket_name, object_path)` returned in the authorized payload.
- No production Storage credentials are provisioned or needed; local integration tests run against local Supabase Storage.

### C. Exact destructive sequence

The runner must execute the following sequential protocol without deviation:
1. **Discovery (optional / bounded batch)**:
   Invoke `discoverExpiredStorageCleanup(limit, dbClient)` to scan and enqueue known expired reservation intents idempotently.
2. **Claim**:
   Invoke `claimStorageCleanupJobs(workerId, limit, leaseSeconds, dbClient)`.
   Receive `ClaimedStorageCleanupJob[]`. Each claimed item contains `storage_cleanup_id`, `worker_id`, `attempt_id`, and `fencing_token`.
3. **Authorization**:
   For each claimed job, invoke `authorize_storage_cleanup_attempt({ storageCleanupId, attemptId, fencingToken, workerId }, dbClient)`.
   - If authorization returns `{ success: false, error_code: ... }` (e.g. `CLEANUP_WITHHELD`, `STALE_ATTEMPT`, `NOT_FOUND`):
     Record failure/withheld reason; do NOT touch Storage; skip to next job.
   - If authorization returns `{ success: true, data: ... }`:
     Extract the authorized `bucket_name` and `object_path`.
4. **Provider Deletion**:
   Invoke `storageProvider.removeObject(authorized.bucket_name, authorized.object_path)`.
   Run outside of any database transaction.
5. **Completion**:
   - If provider deletion succeeds:
     Invoke `completeStorageCleanupAttempt({ storageCleanupId, attemptId, fencingToken, workerId, success: true, errorCode: null }, dbClient)`.
     Queue row transitions to `DONE`.
   - If provider deletion fails with error:
     Map provider error code (e.g. `PROVIDER_TIMEOUT`, `TEMPORARY_FAILURE`, `PROVIDER_UNAVAILABLE`).
     Invoke `completeStorageCleanupAttempt({ storageCleanupId, attemptId, fencingToken, workerId, success: false, errorCode }, dbClient)`.
     Queue row records error, and retries if under 5 attempts.

**Anti-Patterns Prohibited**:
- Never call provider deletion before authorization succeeds.
- Never sweep an entire bucket or list bucket objects to find delete targets.
- Never guess path prefixes or delete by pattern.
- Never accept delete targets from untrusted user input.

### D. Crash windows and ambiguous provider outcomes

The protocol handles all asynchronous crash and failure windows safely:
- **Window 1 (Auth commits, crash before provider delete)**:
  Queue row remains `PROCESSING` with `authorized_at` and `tombstoned_at` recorded. While `leased_until > clock_timestamp()`, no other worker can touch it. After lease expiry, subsequent claim reclaims the job (rotating `attempt_id` and `fencing_token`). On re-authorization, `storage_cleanup_eligibility` matches `tombstone_cleanup_id == p_q.storage_cleanup_id` and successfully re-authorizes the new attempt. The new worker executes deletion.
- **Window 2 (Provider delete succeeds, crash before DB completion)**:
  The object is deleted from Storage, but DB queue remains `PROCESSING`. After lease expiry, the job is reclaimed by a new attempt. The new attempt authorizes and calls provider delete. Storage returns `OBJECT_NOT_FOUND` (404). Under the resolved 404 policy (Question E), absent object satisfies the cleanup objective; worker reports `success = true`; queue settles `DONE`.
- **Window 3 (Provider request times out / outcome ambiguous)**:
  Worker treats timeout as `PROVIDER_TIMEOUT`. If process is alive, reports `complete_storage_cleanup_attempt(..., success: false, errorCode: 'PROVIDER_TIMEOUT')`. If hung/crashed, lease expires and is reclaimed. If the object was deleted during timeout, next attempt gets 404 $\rightarrow$ `DONE`. If not deleted, next attempt removes it $\rightarrow$ `DONE`. Maximum 5 attempts bound prevents infinite retries.
- **Window 4 (Lease expires while provider request is in flight)**:
  If the old worker attempts to complete after lease expiration or reclaim, `complete_storage_cleanup_attempt` validates current `attempt_id`, `fencing_token`, and unexpired lease. The old worker is rejected with `STALE_ATTEMPT`. It cannot overwrite a newer attempt or alter queue state.
- **Window 5 (Attempt reclaimed while old worker holds stale state)**:
  Reclaim updates `attempt_id` and `fencing_token`. Any subsequent call from the old attempt fails closed with `STALE_ATTEMPT`.

### E. Object-not-found semantics

When the Storage provider returns `OBJECT_NOT_FOUND` / 404 for an exact authorized object `(bucket_name, object_path)`:
- **Policy**: An already-absent object achieves the desired terminal end-state (object does not exist in Storage).
- The worker reports completion as `success: true`.
- **Rationale**: The database authorization step already proved that the object has terminal provenance and zero live/historical business references. An already-absent object cannot harm retention and cannot be resurrected (tombstone remains in provenance). Completing as success allows self-healing after crash-after-delete (Window 2) and idempotent replays.
- The worker logs audit data reflecting that the provider reported absent, without fabricating historical provider deletion metrics.

### F. Network/transaction separation

- Storage provider network calls (`storage.remove(...)`) MUST execute strictly outside database transactions.
- Step 3 (authorization RPC) executes and commits independently, creating an immutable tombstone in `private.storage_cleanup_provenance` that prevents resurrection during the external network window.
- Step 4 (Storage call) takes place with zero open database transactions or connection locks.
- Step 5 (completion RPC) executes and commits in its own independent transaction.

### G. Private object and retention safety

All S07-003 safeguards remain fully operative and non-bypassable:
- Confined to `candidate-quarantine` and `interview-quarantine` private buckets.
- Current or historical Candidate submission document reference denies authorization (`RETAINED_REFERENCE`).
- Current or historical Interview document reference denies authorization (`RETAINED_REFERENCE`).
- Live uncancelled reservation denies authorization (`LIVE_RESERVATION`).
- Unelapsed signed upload bound or `not_before` denies authorization (`SIGNED_WINDOW`).
- Genuinely detached legacy queue rows lacking authoritative reservation evidence deny authorization (`UNKNOWN_PROVENANCE`).
- Tombstoned identities cannot be resurrected by subsequent reservation or document insertion (`STORAGE_CLEANUP_IDENTITY_TOMBSTONED`).

---

## Local storage integration test requirements

The future S07-004 implementation must prove physical behavior against disposable local Supabase Storage buckets, covering at least 12 test cases:
1. **Authorized deletion**: An authorized temp object is physically deleted from the quarantine bucket.
2. **Neighbor isolation**: A neighboring object in the same bucket/prefix is not deleted and remains intact.
3. **No-authorization refusal**: A job where authorization was not obtained or was withheld causes zero Storage deletes.
4. **Retained current reference protection**: A reservation whose path is referenced by a current document causes zero Storage deletes.
5. **Retained historical reference protection**: A reservation whose path is referenced by a historical document causes zero Storage deletes.
6. **Stale attempt rejection**: A worker holding an expired lease or stale attempt cannot delete or complete.
7. **Terminal eligible object removal**: An expired/cancelled reservation past its signed window is authorized, deleted from Storage, and completed as `DONE`.
8. **Delete-success crash recovery**: Simulating a crash after provider delete causes subsequent reclaim to complete successfully upon encountering 404.
9. **Already-absent idempotency**: An already-absent authorized object (404) completes cleanly as `DONE`.
10. **Provider error / retry**: A temporary provider error records `errorCode`, leaves queue row eligible for retry under the 5-attempt ceiling.
11. **Stale completion fence**: A reclaimed job rejects completion from the old worker attempt.
12. **Targeted non-sweep execution**: Deletion operates strictly on exact authorized `(bucket, path)` pairs without bucket listing or prefix sweeps.

---

## Expected implementation shape

- `web/src/lib/storage/cleanup-runner.ts`: Server-only runner module implementing single-job execution and bounded batch iteration.
- `web/src/lib/storage/storage-provider.ts`: Storage provider abstraction (with real Supabase Storage implementation and mock implementation for unit tests).
- `web/src/__tests__/storage-cleanup-runner.test.ts`: Unit tests verifying runner state machine, retry policy, error mapping, and crash window handling using mock providers.
- `supabase/tests/storage_cleanup_local_storage_test.sh`: Integration harness executing real physical object creation and deletion against local Supabase Storage containers.

---

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

---

## Preservation, verification and source reopen

Accepted predecessors `TASK-S07-001`, `TASK-S07-002`, and `TASK-S07-003` remain fully intact at their immutable checkpoints.
- Clean zero-state migration replay must continue to pass.
- S07-003 SQL contract, concurrency/fencing, and upgrade-path tests must continue to pass.
- Web unit tests must pass.
- Governance validators must pass.

`SOURCE_REOPEN_REQUIRED: false`.
No canonical invariant requires modifying any accepted predecessor. Bounded physical cleanup is a pure downstream consumer of accepted S07-003 trusted contracts.
